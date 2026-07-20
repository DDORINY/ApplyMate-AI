from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class DemoJob:
    company: str
    title: str
    skills: tuple[str, ...]
    deadline: str


def build_demo_payload(email: str) -> dict:
    jobs = [
        DemoJob("ApplyWorks", "Junior Backend Engineer", ("Python", "FastAPI", "PostgreSQL"), "2026-08-31"),
        DemoJob("CareerFlow", "Frontend Developer", ("TypeScript", "React", "Next.js"), "2026-09-05"),
        DemoJob("DataNest", "AI Application Engineer", ("Python", "LLM", "Docker"), "2026-09-12"),
        DemoJob("CloudBridge", "Platform Engineer", ("Docker", "Redis", "PostgreSQL"), "2026-09-20"),
        DemoJob("PeopleOps Lab", "Product Engineer", ("FastAPI", "React", "SQLAlchemy"), "2026-09-30"),
    ]
    return {
        "user": {"email": email, "name": "ApplyMate Demo User"},
        "profile": {
            "desired_roles": ["Backend Engineer", "AI Application Engineer"],
            "career_level": "JUNIOR",
            "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "TypeScript", "React"],
            "projects": [
                {
                    "name": "AI 취업 매니저",
                    "summary": "채용공고 분석, 추천, 지원 문서 생성을 연결한 MVP 프로젝트",
                }
            ],
        },
        "jobs": [asdict(job) for job in jobs],
        "applications": [
            {"company": "ApplyWorks", "status": "PREPARING"},
            {"company": "CareerFlow", "status": "APPLIED"},
        ],
        "schedules": [
            {"title": "ApplyWorks 서류 마감", "event_type": "APPLICATION_DEADLINE"},
            {"title": "CareerFlow 면접 준비", "event_type": "INTERVIEW"},
        ],
        "notifications": [
            {"event_type": "SCHEDULE_REMINDER", "title": "오늘 확인할 지원 일정이 있습니다."}
        ],
    }
