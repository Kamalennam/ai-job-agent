"""Deterministic resume-to-job scoring. No LLM calls."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.services.jobs.skill_normalizer import (
    canonical_display,
    find_skills,
    normalize_skill,
    skill_satisfied,
)

SCORER_VERSION = "deterministic-v1"

ROLE_PHRASES: dict[str, tuple[str, ...]] = {
    "backend": ("back-end", "back end", "backend"),
    "frontend": ("front-end", "front end", "frontend"),
    "fullstack": ("full-stack", "full stack", "fullstack"),
    "ai": ("machine learning", "ml engineer", "ai engineer", "llm", "rag", "nlp"),
    "data": ("data engineer", "data scientist", "data analyst"),
    "devops": ("devops", "site reliability", "sre"),
    "mobile": ("ios", "android", "mobile engineer", "mobile developer"),
}

_TITLE_STOPWORDS = {
    "senior",
    "junior",
    "staff",
    "principal",
    "lead",
    "engineer",
    "developer",
    "software",
    "the",
    "a",
    "an",
    "and",
    "of",
    "for",
    "with",
    "in",
    "to",
    "sr",
    "jr",
    "ii",
    "iii",
    "level",
}

_SECTION_RE = re.compile(
    r"\b("
    r"preferred qualifications|minimum qualifications|nice to have|nice-to-have|"
    r"good to have|required skills|must have|what you'll need|what you'll bring|"
    r"what you will bring|requirements|qualifications|preferred|bonus|benefits|"
    r"about us|who we are|equal opportunity"
    r")\b",
    re.IGNORECASE,
)
_PREFERRED_LABELS = {
    "preferred qualifications",
    "nice to have",
    "nice-to-have",
    "good to have",
    "preferred",
    "bonus",
}
_REQUIRED_LABELS = {
    "minimum qualifications",
    "required skills",
    "must have",
    "what you'll need",
    "what you'll bring",
    "what you will bring",
    "requirements",
    "qualifications",
}
_YEAR_RANGE_RE = re.compile(
    r"(\d+)\s*(?:-|–|to)\s*(\d+)\s*(?:years|yrs)\b",
    re.IGNORECASE,
)
_YEAR_RE = re.compile(r"(\d+)\s*(?:\+|plus)?\s*(?:years|yrs)\b", re.IGNORECASE)
_YEAR_TOKEN_RE = re.compile(r"(19|20)\d{2}")


@dataclass(frozen=True)
class MatchWeights:
    skill: float = 0.50
    role: float = 0.20
    experience: float = 0.15
    project: float = 0.10
    other: float = 0.05


@dataclass
class ExperienceInput:
    title: str
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None
    company: str | None = None


@dataclass
class ProjectInput:
    name: str
    technologies: list[str] = field(default_factory=list)
    description: str | None = None


@dataclass
class EducationInput:
    institution: str | None = None
    degree: str | None = None
    field: str | None = None


@dataclass
class ParsedResumeInput:
    skills: list[str] = field(default_factory=list)
    experience: list[ExperienceInput] = field(default_factory=list)
    projects: list[ProjectInput] = field(default_factory=list)
    education: list[EducationInput] = field(default_factory=list)
    summary: str | None = None
    raw_text: str | None = None


@dataclass
class JobInput:
    job_id: str
    title: str
    description: str
    url: str
    company: str
    location: str | None = None
    department: str | None = None
    employment_type: str | None = None
    requirements: str | None = None
    remote: bool | None = None
    posted_at: datetime | None = None


@dataclass
class CandidateProfile:
    skills: set[str]
    skill_order: list[str]
    skill_labels: dict[str, str]
    titles: list[str]
    role_families: set[str]
    project_technologies: list[str]
    project_labels: dict[str, str]
    experience_years: float | None
    has_experience: bool
    education_text: str
    summary: str


@dataclass
class NormalizedJob:
    job_id: str
    title: str
    description: str
    location: str | None
    url: str
    company: str
    department: str | None
    employment_type: str | None
    remote: bool | None
    posted_at: datetime | None
    required_skills: list[str]
    preferred_skills: list[str]
    mentioned_skills: list[str]
    experience_requirements: list[str]
    min_years: float | None
    role_families: set[str]


@dataclass
class ScoredMatch:
    job_id: str
    title: str
    company: str
    location: str | None
    remote: bool | None
    posted_at: datetime | None
    url: str
    match_score: int
    matched_skills: list[str]
    missing_skills: list[str]
    matched_role: bool
    experience_match: bool
    project_matches: list[str]
    match_reasons: list[str]
    skill_score: float
    role_score: float
    experience_score: float
    project_score: float
    other_score: float


def _add_skill(
    canonical: str,
    label: str,
    ordered: list[str],
    labels: dict[str, str],
) -> None:
    if not canonical or canonical in labels:
        return
    labels[canonical] = label
    ordered.append(canonical)


def _absorb_listed_skill(
    raw: str,
    ordered: list[str],
    labels: dict[str, str],
) -> str | None:
    single = normalize_skill(raw)
    found = find_skills(raw, {single} if single else None)
    if single and single not in found:
        found = [single, *found]
    for canonical in found:
        if len(found) == 1 and raw.strip():
            label = raw.strip()
        else:
            label = canonical_display(canonical)
        _add_skill(canonical, label, ordered, labels)
    return single


def _parse_year_month(value: str | None) -> tuple[int, int] | None:
    if not value or not str(value).strip():
        return None
    text = str(value).strip().lower()
    if text in {"present", "current", "now"}:
        today = datetime.now(UTC)
        return today.year, today.month
    year_match = _YEAR_TOKEN_RE.search(text)
    if not year_match:
        return None
    year = int(year_match.group(0))
    remainder = text.replace(year_match.group(0), " ", 1)
    month_match = re.search(r"(?<!\d)(0?[1-9]|1[0-2])(?!\d)", remainder)
    month = int(month_match.group(1)) if month_match else 1
    return year, month


def estimate_experience_years(experience: list[ExperienceInput]) -> float | None:
    """Sum role durations. Overlapping roles are not de-duplicated."""
    total_months = 0
    counted = False
    for role in experience:
        start = _parse_year_month(role.start_date)
        if start is None:
            continue
        end = _parse_year_month(role.end_date)
        if end is None:
            today = datetime.now(UTC)
            end = (today.year, today.month)
        months = (end[0] - start[0]) * 12 + (end[1] - start[1])
        if months < 0:
            continue
        total_months += months
        counted = True
    if not counted:
        return None
    return total_months / 12


def detect_roles(text: str) -> set[str]:
    if not text:
        return set()
    lowered = text.lower()
    found: set[str] = set()
    for family, phrases in ROLE_PHRASES.items():
        for phrase in phrases:
            pattern = rf"(?<![a-z0-9]){re.escape(phrase)}(?![a-z0-9])"
            if re.search(pattern, lowered):
                found.add(family)
                break
    return found


def _significant_tokens(text: str) -> set[str]:
    tokens = re.findall(r"[a-z0-9+#]+", text.lower())
    return {token for token in tokens if token not in _TITLE_STOPWORDS and len(token) > 2}


def split_requirement_sections(text: str) -> tuple[str, str]:
    """Split a job description into required and preferred bodies.

    Greenhouse HTML is stored as flattened text, so headings are detected
    inside the paragraph rather than on their own lines.
    """
    matches = list(_SECTION_RE.finditer(text))
    if not matches:
        return text, ""

    required_parts: list[str] = []
    preferred_parts: list[str] = []
    for index, match in enumerate(matches):
        label = match.group(1).lower()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.end() : end]
        if label in _PREFERRED_LABELS:
            preferred_parts.append(body)
        elif label in _REQUIRED_LABELS:
            required_parts.append(body)
    if not required_parts and not preferred_parts:
        return text, ""
    return "\n".join(required_parts), "\n".join(preferred_parts)


def extract_year_requirements(text: str) -> tuple[float | None, list[str]]:
    found: list[int] = []

    def _capture_range(match: re.Match[str]) -> str:
        low = int(match.group(1))
        if 1 <= low <= 20:
            found.append(low)
        return " "

    scrubbed = _YEAR_RANGE_RE.sub(_capture_range, text)
    for match in _YEAR_RE.finditer(scrubbed):
        value = int(match.group(1))
        if 1 <= value <= 20:
            found.append(value)
    if not found:
        return None, []
    phrases = [f"{year}+ years" for year in sorted(set(found))]
    return float(max(found)), phrases


def build_candidate_profile(parsed: ParsedResumeInput) -> CandidateProfile:
    ordered: list[str] = []
    labels: dict[str, str] = {}
    for raw in parsed.skills:
        _absorb_listed_skill(raw, ordered, labels)

    titles = [role.title.strip() for role in parsed.experience if role.title and role.title.strip()]
    text_blobs = [parsed.summary or "", parsed.raw_text or ""]
    for role in parsed.experience:
        text_blobs.append(role.title or "")
        text_blobs.append(role.description or "")

    project_techs: list[str] = []
    project_labels: dict[str, str] = {}
    for project in parsed.projects:
        text_blobs.append(project.name or "")
        text_blobs.append(project.description or "")
        for raw in project.technologies:
            canonical = _absorb_listed_skill(raw, ordered, labels)
            if canonical and canonical not in project_labels:
                project_labels[canonical] = labels.get(canonical, canonical_display(canonical))
                project_techs.append(canonical)

    education_bits: list[str] = []
    for item in parsed.education:
        education_bits.extend(
            bit for bit in (item.institution, item.degree, item.field) if bit
        )
    education_text = " ".join(education_bits)
    text_blobs.append(education_text)

    extras = set(ordered)
    for blob in text_blobs:
        for canonical in find_skills(blob, extras):
            _add_skill(canonical, canonical_display(canonical), ordered, labels)

    role_source = " ".join([*titles, parsed.summary or "", parsed.raw_text or ""])
    return CandidateProfile(
        skills=set(ordered),
        skill_order=ordered,
        skill_labels=labels,
        titles=titles,
        role_families=detect_roles(role_source),
        project_technologies=project_techs,
        project_labels=project_labels,
        experience_years=estimate_experience_years(parsed.experience),
        has_experience=bool(parsed.experience),
        education_text=education_text,
        summary=parsed.summary or "",
    )


def normalize_job(job: JobInput, extra_skills: set[str] | None = None) -> NormalizedJob:
    full_text = "\n".join(
        part for part in (job.title, job.requirements, job.description) if part
    )
    required_body, preferred_body = split_requirement_sections(full_text)
    if required_body or preferred_body:
        required_text = f"{job.title}\n{required_body}"
        preferred_text = preferred_body
    else:
        required_text = full_text
        preferred_text = ""

    required = find_skills(required_text, extra_skills)
    preferred = [
        skill for skill in find_skills(preferred_text, extra_skills) if skill not in required
    ]
    mentioned = find_skills(full_text, extra_skills)
    min_years, year_phrases = extract_year_requirements(full_text)
    role_source = " ".join(part for part in (job.title, job.department) if part)
    families = detect_roles(role_source) or detect_roles(full_text[:500])
    return NormalizedJob(
        job_id=job.job_id,
        title=job.title,
        description=job.description,
        location=job.location,
        url=job.url,
        company=job.company,
        department=job.department,
        employment_type=job.employment_type,
        remote=job.remote,
        posted_at=job.posted_at,
        required_skills=required,
        preferred_skills=preferred,
        mentioned_skills=mentioned,
        experience_requirements=year_phrases,
        min_years=min_years,
        role_families=families,
    )


def _skill_label(canonical: str, labels: dict[str, str]) -> str:
    return labels.get(canonical) or canonical_display(canonical)


def _score_skills(
    profile: CandidateProfile,
    job: NormalizedJob,
) -> tuple[float, list[str], list[str]]:
    required = job.required_skills
    preferred = job.preferred_skills
    matched_required = [skill for skill in required if skill_satisfied(skill, profile.skills)]
    matched_preferred = [skill for skill in preferred if skill_satisfied(skill, profile.skills)]
    missing = [
        canonical_display(skill)
        for skill in [*required, *preferred]
        if not skill_satisfied(skill, profile.skills)
    ]
    matched_canonicals = [*matched_required, *matched_preferred]
    matched = [_skill_label(skill, profile.skill_labels) for skill in matched_canonicals]

    if required:
        coverage = len(matched_required) / len(required)
        bonus = 0.0
        if preferred:
            bonus = 0.15 * (len(matched_preferred) / len(preferred))
        skill_score = min(100.0, (coverage + bonus) * 100)
    elif preferred:
        skill_score = 100.0 * len(matched_preferred) / len(preferred)
    else:
        skill_score = 0.0
    return skill_score, matched, missing


def _score_role(profile: CandidateProfile, job: NormalizedJob) -> tuple[float, bool]:
    job_roles = job.role_families
    candidate_roles = profile.role_families
    if job_roles and candidate_roles:
        if job_roles & candidate_roles:
            return 100.0, True
        fullstack_pair = (
            "fullstack" in candidate_roles and job_roles & {"backend", "frontend"}
        ) or ("fullstack" in job_roles and candidate_roles & {"backend", "frontend", "fullstack"})
        if fullstack_pair:
            return 85.0, True
        return 0.0, False

    title_overlap = _significant_tokens(job.title) & {
        token for title in profile.titles for token in _significant_tokens(title)
    }
    summary_overlap = _significant_tokens(job.title) & _significant_tokens(profile.summary)
    if title_overlap or summary_overlap:
        return 75.0, True
    return 0.0, False


def _score_experience(
    profile: CandidateProfile,
    job: NormalizedJob,
) -> tuple[float, bool]:
    if job.min_years is None:
        if profile.has_experience:
            return 80.0, True
        return 20.0, False
    years = profile.experience_years
    if years is None:
        return 25.0, False
    if years + 0.25 >= job.min_years:
        return 100.0, True
    if years >= job.min_years * 0.6:
        return 55.0, False
    return 15.0, False


def _score_projects(
    profile: CandidateProfile,
    job: NormalizedJob,
) -> tuple[float, list[str]]:
    if not profile.project_technologies:
        return 0.0, []
    mentioned = set(job.mentioned_skills) | set(job.required_skills) | set(job.preferred_skills)
    hits = [
        tech
        for tech in profile.project_technologies
        if tech in mentioned or skill_satisfied(tech, mentioned)
    ]
    displays = [_skill_label(tech, profile.project_labels) for tech in hits]
    if len(hits) >= 2:
        return 100.0, displays
    if hits:
        return 60.0, displays
    return 0.0, []


def _score_other(profile: CandidateProfile, job: NormalizedJob) -> float:
    points = 0.0
    if _significant_tokens(job.title) & _significant_tokens(profile.summary):
        points += 50
    education = profile.education_text.lower()
    description = job.description.lower()
    for field_name in ("computer science", "software engineering", "information technology"):
        if field_name in education and field_name in description:
            points += 50
            break
    if job.department and detect_roles(job.department) & profile.role_families:
        points += 25
    return min(100.0, points)


def _reasons(
    job: NormalizedJob,
    *,
    matched_skills: list[str],
    matched_required_ratio: float,
    matched_role: bool,
    experience_match: bool,
    project_matches: list[str],
    profile: CandidateProfile,
) -> list[str]:
    reasons: list[str] = []
    if matched_skills:
        shown = ", ".join(matched_skills[:4])
        if matched_required_ratio >= 0.6:
            reasons.append(f"Strong skill overlap on {shown}")
        else:
            reasons.append(f"Partial skill overlap on {shown}")
    if matched_role:
        shared = sorted(job.role_families & profile.role_families)
        if not shared and "fullstack" in profile.role_families:
            shared = sorted(job.role_families)
        if shared:
            reasons.append(f"{shared[0].title()} role matches candidate experience")
        else:
            reasons.append(f"{job.title} matches candidate experience")
    if project_matches:
        reasons.append(f"{', '.join(project_matches[:3])} project experience is relevant")
    if job.min_years is not None:
        years_label = int(job.min_years) if job.min_years.is_integer() else job.min_years
        if experience_match:
            reasons.append(f"Experience meets the {years_label}+ year requirement")
        else:
            reasons.append(f"Experience is below the {years_label}+ year requirement")
    return reasons[:4]


def score_job(
    profile: CandidateProfile,
    job: JobInput,
    weights: MatchWeights | None = None,
) -> ScoredMatch:
    weights = weights or MatchWeights()
    normalized = normalize_job(job, extra_skills=set(profile.skill_order))
    skill_score, matched_skills, missing_skills = _score_skills(profile, normalized)
    role_score, matched_role = _score_role(profile, normalized)
    experience_score, experience_match = _score_experience(profile, normalized)
    project_score, project_matches = _score_projects(profile, normalized)
    other_score = _score_other(profile, normalized)

    raw = (
        skill_score * weights.skill
        + role_score * weights.role
        + experience_score * weights.experience
        + project_score * weights.project
        + other_score * weights.other
    )
    required_hits = [
        skill for skill in normalized.required_skills if skill_satisfied(skill, profile.skills)
    ]
    ratio = (
        len(required_hits) / len(normalized.required_skills) if normalized.required_skills else 0.0
    )
    return ScoredMatch(
        job_id=normalized.job_id,
        title=normalized.title,
        company=normalized.company,
        location=normalized.location,
        remote=normalized.remote,
        posted_at=normalized.posted_at,
        url=normalized.url,
        match_score=int(round(raw)),
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        matched_role=matched_role,
        experience_match=experience_match,
        project_matches=project_matches,
        match_reasons=_reasons(
            normalized,
            matched_skills=matched_skills,
            matched_required_ratio=ratio,
            matched_role=matched_role,
            experience_match=experience_match,
            project_matches=project_matches,
            profile=profile,
        ),
        skill_score=skill_score,
        role_score=role_score,
        experience_score=experience_score,
        project_score=project_score,
        other_score=other_score,
    )


def rank_jobs(
    profile: CandidateProfile,
    jobs: list[JobInput],
    *,
    min_score: int,
    weights: MatchWeights | None = None,
) -> tuple[list[ScoredMatch], int]:
    scored = [score_job(profile, job, weights) for job in jobs]
    matched = [item for item in scored if item.match_score >= min_score]
    matched.sort(key=lambda item: (-item.match_score, item.title.lower(), item.job_id))
    return matched, len(jobs)
