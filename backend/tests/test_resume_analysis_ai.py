import pytest

from app.ai.providers import DisabledAIProvider, MockAIProvider
from app.ai.resume_analysis_prompt import SYSTEM_PROMPT, build_user_prompt
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.schemas.resume_analysis import ResumeAnalysisStructuredData


@pytest.mark.anyio
async def test_mock_provider_analyzes_resume_text() -> None:
    settings = get_settings()
    prompt = build_user_prompt(
        "Backend Engineer\nPython, FastAPI, PostgreSQL, Docker 기반 API 개발",
        settings,
    )

    result = await MockAIProvider().analyze_resume(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=prompt,
        response_schema=ResumeAnalysisStructuredData,
    )

    assert result.provider == "mock"
    assert result.model == "mock-resume-analyzer"
    assert result.parsed_data.summary
    assert {skill.name for skill in result.parsed_data.skills} >= {
        "Python",
        "FastAPI",
        "PostgreSQL",
        "Docker",
    }
    assert result.parsed_data.warnings[0].code == "MOCK_PROVIDER"


@pytest.mark.anyio
async def test_disabled_provider_rejects_resume_analysis() -> None:
    with pytest.raises(AppError) as exc_info:
        await DisabledAIProvider().analyze_resume(
            system_prompt=SYSTEM_PROMPT,
            user_prompt="resume text",
            response_schema=ResumeAnalysisStructuredData,
        )

    assert exc_info.value.code == "AI_PROVIDER_DISABLED"
