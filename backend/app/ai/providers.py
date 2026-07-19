import json
import time
from dataclasses import dataclass
from typing import Protocol

import httpx
from pydantic import BaseModel, ValidationError

from app.core.config import Settings
from app.core.exceptions import AppError
from app.schemas.job_analysis import JobAnalysisStructuredData


@dataclass(frozen=True)
class AIProviderResult:
    parsed_data: JobAnalysisStructuredData
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


class DisabledAIProvider:
    provider = "disabled"
    model = None

    async def analyze_job(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_schema: type[BaseModel],
    ) -> AIProviderResult:
        raise AppError("AI_PROVIDER_DISABLED", "AI 분석 Provider가 비활성화되어 있습니다.", 503)


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
        started = time.perf_counter()
        skills = [
            skill
            for skill in ["Python", "FastAPI", "SQLAlchemy", "PostgreSQL", "Docker", "TypeScript"]
            if skill.lower() in user_prompt.lower()
        ] or ["분석 필요"]
        data = JobAnalysisStructuredData(
            summary="저장된 채용공고 내용을 기반으로 핵심 업무, 자격요건, 기술스택을 구조화했습니다.",
            position={
                "title": _line_after(user_prompt, "공고 제목") or None,
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
            education={
                "minimum_level": "UNKNOWN",
                "description": _line_after(user_prompt, "학력 조건") or None,
            },
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
            deadline={
                "type": _line_after(user_prompt, "마감 유형") or "UNKNOWN",
                "date": None,
                "description": _line_after(user_prompt, "마감일") or None,
            },
            company_values=[],
            keywords=skills,
            warnings=[
                {
                    "code": "MOCK_PROVIDER",
                    "message": "Mock Provider 결과이며 실제 AI 호출 없이 생성되었습니다.",
                }
            ],
            confidence={
                "overall": 0.72,
                "responsibilities": 0.7,
                "qualifications": 0.7,
                "skills": 0.75,
                "deadline": 0.5,
            },
        )
        return AIProviderResult(
            parsed_data=data,
            provider=self.provider,
            model=self.model,
            request_id="mock-job-analysis",
            prompt_tokens=max(len(user_prompt) // 4, 1),
            completion_tokens=200,
            total_tokens=max(len(user_prompt) // 4, 1) + 200,
            latency_ms=int((time.perf_counter() - started) * 1000),
            raw_response=data.model_dump_json(),
        )


class OpenAIProvider:
    provider = "openai"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.model = settings.openai_model

    async def analyze_job(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_schema: type[BaseModel],
    ) -> AIProviderResult:
        started = time.perf_counter()
        payload = {
            "model": self.settings.openai_model,
            "input": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
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
            raise AppError("AI_PROVIDER_TIMEOUT", "AI 분석 요청 시간이 초과되었습니다.", 504) from exc
        except httpx.HTTPError as exc:
            raise AppError("AI_PROVIDER_REQUEST_FAILED", "AI Provider 요청에 실패했습니다.", 502) from exc
        if response.status_code == 429:
            raise AppError("AI_PROVIDER_RATE_LIMITED", "AI Provider 요청 한도를 초과했습니다.", 429)
        if response.status_code >= 500:
            raise AppError("AI_PROVIDER_UNAVAILABLE", "AI Provider가 일시적으로 응답하지 않습니다.", 502)
        if response.status_code >= 400:
            raise AppError("AI_PROVIDER_REQUEST_FAILED", "AI Provider 요청에 실패했습니다.", 502)

        body = response.json()
        output_text = body.get("output_text") or _extract_output_text(body)
        try:
            parsed = response_schema.model_validate_json(output_text)
        except (ValidationError, ValueError) as exc:
            raise AppError("AI_PROVIDER_INVALID_RESPONSE", "AI Provider 응답 구조가 올바르지 않습니다.", 502) from exc

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
            raise AppError(
                "AI_PROVIDER_CONFIG_INVALID",
                "OpenAI Provider 사용에는 OPENAI_API_KEY와 OPENAI_MODEL이 필요합니다.",
                503,
            )
        return OpenAIProvider(settings)
    raise AppError("AI_PROVIDER_INVALID", "지원하지 않는 AI Provider입니다.", 503)


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
    }


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
