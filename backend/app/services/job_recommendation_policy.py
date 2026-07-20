from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Any

from app.models.career import CareerProfile, Experience, JobPreference, Project, UserSkill
from app.models.job import JobAnalysis, JobEmploymentType, JobMatch, JobPosting
from app.models.job_recommendation import (
    JobRecommendationGrade,
    JobRecommendationMatchStatus,
    JobRecommendationReasonType,
    JobRecommendationRequirementType,
    JobRecommendationSeverity,
)
from app.services.job_match_scoring import extract_job_skills, job_analysis_hash, normalize

POLICY_VERSION = "RULE_BASED_V1"
RECOMMENDATION_TYPE = "RULE_BASED"

SCORE_WEIGHTS = {
    "role": 25,
    "skill": 25,
    "experience": 15,
    "employment_type": 10,
    "location": 10,
    "project": 10,
    "preference": 5,
}

ALIASES = {
    "fast api": "fastapi",
    "fast-api": "fastapi",
    "postgres": "postgresql",
    "postgre": "postgresql",
    "js": "javascript",
    "ts": "typescript",
    "react.js": "react",
    "next": "next.js",
    "yolov11": "yolo11",
}


@dataclass
class RecommendationProfile:
    profile: CareerProfile | None
    skills: list[UserSkill]
    experiences: list[Experience]
    projects: list[Project]
    preferences: JobPreference | None


@dataclass
class RecommendationReason:
    reason_type: JobRecommendationReasonType
    requirement_type: JobRecommendationRequirementType
    label: str
    normalized_value: str | None
    match_status: JobRecommendationMatchStatus
    weight: int
    score_delta: int
    severity: JobRecommendationSeverity
    evidence: str


@dataclass
class RecommendationCalculation:
    score: int
    grade: JobRecommendationGrade
    has_blocking_mismatch: bool
    matched_count: int
    missing_count: int
    unknown_count: int
    score_breakdown: dict[str, int]
    reasons: list[RecommendationReason] = field(default_factory=list)
    missing_profile_fields: list[str] = field(default_factory=list)
    input_snapshot: dict[str, Any] = field(default_factory=dict)


class JobRecommendationPolicy:
    version = POLICY_VERSION

    def calculate(
        self,
        profile: RecommendationProfile,
        job: JobPosting,
        analysis: JobAnalysis | None,
        match: JobMatch | None,
    ) -> RecommendationCalculation:
        reasons: list[RecommendationReason] = []
        missing_profile_fields = self.missing_profile_fields(profile)
        score_breakdown = {
            "role": self.role_score(profile, job, analysis, reasons),
            "skill": self.skill_score(profile, analysis, job, reasons),
            "experience": self.experience_score(profile, analysis, reasons),
            "employment_type": self.employment_type_score(profile.preferences, job, reasons),
            "location": self.location_score(profile.preferences, job, reasons),
            "project": self.project_score(profile, analysis, reasons),
            "preference": self.preference_score(profile.preferences, job, match, reasons),
        }
        if not analysis:
            reasons.append(
                RecommendationReason(
                    reason_type=JobRecommendationReasonType.DATA_INSUFFICIENT,
                    requirement_type=JobRecommendationRequirementType.DATA,
                    label="공고 분석 데이터 부족",
                    normalized_value=None,
                    match_status=JobRecommendationMatchStatus.UNKNOWN,
                    weight=0,
                    score_delta=0,
                    severity=JobRecommendationSeverity.INFO,
                    evidence="채용공고 분석이 없어 공고 원문과 기본 필드만 사용했습니다.",
                )
            )
        has_blocking = any(
            reason.match_status == JobRecommendationMatchStatus.MISSING
            and reason.severity == JobRecommendationSeverity.REQUIRED
            for reason in reasons
        )
        raw_score = sum(score_breakdown.values())
        if missing_profile_fields:
            raw_score = max(0, raw_score - min(15, len(missing_profile_fields) * 5))
        score = clamp(raw_score)
        grade = grade_for(score, has_blocking)
        matched_count = sum(1 for reason in reasons if reason.match_status == JobRecommendationMatchStatus.MATCHED)
        missing_count = sum(1 for reason in reasons if reason.match_status == JobRecommendationMatchStatus.MISSING)
        unknown_count = sum(1 for reason in reasons if reason.match_status == JobRecommendationMatchStatus.UNKNOWN)

        return RecommendationCalculation(
            score=score,
            grade=grade,
            has_blocking_mismatch=has_blocking,
            matched_count=matched_count,
            missing_count=missing_count,
            unknown_count=unknown_count,
            score_breakdown=score_breakdown,
            reasons=reasons,
            missing_profile_fields=missing_profile_fields,
            input_snapshot={
                "policy_version": POLICY_VERSION,
                "recommendation_type": RECOMMENDATION_TYPE,
                "profile_hash": profile_hash(profile),
                "job_hash": recommendation_job_hash(job, analysis, match),
                "job_analysis_id": analysis.id if analysis else None,
                "matching_analysis_id": match.id if match else None,
                "has_job_analysis": bool(analysis),
                "has_match_analysis": bool(match),
            },
        )

    def role_score(
        self,
        profile: RecommendationProfile,
        job: JobPosting,
        analysis: JobAnalysis | None,
        reasons: list[RecommendationReason],
    ) -> int:
        desired = profile.profile.desired_job_title if profile.profile else ""
        desired_roles = profile.preferences.desired_roles if profile.preferences else []
        target = " ".join(
            [
                job.title,
                job.position or "",
                json.dumps(analysis.position_data or {}, ensure_ascii=False) if analysis else "",
            ]
        )
        source_terms = [desired, *desired_roles]
        if any(term and normalize_alias(term) in normalize_alias(target) for term in source_terms):
            reasons.append(match_reason(JobRecommendationReasonType.ROLE_MATCH, JobRecommendationRequirementType.ROLE, desired or source_terms[0], 25, "희망 직무와 공고 직무 키워드가 일치합니다."))
            return SCORE_WEIGHTS["role"]
        overlap = token_set(" ".join(source_terms)) & token_set(target)
        if overlap:
            reasons.append(match_reason(JobRecommendationReasonType.ROLE_MATCH, JobRecommendationRequirementType.ROLE, ", ".join(sorted(overlap)[:3]), 15, "희망 직무와 공고 직무 키워드가 일부 겹칩니다."))
            return 15
        reasons.append(unknown_reason(JobRecommendationRequirementType.ROLE, "직무 일치 근거 부족", "희망 직무와 공고 직무의 명확한 일치 근거가 부족합니다."))
        return 8

    def skill_score(
        self,
        profile: RecommendationProfile,
        analysis: JobAnalysis | None,
        job: JobPosting,
        reasons: list[RecommendationReason],
    ) -> int:
        user_skills = {normalize_alias(skill.skill.name): skill.skill.name for skill in profile.skills if skill.skill}
        job_skills = extract_job_skills(analysis) if analysis else skills_from_job_text(job)
        if not job_skills:
            reasons.append(unknown_reason(JobRecommendationRequirementType.SKILL, "기술 조건 정보 부족", "공고에서 명확한 기술 조건을 찾지 못했습니다."))
            return 12
        total_weight = 0
        matched_weight = 0
        for skill in job_skills:
            label = skill["name"]
            requirement = skill.get("requirement", "MENTIONED")
            weight = 3 if requirement == "REQUIRED" else 2 if requirement == "PREFERRED" else 1
            total_weight += weight
            normalized = normalize_alias(label)
            if normalized in user_skills:
                matched_weight += weight
                reasons.append(match_reason(JobRecommendationReasonType.SKILL_MATCH, JobRecommendationRequirementType.SKILL, label, weight, f"사용자 기술 `{user_skills[normalized]}`와 공고 기술이 일치합니다.", normalized))
            else:
                reasons.append(
                    RecommendationReason(
                        reason_type=JobRecommendationReasonType.SKILL_MISSING,
                        requirement_type=JobRecommendationRequirementType.SKILL,
                        label=label,
                        normalized_value=normalized,
                        match_status=JobRecommendationMatchStatus.MISSING,
                        weight=weight,
                        score_delta=0,
                        severity=JobRecommendationSeverity.REQUIRED if requirement == "REQUIRED" else JobRecommendationSeverity.PREFERRED,
                        evidence=f"공고의 {requirement} 기술이 사용자 기술 목록에 없습니다.",
                    )
                )
        return round(SCORE_WEIGHTS["skill"] * (matched_weight / total_weight)) if total_weight else 12

    def experience_score(
        self,
        profile: RecommendationProfile,
        analysis: JobAnalysis | None,
        reasons: list[RecommendationReason],
    ) -> int:
        user_years = profile.profile.years_of_experience if profile.profile else None
        required = (analysis.experience_data or {}).get("minimum_years") if analysis else None
        if user_years is None:
            reasons.append(unknown_reason(JobRecommendationRequirementType.EXPERIENCE, "경력 정보 부족", "프로필 경력 연차가 없습니다."))
            return 5
        if required is None:
            reasons.append(unknown_reason(JobRecommendationRequirementType.EXPERIENCE, "공고 경력 조건 불명확", "공고 분석에서 최소 경력 조건을 찾지 못했습니다."))
            return 10
        if user_years >= required:
            reasons.append(match_reason(JobRecommendationReasonType.EXPERIENCE_MATCH, JobRecommendationRequirementType.EXPERIENCE, f"{user_years}년", 15, "프로필 경력 연차가 공고 요구 경력을 충족합니다."))
            return SCORE_WEIGHTS["experience"]
        gap = required - user_years
        reasons.append(
            RecommendationReason(
                reason_type=JobRecommendationReasonType.EXPERIENCE_GAP,
                requirement_type=JobRecommendationRequirementType.EXPERIENCE,
                label=f"{required}년",
                normalized_value=str(required),
                match_status=JobRecommendationMatchStatus.MISSING,
                weight=15,
                score_delta=0,
                severity=JobRecommendationSeverity.REQUIRED if gap >= 2 else JobRecommendationSeverity.PREFERRED,
                evidence=f"프로필 경력 {user_years}년이 공고 요구 {required}년보다 낮습니다.",
            )
        )
        return max(0, SCORE_WEIGHTS["experience"] - gap * 5)

    def employment_type_score(
        self,
        preferences: JobPreference | None,
        job: JobPosting,
        reasons: list[RecommendationReason],
    ) -> int:
        if not preferences or not preferences.preferred_employment_types:
            return 6
        if job.employment_type.value in preferences.preferred_employment_types:
            reasons.append(match_reason(JobRecommendationReasonType.EMPLOYMENT_TYPE_MATCH, JobRecommendationRequirementType.EMPLOYMENT_TYPE, job.employment_type.value, 10, "희망 고용 형태와 공고 고용 형태가 일치합니다."))
            return SCORE_WEIGHTS["employment_type"]
        if job.employment_type != JobEmploymentType.UNKNOWN:
            reasons.append(missing_reason(JobRecommendationReasonType.EMPLOYMENT_TYPE_MISMATCH, JobRecommendationRequirementType.EMPLOYMENT_TYPE, job.employment_type.value, "희망 고용 형태와 다릅니다."))
        return 2

    def location_score(
        self,
        preferences: JobPreference | None,
        job: JobPosting,
        reasons: list[RecommendationReason],
    ) -> int:
        if not preferences or not preferences.preferred_locations:
            return 6
        if job.location and any(normalize_alias(loc) in normalize_alias(job.location) for loc in preferences.preferred_locations):
            reasons.append(match_reason(JobRecommendationReasonType.LOCATION_MATCH, JobRecommendationRequirementType.LOCATION, job.location, 10, "희망 근무 지역과 공고 지역이 일치합니다."))
            return SCORE_WEIGHTS["location"]
        reasons.append(missing_reason(JobRecommendationReasonType.LOCATION_MISMATCH, JobRecommendationRequirementType.LOCATION, job.location or "지역 정보 없음", "희망 근무 지역과 명확히 일치하지 않습니다."))
        return 3

    def project_score(
        self,
        profile: RecommendationProfile,
        analysis: JobAnalysis | None,
        reasons: list[RecommendationReason],
    ) -> int:
        if not profile.projects:
            reasons.append(unknown_reason(JobRecommendationRequirementType.PROJECT, "프로젝트 정보 부족", "등록된 프로젝트가 없습니다."))
            return 4
        job_skills = {normalize_alias(skill["name"]) for skill in extract_job_skills(analysis)} if analysis else set()
        project_tokens = set()
        for project in profile.projects:
            project_tokens |= token_set(" ".join([project.name, project.summary or "", project.role or "", project.description or ""]))
            project_tokens |= {normalize_alias(link.skill.name) for link in project.project_skills if link.skill}
        overlap = sorted(job_skills & project_tokens)
        if overlap:
            reasons.append(match_reason(JobRecommendationReasonType.PROJECT_MATCH, JobRecommendationRequirementType.PROJECT, ", ".join(overlap[:3]), 10, "프로젝트 기술/키워드가 공고 요구와 겹칩니다."))
            return SCORE_WEIGHTS["project"]
        return 5

    def preference_score(
        self,
        preferences: JobPreference | None,
        job: JobPosting,
        match: JobMatch | None,
        reasons: list[RecommendationReason],
    ) -> int:
        score = 2
        if job.is_favorite:
            score += 2
            reasons.append(match_reason(JobRecommendationReasonType.PREFERENCE_MATCH, JobRecommendationRequirementType.PREFERENCE, "관심 공고", 2, "사용자가 관심 공고로 표시했습니다."))
        if preferences and preferences.priority_keywords:
            haystack = normalize_alias(" ".join([job.title, job.position or "", job.description or "", job.requirements or ""]))
            hits = [keyword for keyword in preferences.priority_keywords if normalize_alias(keyword) in haystack]
            if hits:
                score += 2
                reasons.append(match_reason(JobRecommendationReasonType.PREFERENCE_MATCH, JobRecommendationRequirementType.PREFERENCE, ", ".join(hits[:3]), 2, "선호 키워드가 공고 내용에 포함됩니다."))
        if match and match.total_score >= 70:
            score += 1
        return min(SCORE_WEIGHTS["preference"], score)

    def missing_profile_fields(self, profile: RecommendationProfile) -> list[str]:
        missing = []
        if not profile.profile:
            return ["career_profile", "desired_job_title", "skills", "preferences"]
        if not profile.profile.desired_job_title:
            missing.append("desired_job_title")
        if not profile.skills:
            missing.append("skills")
        if not profile.preferences:
            missing.append("preferences")
        elif not profile.preferences.preferred_locations:
            missing.append("preferred_locations")
        if not profile.experiences:
            missing.append("experiences")
        return missing


def recommendation_job_hash(job: JobPosting, analysis: JobAnalysis | None, match: JobMatch | None = None) -> str:
    payload = {
        "job_id": job.id,
        "job_updated_at": job.updated_at.isoformat() if job.updated_at else None,
        "content_hash": job.content_hash,
        "analysis_hash": job_analysis_hash(analysis) if analysis else None,
        "match_id": match.id if match else None,
        "match_hash": match.job_analysis_hash if match else None,
    }
    return digest(payload)


def profile_hash(profile: RecommendationProfile) -> str:
    payload = {
        "profile_updated_at": profile.profile.updated_at.isoformat() if profile.profile else None,
        "profile": {
            "desired_job_title": profile.profile.desired_job_title if profile.profile else None,
            "career_level": profile.profile.career_level.value if profile.profile else None,
            "years_of_experience": profile.profile.years_of_experience if profile.profile else None,
        },
        "skills": [(item.skill.normalized_name, item.proficiency_level.value, item.years_of_experience) for item in profile.skills if item.skill],
        "experiences": [(item.position, item.updated_at.isoformat() if item.updated_at else None) for item in profile.experiences],
        "projects": [(item.name, item.updated_at.isoformat() if item.updated_at else None) for item in profile.projects],
        "preferences": {
            "employment_types": profile.preferences.preferred_employment_types if profile.preferences else [],
            "locations": profile.preferences.preferred_locations if profile.preferences else [],
            "roles": profile.preferences.desired_roles if profile.preferences else [],
            "keywords": profile.preferences.priority_keywords if profile.preferences else [],
        },
    }
    return digest(payload)


def normalize_alias(value: str) -> str:
    normalized = normalize(value)
    return ALIASES.get(normalized, normalized)


def token_set(value: str) -> set[str]:
    return {normalize_alias(token) for token in re.split(r"[^0-9A-Za-z가-힣+#.]+", value) if len(token.strip()) >= 2}


def skills_from_job_text(job: JobPosting) -> list[dict[str, str]]:
    text = " ".join([job.requirements or "", job.preferred_qualifications or "", job.description or ""])
    known = ["Python", "FastAPI", "Django", "Flask", "React", "TypeScript", "JavaScript", "PostgreSQL", "Redis", "Docker", "Kubernetes", "AWS"]
    result = []
    for skill in known:
        if normalize_alias(skill) in normalize_alias(text):
            result.append({"name": skill, "requirement": "MENTIONED"})
    return result


def grade_for(score: int, blocked: bool) -> JobRecommendationGrade:
    if blocked:
        return JobRecommendationGrade.BLOCKED
    if score >= 85:
        return JobRecommendationGrade.EXCELLENT
    if score >= 70:
        return JobRecommendationGrade.GOOD
    if score >= 50:
        return JobRecommendationGrade.POSSIBLE
    return JobRecommendationGrade.LOW


def clamp(value: float | int) -> int:
    return max(0, min(100, round(value)))


def digest(payload: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def match_reason(
    reason_type: JobRecommendationReasonType,
    requirement_type: JobRecommendationRequirementType,
    label: str,
    score_delta: int,
    evidence: str,
    normalized: str | None = None,
) -> RecommendationReason:
    return RecommendationReason(
        reason_type=reason_type,
        requirement_type=requirement_type,
        label=label,
        normalized_value=normalized or normalize_alias(label),
        match_status=JobRecommendationMatchStatus.MATCHED,
        weight=score_delta,
        score_delta=score_delta,
        severity=JobRecommendationSeverity.INFO,
        evidence=evidence,
    )


def missing_reason(
    reason_type: JobRecommendationReasonType,
    requirement_type: JobRecommendationRequirementType,
    label: str,
    evidence: str,
) -> RecommendationReason:
    return RecommendationReason(
        reason_type=reason_type,
        requirement_type=requirement_type,
        label=label,
        normalized_value=normalize_alias(label),
        match_status=JobRecommendationMatchStatus.MISSING,
        weight=0,
        score_delta=0,
        severity=JobRecommendationSeverity.PREFERRED,
        evidence=evidence,
    )


def unknown_reason(
    requirement_type: JobRecommendationRequirementType,
    label: str,
    evidence: str,
) -> RecommendationReason:
    return RecommendationReason(
        reason_type=JobRecommendationReasonType.DATA_INSUFFICIENT,
        requirement_type=requirement_type,
        label=label,
        normalized_value=None,
        match_status=JobRecommendationMatchStatus.UNKNOWN,
        weight=0,
        score_delta=0,
        severity=JobRecommendationSeverity.INFO,
        evidence=evidence,
    )
