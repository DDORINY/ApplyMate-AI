import json
import time
from dataclasses import dataclass
from typing import Protocol

import httpx
from pydantic import BaseModel, ValidationError

from app.core.config import Settings
from app.core.exceptions import AppError
from app.schemas.application_document import (
    ApplicationDocumentBlock,
    ApplicationDocumentSourceReference,
    ApplicationDocumentStructuredData,
)
from app.schemas.document_improvement import (
    DocumentImprovementEvidence,
    DocumentImprovementSentenceSuggestionData,
    DocumentImprovementStructuredData,
)
from app.models.document_improvement import (
    DocumentImprovementChangeType,
    DocumentImprovementRiskLevel,
    DocumentImprovementSourceType,
)
from app.schemas.job_analysis import JobAnalysisStructuredData
from app.schemas.resume_analysis import (
    ResumeAnalysisEvidence,
    ResumeAnalysisSkill,
    ResumeAnalysisStructuredData,
    ResumeAnalysisWarning,
)


@dataclass(frozen=True)
class AIProviderResult:
    parsed_data: BaseModel
    provider: str
    model: str | None
    request_id: str | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    latency_ms: int | None = None
    raw_response: str | None = None


class AIProvider(Protocol):
    provider: str
    model: str | None

    async def analyze_job(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_schema: type[BaseModel],
    ) -> AIProviderResult:
        ...

    async def analyze_resume(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_schema: type[BaseModel],
    ) -> AIProviderResult:
        ...

    async def generate_application_document(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_schema: type[BaseModel],
    ) -> AIProviderResult:
        ...

    async def improve_application_document(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_schema: type[BaseModel],
    ) -> AIProviderResult:
        ...


class DisabledAIProvider:
    provider = "disabled"
    model = None

    async def analyze_job(self, **_kwargs: object) -> AIProviderResult:
        raise AppError("AI_PROVIDER_DISABLED", "AI provider is disabled.", 503)

    async def analyze_resume(self, **_kwargs: object) -> AIProviderResult:
        raise AppError("AI_PROVIDER_DISABLED", "AI provider is disabled.", 503)

    async def generate_application_document(self, **_kwargs: object) -> AIProviderResult:
        raise AppError("AI_PROVIDER_DISABLED", "AI document generation provider is disabled.", 503)

    async def improve_application_document(self, **_kwargs: object) -> AIProviderResult:
        raise AppError("AI_PROVIDER_DISABLED", "AI document improvement provider is disabled.", 503)


class MockAIProvider:
    provider = "mock"
    model = "mock-job-analyzer"

    async def analyze_job(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_schema: type[BaseModel],
    ) -> AIProviderResult:
        _ = system_prompt
        started = time.perf_counter()
        skills = [
            skill
            for skill in ["Python", "FastAPI", "SQLAlchemy", "PostgreSQL", "Docker", "TypeScript", "React", "Next.js"]
            if skill.lower() in user_prompt.lower()
        ] or ["검토 필요"]
        data = JobAnalysisStructuredData(
            summary="저장된 채용공고 내용을 기반으로 직무, 자격요건, 기술 스택을 구조화했습니다.",
            position={
                "title": _line_after(user_prompt, "공고 제목") or _line_after(user_prompt, "title") or None,
                "category": "UNKNOWN",
                "seniority": "UNKNOWN",
                "employment_type": _line_after(user_prompt, "고용 형태") or "UNKNOWN",
            },
            responsibilities=[
                {
                    "text": "채용공고에 명시된 주요 업무 수행",
                    "importance": "HIGH",
                    "evidence": _line_after(user_prompt, "주요 업무") or "공고 본문",
                }
            ],
            required_qualifications=[
                {
                    "text": _line_after(user_prompt, "필수 조건") or "공고에 명시된 필수 조건 확인 필요",
                    "category": "TECHNICAL",
                    "importance": "REQUIRED",
                    "evidence": _line_after(user_prompt, "필수 조건") or "필수 조건 영역",
                }
            ],
            preferred_qualifications=[
                {
                    "text": _line_after(user_prompt, "우대 조건") or "우대 조건이 명확하지 않습니다.",
                    "category": "OTHER",
                    "importance": "PREFERRED",
                    "evidence": _line_after(user_prompt, "우대 조건") or None,
                }
            ],
            technical_skills=[
                {
                    "name": skill,
                    "category": "TECHNICAL",
                    "requirement": "REQUIRED",
                    "evidence": "채용공고 텍스트",
                }
                for skill in skills
            ],
            experience={
                "minimum_years": None,
                "maximum_years": None,
                "entry_level_allowed": None,
                "description": _line_after(user_prompt, "경력 조건") or None,
            },
            education={"minimum_level": "UNKNOWN", "description": _line_after(user_prompt, "학력 조건") or None},
            work_conditions={
                "location": _line_after(user_prompt, "근무 지역") or None,
                "work_type": _line_after(user_prompt, "근무 형태") or "UNKNOWN",
                "employment_type": _line_after(user_prompt, "고용 형태") or "UNKNOWN",
            },
            recruitment_process=[
                item.strip()
                for item in (_line_after(user_prompt, "채용 절차") or "").replace(">", "-").split("-")
                if item.strip()
            ],
            deadline={"type": _line_after(user_prompt, "마감 유형") or "UNKNOWN", "date": None, "description": _line_after(user_prompt, "마감일") or None},
            company_values=[],
            keywords=skills,
            warnings=[{"code": "MOCK_PROVIDER", "message": "Mock Provider 결과입니다."}],
            confidence={"overall": 0.72, "responsibilities": 0.7, "qualifications": 0.7, "skills": 0.75, "deadline": 0.5},
        )
        parsed = response_schema.model_validate(data.model_dump())
        return _result(parsed, self.provider, self.model, "mock-job-analysis", user_prompt, started)

    async def analyze_resume(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_schema: type[BaseModel],
    ) -> AIProviderResult:
        _ = system_prompt
        started = time.perf_counter()
        resume_text = _resume_text_from_prompt(user_prompt)
        skill_names = _resume_skill_candidates(resume_text)
        evidence_text = _first_non_empty_line(resume_text) or resume_text[:200] or "resume text"
        evidence = ResumeAnalysisEvidence(source="RAW_TEXT", source_text=evidence_text[:1000])
        data = ResumeAnalysisStructuredData(
            summary="업로드된 이력서 텍스트를 기반으로 주요 기술과 경력 후보를 구조화했습니다.",
            headline=_first_non_empty_line(resume_text),
            skills=[ResumeAnalysisSkill(name=skill, category="TECHNICAL", evidence=[evidence]) for skill in skill_names],
            experiences=[],
            projects=[],
            education=[],
            keywords=skill_names,
            warnings=[ResumeAnalysisWarning(code="MOCK_PROVIDER", message="Mock Provider 결과입니다.")],
            confidence={"overall": 0.65 if skill_names else 0.35, "skills": 0.7 if skill_names else 0.2, "experiences": 0.3, "projects": 0.3, "education": 0.3},
        )
        parsed = response_schema.model_validate(data.model_dump())
        return _result(parsed, self.provider, "mock-resume-analyzer", "mock-resume-analysis", user_prompt, started)

    async def generate_application_document(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_schema: type[BaseModel],
    ) -> AIProviderResult:
        _ = system_prompt
        started = time.perf_counter()
        sources = _application_document_sources_from_prompt(user_prompt)
        document_type = _line_after(user_prompt, "document_type") or "CUSTOM_QUESTION"
        title = _line_after(user_prompt, "title") or "지원 문서 초안"
        question = _line_after(user_prompt, "question")
        selected = sources[:3] or [
            {
                "source_type": "user_instruction",
                "source_id": "manual",
                "field_path": "instructions",
                "text": "사용자가 직접 확인해야 하는 지원 문서 초안입니다.",
            }
        ]
        blocks = []
        for sequence, source in enumerate(selected, start=1):
            evidence_text = str(source["text"])[:500]
            block_text = _application_document_sentence(sequence, question, evidence_text)
            blocks.append(
                ApplicationDocumentBlock(
                    sequence=sequence,
                    text=block_text,
                    source_references=[
                        ApplicationDocumentSourceReference(
                            source_type=str(source["source_type"]),
                            source_id=str(source["source_id"]),
                            field_path=str(source["field_path"]),
                            evidence_text=evidence_text,
                        )
                    ],
                    confidence=0.72 if source["source_type"] != "user_instruction" else 0.55,
                    requires_review=source["source_type"] == "user_instruction",
                    review_reason="추가 근거 확인이 필요합니다." if source["source_type"] == "user_instruction" else None,
                )
            )
        content = "\n\n".join(block.text for block in blocks)
        data = ApplicationDocumentStructuredData(
            title=title,
            document_type=document_type,
            content=content,
            blocks=blocks,
            warnings=["MOCK_PROVIDER: 실제 AI 호출 없이 결정론적 초안을 생성했습니다."],
            requires_review=any(block.requires_review for block in blocks),
            character_count_candidate=len(content),
        )
        parsed = response_schema.model_validate(data.model_dump())
        return _result(parsed, self.provider, "mock-application-document-writer", "mock-application-document", user_prompt + content, started)

    async def improve_application_document(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_schema: type[BaseModel],
    ) -> AIProviderResult:
        _ = system_prompt
        started = time.perf_counter()
        current = _section_after(user_prompt, "current_document:", "sources:").strip()
        first_sentence = _first_sentence(current) or current[:200] or "지원 문서 내용"
        source_text = _first_source_text(user_prompt) or first_sentence
        improvement_type = _line_after(user_prompt, "improvement_type") or "CLARITY"
        suggested = _mock_improved_sentence(first_sentence, improvement_type, source_text)
        suggested_content = current.replace(first_sentence, suggested, 1) if current else suggested
        evidence = DocumentImprovementEvidence(
            source_type=DocumentImprovementSourceType.CURRENT_DOCUMENT,
            source_id="base_version",
            source_text=first_sentence[:1000],
        )
        source_evidence = DocumentImprovementEvidence(
            source_type=DocumentImprovementSourceType.USER_INSTRUCTION,
            source_id="request",
            source_text=source_text[:1000],
        )
        data = DocumentImprovementStructuredData(
            summary="Mock Provider가 기존 문서의 첫 문장을 기준으로 개선안을 생성했습니다.",
            overall_feedback="승인 전 기존 문서는 변경되지 않습니다. 제안 문장의 사실 여부를 검토해 주세요.",
            suggested_title=_line_after(user_prompt, "title") or "AI 개선본",
            suggested_content=suggested_content,
            sentence_suggestions=[
                DocumentImprovementSentenceSuggestionData(
                    id="mock-1",
                    paragraph_index=0,
                    sentence_index=0,
                    original_text=first_sentence,
                    suggested_text=suggested,
                    change_type=DocumentImprovementChangeType.REWRITE,
                    reason="문장의 목적과 직무 연결성을 더 명확히 표현했습니다.",
                    evidence=[evidence, source_evidence],
                    risk_level=DocumentImprovementRiskLevel.LOW,
                    selected=True,
                )
            ],
            warnings=["MOCK_PROVIDER: 실제 OpenAI 호출 없이 결정론적 개선안을 생성했습니다."],
            missing_information=[],
            used_sources=[evidence, source_evidence],
            confidence={"overall": 0.72, "evidence": 0.7},
        )
        parsed = response_schema.model_validate(data.model_dump())
        return _result(parsed, self.provider, "mock-document-improver", "mock-document-improvement", user_prompt + suggested_content, started)


class OpenAIProvider:
    provider = "openai"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.model = settings.openai_model

    async def analyze_job(self, *, system_prompt: str, user_prompt: str, response_schema: type[BaseModel]) -> AIProviderResult:
        return await self._request_json(system_prompt=system_prompt, user_prompt=user_prompt, response_schema=response_schema)

    async def analyze_resume(self, *, system_prompt: str, user_prompt: str, response_schema: type[BaseModel]) -> AIProviderResult:
        return await self._request_json(system_prompt=system_prompt, user_prompt=user_prompt, response_schema=response_schema)

    async def generate_application_document(self, *, system_prompt: str, user_prompt: str, response_schema: type[BaseModel]) -> AIProviderResult:
        return await self._request_json(system_prompt=system_prompt, user_prompt=user_prompt, response_schema=response_schema)

    async def improve_application_document(self, *, system_prompt: str, user_prompt: str, response_schema: type[BaseModel]) -> AIProviderResult:
        return await self._request_json(system_prompt=system_prompt, user_prompt=user_prompt, response_schema=response_schema)

    async def _request_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_schema: type[BaseModel],
    ) -> AIProviderResult:
        started = time.perf_counter()
        payload = {
            "model": self.settings.openai_model,
            "input": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            "text": {"format": {"type": "json_object"}},
        }
        try:
            async with httpx.AsyncClient(timeout=self.settings.ai_request_timeout_seconds) as client:
                response = await client.post(
                    "https://api.openai.com/v1/responses",
                    headers={"Authorization": f"Bearer {self.settings.openai_api_key}"},
                    json=payload,
                )
        except httpx.TimeoutException as exc:
            raise AppError("AI_PROVIDER_TIMEOUT", "AI provider request timed out.", 504) from exc
        except httpx.HTTPError as exc:
            raise AppError("AI_PROVIDER_REQUEST_FAILED", "AI provider request failed.", 502) from exc
        if response.status_code == 429:
            raise AppError("AI_PROVIDER_RATE_LIMITED", "AI provider rate limit exceeded.", 429)
        if response.status_code >= 500:
            raise AppError("AI_PROVIDER_UNAVAILABLE", "AI provider is temporarily unavailable.", 502)
        if response.status_code >= 400:
            raise AppError("AI_PROVIDER_REQUEST_FAILED", "AI provider request failed.", 502)

        body = response.json()
        output_text = body.get("output_text") or _extract_output_text(body)
        try:
            parsed = response_schema.model_validate_json(output_text)
        except (ValidationError, ValueError) as exc:
            raise AppError("AI_PROVIDER_INVALID_RESPONSE", "AI provider response schema is invalid.", 502) from exc
        usage = body.get("usage") or {}
        return AIProviderResult(
            parsed_data=parsed,
            provider=self.provider,
            model=self.model,
            request_id=response.headers.get("x-request-id") or body.get("id"),
            prompt_tokens=usage.get("input_tokens"),
            completion_tokens=usage.get("output_tokens"),
            total_tokens=usage.get("total_tokens"),
            latency_ms=int((time.perf_counter() - started) * 1000),
            raw_response=json.dumps(body, ensure_ascii=False),
        )


def get_ai_provider(settings: Settings) -> AIProvider:
    if settings.ai_provider == "disabled":
        return DisabledAIProvider()
    if settings.ai_provider == "mock":
        return MockAIProvider()
    if settings.ai_provider == "openai":
        if not settings.openai_api_key or not settings.openai_model:
            raise AppError("AI_PROVIDER_CONFIG_INVALID", "OPENAI_API_KEY and OPENAI_MODEL are required.", 503)
        return OpenAIProvider(settings)
    raise AppError("AI_PROVIDER_INVALID", "Unsupported AI provider.", 503)


def provider_status(settings: Settings) -> dict[str, str | bool | None]:
    enabled = settings.ai_provider != "disabled"
    model = None
    available = enabled
    if settings.ai_provider == "mock":
        model = "mock-job-analyzer"
    elif settings.ai_provider == "openai":
        model = settings.openai_model or None
        available = bool(settings.openai_api_key and settings.openai_model)
    elif settings.ai_provider != "disabled":
        available = False
    return {
        "active_provider": settings.ai_provider,
        "enabled": enabled,
        "model": model,
        "analysis_available": available,
        "generation_available": available,
        "improvement_available": available,
    }


def _result(parsed: BaseModel, provider: str, model: str | None, request_id: str, text: str, started: float) -> AIProviderResult:
    prompt_tokens = max(len(text) // 4, 1)
    return AIProviderResult(
        parsed_data=parsed,
        provider=provider,
        model=model,
        request_id=request_id,
        prompt_tokens=prompt_tokens,
        completion_tokens=160,
        total_tokens=prompt_tokens + 160,
        latency_ms=int((time.perf_counter() - started) * 1000),
        raw_response=parsed.model_dump_json(),
    )


def _extract_output_text(body: dict) -> str:
    chunks: list[str] = []
    for output in body.get("output", []):
        for content in output.get("content", []):
            text = content.get("text")
            if text:
                chunks.append(text)
    return "\n".join(chunks)


def _line_after(text: str, label: str) -> str:
    prefix = f"{label}:"
    for line in text.splitlines():
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip()
    return ""


def _resume_skill_candidates(text: str) -> list[str]:
    known_skills = [
        "Python",
        "FastAPI",
        "Django",
        "JavaScript",
        "TypeScript",
        "React",
        "Next.js",
        "SQL",
        "PostgreSQL",
        "Docker",
        "AWS",
        "Kubernetes",
        "Git",
        "Pandas",
        "TensorFlow",
        "PyTorch",
    ]
    lowered = text.lower()
    return [skill for skill in known_skills if skill.lower() in lowered]


def _first_non_empty_line(text: str) -> str | None:
    for line in text.splitlines():
        cleaned = line.strip()
        if cleaned and not cleaned.startswith("---") and ":" not in cleaned[:30]:
            return cleaned[:200]
    return None


def _resume_text_from_prompt(prompt: str) -> str:
    markers = prompt.split("---")
    if len(markers) >= 3:
        return markers[-2].strip()
    return prompt


def _application_document_sources_from_prompt(prompt: str) -> list[dict[str, str]]:
    sources: list[dict[str, str]] = []
    for line in prompt.splitlines():
        if not line.startswith("SOURCE|"):
            continue
        parts = line.split("|", 4)
        if len(parts) != 5:
            continue
        _, source_type, source_id, field_path, text = parts
        if text.strip():
            sources.append(
                {
                    "source_type": source_type,
                    "source_id": source_id,
                    "field_path": field_path,
                    "text": text.strip(),
                }
            )
    return sources


def _application_document_sentence(sequence: int, question: str, evidence_text: str) -> str:
    clean = evidence_text.strip().rstrip(".")
    if sequence == 1 and question:
        return f"{question}에 대해, 저장된 근거 중 '{clean}' 내용을 중심으로 지원 동기를 구성하겠습니다."
    if sequence == 1:
        return f"저는 저장된 근거 중 '{clean}' 경험을 바탕으로 이 직무와의 접점을 설명할 수 있습니다."
    if sequence == 2:
        return f"특히 '{clean}' 근거는 직무 수행에 필요한 역량을 보여주는 핵심 자료입니다."
    return f"따라서 '{clean}' 내용을 기반으로 지원 문서의 결론을 신중하게 정리하겠습니다."


def _section_after(text: str, start_marker: str, end_marker: str) -> str:
    if start_marker not in text:
        return ""
    section = text.split(start_marker, 1)[1]
    if end_marker in section:
        section = section.split(end_marker, 1)[0]
    return section


def _first_sentence(text: str) -> str:
    normalized = " ".join(line.strip() for line in text.splitlines() if line.strip())
    if not normalized:
        return ""
    for marker in [".", "!", "?", "다.", "요."]:
        if marker in normalized:
            index = normalized.find(marker) + len(marker)
            return normalized[:index].strip()
    return normalized[:200]


def _first_source_text(prompt: str) -> str:
    for line in prompt.splitlines():
        cleaned = line.strip()
        if cleaned.startswith("text:"):
            return cleaned.split(":", 1)[1].strip()
    return ""


def _mock_improved_sentence(original: str, improvement_type: str, source_text: str) -> str:
    source = source_text.strip().rstrip(".")
    if improvement_type == "CONCISENESS":
        return f"{source} 경험을 바탕으로 직무에 필요한 역량을 명확히 보여드리겠습니다."
    if improvement_type == "PROFESSIONAL_TONE":
        return f"{source} 경험을 기반으로, 지원 직무에서 요구되는 문제 해결 역량을 체계적으로 발휘하겠습니다."
    if improvement_type in {"SKILL_EMPHASIS", "JOB_ALIGNMENT"}:
        return f"{source} 경험을 통해 확인한 기술 역량을 지원 직무의 요구사항과 연결해 기여하겠습니다."
    if improvement_type == "LENGTH_REDUCTION":
        return f"{source} 경험으로 직무 적합성을 보여드리겠습니다."
    if improvement_type == "LENGTH_EXPANSION":
        return f"{source} 경험을 바탕으로 문제를 구조화하고 실행 가능한 개선안을 만들며, 그 과정에서 얻은 역량을 지원 직무에 연결하겠습니다."
    return f"{original.rstrip()} 이 경험을 지원 직무와 더 직접적으로 연결해 설명하겠습니다."
