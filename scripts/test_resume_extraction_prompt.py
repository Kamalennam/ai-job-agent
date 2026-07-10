#!/usr/bin/env python3
"""
Test resume extraction prompt against Ollama BEFORE using it in the app pipeline.

Usage (from repo root):
  python scripts/test_resume_extraction_prompt.py
  python scripts/test_resume_extraction_prompt.py --file path/to/resume.txt

Requires:
  - Ollama running (docker compose up ollama)
  - Model pulled: docker compose exec ollama ollama pull llama3.2
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

SAMPLE_RESUME = """
Jane Developer
jane@example.com | +1 555 123 4567 | San Francisco, CA

SUMMARY
Backend engineer with 5 years building Python APIs and data pipelines.

SKILLS
Python, FastAPI, MongoDB, Redis, Celery, React, Docker, AWS

EXPERIENCE
Senior Software Engineer | Acme Corp | Jan 2021 - Present
- Built job ingestion microservices with FastAPI and MongoDB
- Reduced API latency by 40% through caching and query optimization

Software Engineer | Startup Labs | Jun 2018 - Dec 2020
- Developed REST APIs and background workers for analytics platform

PROJECTS
AI Job Agent | Personal Project | 2024
- Automated resume parsing and job matching pipeline using Ollama and FastAPI
- Technologies: Python, React, MongoDB, Docker

Open Metrics Dashboard | Open Source | 2023
- Grafana-style metrics dashboard for small teams
- Technologies: Go, PostgreSQL

EDUCATION
B.S. Computer Science | State University | 2014 - 2018
"""


async def run_test(resume_text: str) -> None:
    from app.ai.resume_extraction.extract import extract_structured_resume

    print("Calling Ollama with resume_extraction prompt...\n")
    result = await extract_structured_resume(resume_text)
    print(result.model_dump_json(indent=2))
    print("\nValidation summary:")
    print(f"  Skills:     {len(result.skills)}")
    print(f"  Experience: {len(result.experience)}")
    print(f"  Projects:   {len(result.projects)}")
    print(f"  Education:  {len(result.education)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Test resume extraction prompt with Ollama")
    parser.add_argument("--file", type=Path, help="Path to plain-text resume content")
    args = parser.parse_args()

    if args.file:
        resume_text = args.file.read_text(encoding="utf-8")
    else:
        resume_text = SAMPLE_RESUME

    asyncio.run(run_test(resume_text))


if __name__ == "__main__":
    main()
