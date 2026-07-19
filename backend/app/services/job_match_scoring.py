import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

from app.models.career import (
    CareerProfile,
    ExcludedCondition,
    ExcludedConditionType,
    Experience,
    JobPreference,
    Project,
    UserSkill,
)
from app.models.job import (
    JobAnalysis,
    JobMatchGrade,
    JobMatchRecommendationStatus,
    JobPosting,
)

CALCULATION_VERSION = "v1"
WEIGHTS = {
    "role": 0.25,
    "skill": 0.30,
    "experience": 0.15,
    "project": 0.15,
    "preference": 0.10,
    "risk": 0.05,
}

ALIASES = {
    "js": "javascript",
    "ts": "typescript",
    "postgres": "postgresql",
    "fast api": "fastapi",
    "next": "next.js",
    "react.js": "react",
}


@dataclass
class ProfileSnapshot:
    profile: CareerProfile
    skills: list[UserSkill]
    experiences: list[Experience]
    projects: list[Project]
    preferences: JobPreference | None
    exclusions: list[ExcludedCondition]


@dataclass
class MatchCalculation:
    total_score: int
    grade: JobMatchGrade
    recommendation_status: JobMatchRecommendationStatus
    role_score: int
    skill_score: int
    experience_score: int
    project_score: int
    preference_score: int
    risk_score: int
    matched_skills: list[dict[str, Any]] = field(default_factory=list)
    missing_skills: list[dict[str, Any]] = field(default_factory=list)
    matched_projects: list[dict[str, Any]] = field(default_factory=list)
    strengths: list[dict[str, Any]] = field(default_factory=list)
    gaps: list[dict[str, Any]] = field(default_factory=list)
    risks: list[dict[str, Any]] = field(default_factory=list)
    recommendation_summary: str = ""
    profile_completeness: int = 0

    def snapshot(self) -> dict[str, Any]:
        return {
            "total_score": self.total_score,
            "grade": self.grade.value,
            "recommendation_status": self.recommendation_status.value,
            "scores": {
                "role": self.role_score,
                "skill": self.skill_score,
                "experience": self.experience_score,
                "project": self.project_score,
                "preference": self.preference_score,
                "risk": self.risk_score,
            },
            "matched_skills": self.matched_skills,
            "missing_skills": self.missing_skills,
            "matched_projects": self.matched_projects,
            "strengths": self.strengths,
            "gaps": self.gaps,
            "risks": self.risks,
            "recommendation_summary": self.recommendation_summary,
            "profile_completeness": self.profile_completeness,
            "calculation_version": CALCULATION_VERSION,
        }


class JobMatchScoringEngine:
    def calculate(
        self, snapshot: ProfileSnapshot, job: JobPosting, analysis: JobAnalysis
    ) -> MatchCalculation:
        job_skills = extract_job_skills(analysis)
        user_skills = {normalize(skill.skill.name): skill for skill in snapshot.skills}

        matched_skills, missing_skills, skill_score = self.skill_score(user_skills, job_skills)
        role_score, role_strengths = self.role_score(snapshot, job, analysis)
        experience_score, experience_gaps = self.experience_score(snapshot, analysis)
        project_score, matched_projects = self.project_score(
            snapshot.projects, job_skills, analysis
        )
        preference_score, preference_gaps = self.preference_score(snapshot.preferences, job)
        risk_score, risks, hard_exclusion = self.risk_score(
            snapshot.exclusions, job, analysis, missing_skills
        )
        profile_completeness = completeness(snapshot)

        total_score = clamp(
            role_score * WEIGHTS["role"]
            + skill_score * WEIGHTS["skill"]
            + experience_score * WEIGHTS["experience"]
            + project_score * WEIGHTS["project"]
            + preference_score * WEIGHTS["preference"]
            + risk_score * WEIGHTS["risk"]
        )
        grade = grade_for(total_score)
        recommendation_status = recommendation_for(
            total_score, hard_exclusion, profile_completeness
        )
        strengths = role_strengths + [
            {
                "code": "MATCHED_SKILL",
                "title": f"{item['name']} skill matches",
                "evidence": item["evidence"],
            }
            for item in matched_skills[:5]
        ]
        gaps = [
            {
                "code": "MISSING_SKILL",
                "title": f"{item['name']} skill needs evidence",
                "description": f"Requirement type: {item['requirement']}",
                "impact": item["impact"],
            }
            for item in missing_skills[:5]
        ]
        gaps.extend(experience_gaps)
        gaps.extend(preference_gaps)

        return MatchCalculation(
            total_score=total_score,
            grade=grade,
            recommendation_status=recommendation_status,
            role_score=role_score,
            skill_score=skill_score,
            experience_score=experience_score,
            project_score=project_score,
            preference_score=preference_score,
            risk_score=risk_score,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            matched_projects=matched_projects,
            strengths=strengths,
            gaps=gaps,
            risks=risks,
            recommendation_summary=summary_for(total_score, recommendation_status, gaps, risks),
            profile_completeness=profile_completeness,
        )

    def role_score(
        self, snapshot: ProfileSnapshot, job: JobPosting, analysis: JobAnalysis
    ) -> tuple[int, list[dict[str, Any]]]:
        target_text = " ".join(
            str(item or "")
            for item in [
                job.title,
                job.position,
                (analysis.position_data or {}).get("title"),
                (analysis.position_data or {}).get("category"),
            ]
        )
        source_text = " ".join(
            str(item or "")
            for item in [
                snapshot.profile.desired_job_title,
                snapshot.profile.headline,
                snapshot.profile.introduction,
                *(project.role for project in snapshot.projects),
                *(experience.position for experience in snapshot.experiences),
            ]
        )
        target_tokens = token_set(target_text)
        source_tokens = token_set(source_text)
        overlap = target_tokens & source_tokens
        desired_title = normalize(snapshot.profile.desired_job_title)

        if desired_title and desired_title in normalize(target_text):
            score = 90
        elif overlap:
            score = min(80, 45 + len(overlap) * 10)
        else:
            score = 35

        strengths = []
        if overlap:
            strengths.append(
                {
                    "code": "ROLE_KEYWORD_MATCH",
                    "title": "Profile role keywords overlap with the job.",
                    "evidence": ", ".join(sorted(overlap)[:5]),
                }
            )
        return clamp(score), strengths

    def skill_score(
        self, user_skills: dict[str, UserSkill], job_skills: list[dict[str, str]]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
        if not job_skills:
            return [], [], 55

        total_weight = 0
        matched_weight = 0
        matched = []
        missing = []
        for skill in job_skills:
            name = skill["name"]
            key = normalize(name)
            requirement = skill.get("requirement", "MENTIONED")
            weight = {"REQUIRED": 3, "PREFERRED": 2}.get(requirement, 1)
            total_weight += weight
            if key in user_skills:
                matched_weight += weight
                matched.append(
                    {
                        "name": name,
                        "requirement": requirement,
                        "user_source": "USER_SKILL",
                        "evidence": user_skills[key].skill.name,
                    }
                )
            else:
                missing.append(
                    {"name": name, "requirement": requirement, "impact": impact(requirement)}
                )
        return matched, missing, clamp((matched_weight / total_weight) * 100)

    def experience_score(
        self, snapshot: ProfileSnapshot, analysis: JobAnalysis
    ) -> tuple[int, list[dict[str, Any]]]:
        required = (analysis.experience_data or {}).get("minimum_years")
        entry_allowed = (analysis.experience_data or {}).get("entry_level_allowed")
        user_years = snapshot.profile.years_of_experience
        if required is None:
            return 65, []
        if user_years >= required:
            return 100, []
        if required == 0 or entry_allowed:
            return 85, []
        gap = required - user_years
        return clamp(100 - gap * 25), [
            {
                "code": "EXPERIENCE_SHORTAGE",
                "title": "Experience is lower than the parsed job requirement.",
                "description": f"Profile years: {user_years}, required years: {required}",
                "impact": "HIGH" if gap >= 2 else "MEDIUM",
            }
        ]

    def project_score(
        self, projects: list[Project], job_skills: list[dict[str, str]], analysis: JobAnalysis
    ) -> tuple[int, list[dict[str, Any]]]:
        if not projects:
            return 45, []

        required = {normalize(skill["name"]) for skill in job_skills}
        responsibility_tokens = token_set(json.dumps(analysis.responsibilities or []))
        matched_projects = []
        for project in projects:
            project_skill_names = {
                normalize(link.skill.name) for link in project.project_skills if link.skill
            }
            matched = sorted(required & project_skill_names)
            project_tokens = token_set(
                " ".join(
                    [
                        project.name,
                        project.summary or "",
                        project.role or "",
                        project.description or "",
                        project.responsibilities or "",
                    ]
                )
            )
            keyword_overlap = sorted(project_tokens & responsibility_tokens)[:5]
            if matched or keyword_overlap:
                matched_projects.append(
                    {
                        "project_id": project.id,
                        "title": project.name,
                        "matched_skills": matched,
                        "matched_keywords": keyword_overlap,
                        "reason": "Project evidence overlaps with job skills or responsibilities.",
                    }
                )
        if not matched_projects:
            return 55, []
        return clamp(60 + len(matched_projects) * 15), matched_projects[:5]

    def preference_score(
        self, preferences: JobPreference | None, job: JobPosting
    ) -> tuple[int, list[dict[str, Any]]]:
        if not preferences:
            return 70, []

        score = 70
        notes = []
        if preferences.preferred_employment_types:
            if job.employment_type.value in preferences.preferred_employment_types:
                score += 10
            else:
                score -= 15
                notes.append(
                    {"code": "EMPLOYMENT_TYPE_MISMATCH", "title": "Employment type mismatch."}
                )
        if preferences.remote_preference.value != "ANY":
            if job.work_type.value == preferences.remote_preference.value:
                score += 10
            else:
                score -= 15
                notes.append({"code": "WORK_TYPE_MISMATCH", "title": "Work type mismatch."})
        if preferences.preferred_locations and job.location:
            if any(normalize(loc) in normalize(job.location) for loc in preferences.preferred_locations):
                score += 10
            else:
                score -= 10
                notes.append({"code": "LOCATION_MISMATCH", "title": "Location preference mismatch."})
        if preferences.minimum_salary and job.salary_max and job.salary_max < preferences.minimum_salary:
            score -= 15
            notes.append(
                {"code": "SALARY_BELOW_PREFERENCE", "title": "Salary is below preference."}
            )
        return clamp(score), notes

    def risk_score(
        self,
        exclusions: list[ExcludedCondition],
        job: JobPosting,
        analysis: JobAnalysis,
        missing_skills: list[dict[str, Any]],
    ) -> tuple[int, list[dict[str, Any]], bool]:
        risks = []
        hard_exclusion = False
        haystack = normalize(
            " ".join(
                [
                    job.title,
                    job.position or "",
                    job.location or "",
                    job.description or "",
                    job.requirements or "",
                    job.preferred_qualifications or "",
                    json.dumps(analysis_payload(analysis), ensure_ascii=False),
                ]
            )
        )

        for condition in exclusions:
            if not condition.is_active:
                continue
            value = normalize(condition.value)
            matched = False
            if condition.condition_type == ExcludedConditionType.EMPLOYMENT_TYPE:
                matched = value == normalize(job.employment_type.value)
            elif condition.condition_type == ExcludedConditionType.COMPANY_SIZE and job.company:
                matched = value == normalize(job.company.company_size.value)
            else:
                matched = bool(value and value in haystack)
            if matched:
                hard_exclusion = True
                risks.append(
                    {
                        "code": f"EXCLUDED_{condition.condition_type.value}",
                        "level": "HIGH",
                        "title": "Job matches an active exclusion condition.",
                        "description": condition.reason or condition.value,
                        "evidence": condition.value,
                    }
                )

        for skill in missing_skills:
            if skill["requirement"] == "REQUIRED":
                risks.append(
                    {
                        "code": "MISSING_REQUIRED_SKILL",
                        "level": "HIGH",
                        "title": f"Required skill is missing: {skill['name']}",
                        "evidence": skill["name"],
                    }
                )

        score = 100 - sum(35 if risk["level"] == "HIGH" else 15 for risk in risks)
        return clamp(score), risks, hard_exclusion


def extract_job_skills(analysis: JobAnalysis) -> list[dict[str, str]]:
    skills = []
    seen = set()
    for item in analysis.technical_skills or []:
        name = str(item.get("name", "")).strip()
        if not name:
            continue
        key = normalize(name)
        if key in seen:
            continue
        seen.add(key)
        skills.append(
            {
                "name": name,
                "requirement": str(item.get("requirement") or "MENTIONED").upper(),
            }
        )
    return skills


def profile_hash(snapshot: ProfileSnapshot) -> str:
    data = {
        "profile": {
            "display_name": snapshot.profile.display_name,
            "headline": snapshot.profile.headline,
            "career_level": snapshot.profile.career_level.value,
            "years_of_experience": snapshot.profile.years_of_experience,
            "desired_job_title": snapshot.profile.desired_job_title,
            "introduction": snapshot.profile.introduction,
            "updated_at": serialize(snapshot.profile.updated_at),
        },
        "skills": [
            {
                "name": skill.skill.name,
                "category": skill.skill.category.value,
                "proficiency_level": skill.proficiency_level.value,
                "years_of_experience": skill.years_of_experience,
                "is_primary": skill.is_primary,
                "updated_at": serialize(skill.updated_at),
            }
            for skill in snapshot.skills
        ],
        "experiences": [
            {
                "company_name": item.company_name,
                "position": item.position,
                "employment_type": item.employment_type.value,
                "start_date": serialize(item.start_date),
                "end_date": serialize(item.end_date),
                "is_current": item.is_current,
                "description": item.description,
                "achievements": item.achievements,
                "updated_at": serialize(item.updated_at),
            }
            for item in snapshot.experiences
        ],
        "projects": [
            {
                "name": project.name,
                "summary": project.summary,
                "role": project.role,
                "description": project.description,
                "responsibilities": project.responsibilities,
                "achievements": project.achievements,
                "skills": [link.skill.name for link in project.project_skills if link.skill],
                "updated_at": serialize(project.updated_at),
            }
            for project in snapshot.projects
        ],
        "preferences": attrs(snapshot.preferences) if snapshot.preferences else None,
        "exclusions": [attrs(item) for item in snapshot.exclusions if item.is_active],
    }
    return stable_hash(data)


def job_analysis_hash(analysis: JobAnalysis) -> str:
    return stable_hash(
        {
            "id": analysis.id,
            "updated_at": serialize(analysis.updated_at),
            "input_hash": analysis.input_hash,
            "summary": analysis.summary,
            **analysis_payload(analysis),
        }
    )


def analysis_payload(analysis: JobAnalysis) -> dict[str, Any]:
    return {
        "position_data": analysis.position_data,
        "responsibilities": analysis.responsibilities,
        "required_qualifications": analysis.required_qualifications,
        "preferred_qualifications": analysis.preferred_qualifications,
        "technical_skills": analysis.technical_skills,
        "experience_data": analysis.experience_data,
        "education_data": analysis.education_data,
        "work_conditions": analysis.work_conditions,
        "company_values": analysis.company_values,
        "keywords": analysis.keywords,
    }


def attrs(obj: Any) -> dict[str, Any]:
    if obj is None:
        return {}
    values = {}
    for key, value in vars(obj).items():
        if key.startswith("_") or key in {"metadata", "registry"}:
            continue
        values[key] = getattr(value, "value", serialize(value))
    return values


def stable_hash(data: Any) -> str:
    payload = json.dumps(data, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()


def serialize(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def normalize(value: str) -> str:
    normalized = re.sub(r"\s+", " ", value.strip().lower())
    return ALIASES.get(normalized, normalized)


def token_set(value: str) -> set[str]:
    return {
        normalize(token)
        for token in re.split(r"[^0-9a-zA-Z가-힣+#.]+", value)
        if len(token) >= 2
    }


def clamp(score: float) -> int:
    return max(0, min(100, round(score)))


def grade_for(score: int) -> JobMatchGrade:
    if score >= 85:
        return JobMatchGrade.EXCELLENT
    if score >= 70:
        return JobMatchGrade.GOOD
    if score >= 50:
        return JobMatchGrade.MODERATE
    if score >= 30:
        return JobMatchGrade.LOW
    return JobMatchGrade.VERY_LOW


def recommendation_for(
    score: int, hard_exclusion: bool, profile_completeness: int
) -> JobMatchRecommendationStatus:
    if profile_completeness < 35:
        return JobMatchRecommendationStatus.INSUFFICIENT_DATA
    if hard_exclusion:
        return JobMatchRecommendationStatus.NOT_RECOMMENDED
    if score >= 85:
        return JobMatchRecommendationStatus.STRONGLY_RECOMMENDED
    if score >= 70:
        return JobMatchRecommendationStatus.RECOMMENDED
    if score >= 50:
        return JobMatchRecommendationStatus.CONSIDER
    return JobMatchRecommendationStatus.NOT_RECOMMENDED


def completeness(snapshot: ProfileSnapshot) -> int:
    score = 20
    if snapshot.skills:
        score += 25
    if snapshot.experiences:
        score += 20
    if snapshot.projects:
        score += 20
    if snapshot.preferences:
        score += 10
    if snapshot.profile.introduction:
        score += 5
    return clamp(score)


def impact(requirement: str) -> str:
    return {"REQUIRED": "HIGH", "PREFERRED": "MEDIUM"}.get(requirement, "LOW")


def summary_for(
    score: int,
    recommendation: JobMatchRecommendationStatus,
    gaps: list[dict[str, Any]],
    risks: list[dict[str, Any]],
) -> str:
    if recommendation == JobMatchRecommendationStatus.NOT_RECOMMENDED:
        return "지원 제외 조건 또는 높은 위험 요소가 있어 지원 우선순위가 낮습니다."
    if score >= 70:
        return "공고 요구사항과 사용자 프로필의 핵심 근거가 잘 맞습니다."
    if risks:
        return "일부 강점은 있으나 필수 조건과 위험 요소를 먼저 확인해야 합니다."
    if gaps:
        return "보완할 항목이 있어 지원 전 경험과 기술 근거를 정리하는 것이 좋습니다."
    return "프로필 정보가 충분하지 않아 보수적으로 산정했습니다."
