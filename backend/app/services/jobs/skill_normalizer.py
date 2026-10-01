"""Normalize skill names and find them in text without substring false positives."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache

# Canonical skill → display label. This is a seed catalog, not a complete taxonomy.
SEED_SKILLS: dict[str, str] = {
    "python": "Python",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "java": "Java",
    "kotlin": "Kotlin",
    "go": "Go",
    "rust": "Rust",
    "ruby": "Ruby",
    "php": "PHP",
    "c++": "C++",
    "c#": "C#",
    "swift": "Swift",
    "scala": "Scala",
    "sql": "SQL",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "react": "React",
    "react native": "React Native",
    "angular": "Angular",
    "vue": "Vue",
    "next.js": "Next.js",
    "node.js": "Node.js",
    "express": "Express",
    "spring": "Spring",
    "html": "HTML",
    "css": "CSS",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "elasticsearch": "Elasticsearch",
    "spark": "Spark",
    "kafka": "Kafka",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "aws": "AWS",
    "gcp": "GCP",
    "azure": "Azure",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "terraform": "Terraform",
    "linux": "Linux",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "scikit-learn": "scikit-learn",
    "langchain": "LangChain",
    "rag": "RAG",
    "llm": "LLM",
    "openai": "OpenAI",
    "huggingface": "Hugging Face",
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "nlp": "NLP",
    "graphql": "GraphQL",
    "grpc": "gRPC",
    "celery": "Celery",
    "rabbitmq": "RabbitMQ",
    "airflow": "Airflow",
    "jenkins": "Jenkins",
    "github actions": "GitHub Actions",
    "ci/cd": "CI/CD",
    "uikit": "UIKit",
    "objective-c": "Objective-C",
    "git": "Git",
}

# Surface form → canonical. Longer aliases are matched before shorter skills.
ALIASES: dict[str, str] = {
    "react.js": "react",
    "reactjs": "react",
    "react js": "react",
    "react-native": "react native",
    "reactnative": "react native",
    "vue.js": "vue",
    "vuejs": "vue",
    "vue js": "vue",
    "angular.js": "angular",
    "angularjs": "angular",
    "nextjs": "next.js",
    "next js": "next.js",
    "nodejs": "node.js",
    "node js": "node.js",
    "node.js": "node.js",
    "express.js": "express",
    "expressjs": "express",
    "fast api": "fastapi",
    "fast-api": "fastapi",
    "postgres": "postgresql",
    "postgre sql": "postgresql",
    "mongo": "mongodb",
    "mongo db": "mongodb",
    "k8s": "kubernetes",
    "amazon web services": "aws",
    "aws ec2": "aws",
    "aws s3": "aws",
    "aws lambda": "aws",
    "amazon ec2": "aws",
    "amazon s3": "aws",
    "ec2": "aws",
    "s3": "aws",
    "golang": "go",
    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "hugging face": "huggingface",
    "objective c": "objective-c",
    "c sharp": "c#",
    "csharp": "c#",
    "cpp": "c++",
    "ci cd": "ci/cd",
    "cicd": "ci/cd",
    "js": "javascript",
    "ml": "machine learning",
}

# Child skill → parent. Either side satisfies the other during comparison.
RELATED_SKILLS: dict[str, str] = {
    "react native": "react",
}

# Bare tokens that are normal English words. Scanned only when the candidate lists them,
# except longer aliases such as "golang" which stay in the default scan.
AMBIGUOUS_SURFACES = {"go", "r"}

_SEPARATOR = r"[\s._/+#-]*"
_TOKEN_RE = re.compile(r"[a-z0-9+#]+")
_CLEAN_RE = re.compile(r"[^\w\s.+#/+-]+", re.UNICODE)
_SPACE_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class SkillPattern:
    canonical: str
    surface: str
    regex: re.Pattern[str]


def _compile_surface(surface: str) -> re.Pattern[str]:
    tokens = _TOKEN_RE.findall(surface.lower())
    if not tokens:
        tokens = [re.escape(surface.lower())]
    body = _SEPARATOR.join(re.escape(token) for token in tokens)
    return re.compile(body, re.IGNORECASE)


def _iter_surfaces() -> list[tuple[str, str]]:
    surfaces: list[tuple[str, str]] = []
    seen: set[str] = set()
    for surface, canonical in ALIASES.items():
        if surface in AMBIGUOUS_SURFACES or surface in seen:
            continue
        seen.add(surface)
        surfaces.append((surface, canonical))
    for canonical in SEED_SKILLS:
        if canonical in AMBIGUOUS_SURFACES or canonical in seen:
            continue
        seen.add(canonical)
        surfaces.append((canonical, canonical))
    return surfaces


def _build_default_patterns() -> tuple[SkillPattern, ...]:
    patterns = [
        SkillPattern(canonical=canonical, surface=surface, regex=_compile_surface(surface))
        for surface, canonical in _iter_surfaces()
    ]
    patterns.sort(key=lambda item: len(item.surface), reverse=True)
    return tuple(patterns)


_PATTERNS = _build_default_patterns()
_INDEXED_CANONICALS = {pattern.canonical for pattern in _PATTERNS}


def canonical_display(canonical: str) -> str:
    if canonical in SEED_SKILLS:
        return SEED_SKILLS[canonical]
    if canonical in {"node.js", "next.js", "ci/cd", "c++", "c#"}:
        return canonical
    return canonical.title()


def normalize_skill(value: str) -> str | None:
    """Map a listed skill to its canonical form. Unknown skills stay as cleaned text."""
    cleaned = value.lower().strip()
    cleaned = cleaned.replace("&", " and ")
    cleaned = _CLEAN_RE.sub(" ", cleaned)
    cleaned = _SPACE_RE.sub(" ", cleaned).strip(" .")
    if len(cleaned) < 2:
        return None
    if cleaned in ALIASES:
        return ALIASES[cleaned]
    compact = cleaned.replace(".", "").replace(" ", "").replace("-", "")
    if compact in ALIASES:
        return ALIASES[compact]
    if cleaned in SEED_SKILLS:
        return cleaned
    return cleaned


def skill_satisfied(job_skill: str, candidate_skills: set[str]) -> bool:
    if job_skill in candidate_skills:
        return True
    parent = RELATED_SKILLS.get(job_skill)
    if parent and parent in candidate_skills:
        return True
    for owned in candidate_skills:
        if RELATED_SKILLS.get(owned) == job_skill:
            return True
    return False


def _has_boundary(text: str, start: int, end: int) -> bool:
    if start > 0 and text[start - 1].isalnum():
        return False
    if end < len(text) and text[end].isalnum():
        return False
    return True


@lru_cache(maxsize=256)
def _extra_patterns(canonicals: tuple[str, ...]) -> tuple[SkillPattern, ...]:
    patterns: list[SkillPattern] = []
    for canonical in canonicals:
        if canonical in _INDEXED_CANONICALS and canonical not in AMBIGUOUS_SURFACES:
            continue
        surface = canonical.lower()
        if surface in AMBIGUOUS_SURFACES and surface == "go":
            regex = re.compile(
                r"\bgo(?:lang)?\b(?!\s+(?:to|into|for|back|out|through|ahead|home|well)\b)",
                re.IGNORECASE,
            )
            patterns.append(SkillPattern(canonical="go", surface="go", regex=regex))
            continue
        patterns.append(
            SkillPattern(canonical=canonical, surface=surface, regex=_compile_surface(surface))
        )
    return tuple(patterns)


def find_skills(text: str, extra: set[str] | None = None) -> list[str]:
    """Return canonical skills in order of appearance.

    Longer phrases win over shorter ones that sit inside them, so "javascript"
    does not also count as "java", and "AWS EC2" counts as AWS once.
    """
    if not text or not text.strip():
        return []

    patterns = _PATTERNS
    if extra:
        custom = tuple(sorted(skill for skill in extra if skill))
        if custom:
            patterns = patterns + _extra_patterns(custom)

    candidates: list[tuple[int, int, str]] = []
    for pattern in patterns:
        for match in pattern.regex.finditer(text):
            start, end = match.start(), match.end()
            if end <= start or not _has_boundary(text, start, end):
                continue
            candidates.append((start, end, pattern.canonical))

    candidates.sort(key=lambda item: (item[0], -(item[1] - item[0])))
    occupied = bytearray(len(text))
    found: list[str] = []
    seen: set[str] = set()
    for start, end, canonical in candidates:
        if any(occupied[start:end]):
            continue
        for index in range(start, end):
            occupied[index] = 1
        if canonical not in seen:
            seen.add(canonical)
            found.append(canonical)
    return found
