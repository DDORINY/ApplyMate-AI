# Codex 요청 예시

## 기능 구현 요청

```text
AGENTS.md와 관련 docs를 먼저 확인해 주세요.

이번 작업은 ApplyMate AI v0.1.2 커리어 프로필 구현입니다.

브랜치:
feature/v0.1.2-career-profile

범위:
- Backend 커리어 프로필 API
- SQLAlchemy 모델과 Alembic migration
- Frontend 프로필 입력 화면
- 관련 테스트
- 문서 갱신

제외:
- AI 분석
- 채용공고 등록
- Google Calendar 연동

검증:
- backend pytest
- backend ruff
- frontend lint
- frontend type-check
- frontend build
- docker compose config
```

## 버그 수정 요청

```text
로그인 후 /me 접근 시 Access Token 재발급이 반복되는 문제를 확인해 주세요.

요구사항:
- 원인을 먼저 설명
- 필요한 최소 범위만 수정
- 관련 테스트 추가
- 검증 결과 보고
```

## 문서 수정 요청

```text
docs/04_api/api-specification.md와 docs/04_api/error-codes.md를 현재 코드 기준으로 맞춰 주세요.

코드 변경은 하지 말고 문서만 수정해 주세요.
```

## 리뷰 요청

```text
현재 PR 변경사항을 리뷰해 주세요.

우선순위:
- 보안 취약점
- API 계약 불일치
- DB migration 위험
- 테스트 누락

수정은 하지 말고 findings만 정리해 주세요.
```
