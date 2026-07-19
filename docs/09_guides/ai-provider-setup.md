# AI Provider 설정 가이드

v0.2.1은 `disabled`, `mock`, `openai` Provider를 지원합니다.

## 환경변수

```env
AI_PROVIDER=disabled
OPENAI_API_KEY=
OPENAI_MODEL=
AI_REQUEST_TIMEOUT_SECONDS=60
AI_MAX_RETRIES=2
AI_ANALYSIS_MAX_INPUT_CHARS=30000
AI_ANALYSIS_PROMPT_VERSION=v1
AI_ANALYSIS_SCHEMA_VERSION=v1
AI_STORE_RAW_RESPONSE=false
AI_DAILY_ANALYSIS_LIMIT=20
AI_ANALYSIS_COOLDOWN_SECONDS=30
```

## Provider

- `disabled`: 기본값입니다. 분석 요청은 `AI_PROVIDER_DISABLED` 오류를 반환합니다.
- `mock`: 로컬 개발과 자동 테스트용입니다. 외부 네트워크를 호출하지 않습니다.
- `openai`: OpenAI 공식 HTTP API를 사용합니다. `OPENAI_API_KEY`, `OPENAI_MODEL`이 필요합니다.

## 개발 환경 추천

로컬 기능 확인과 테스트는 다음처럼 Mock Provider를 사용합니다.

```env
AI_PROVIDER=mock
AI_ANALYSIS_COOLDOWN_SECONDS=0
```

실제 OpenAI 호출은 API Key가 설정된 환경에서만 선택적으로 수행합니다. API Key는 저장소에 커밋하지 않습니다.
