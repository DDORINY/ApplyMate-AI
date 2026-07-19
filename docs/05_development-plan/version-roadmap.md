# Version Roadmap

## 2026-07-20 현재 상태

- 최신 완료 버전: `v0.5.1`
- 현재 작업 브랜치: `feature/v0.6.0-job-recommendations`
- 다음 개발 버전: `v0.6.0`
- 현재 migration head: `20260719_2200`
- `v0.5.1`은 `main` 병합 및 `v0.5.1` 태그 push가 완료되었다.
- `v0.6.0`은 일일 맞춤 채용공고 추천 기반 구현 단계이며, 계획 문서는 `docs/05_development-plan/releases/v0.6.0-plan.md`를 기준으로 한다.

## Environment connection note

- Gmail is not connected with current `.env` because `GMAIL_PROVIDER` is empty and Gmail OAuth credentials are missing.
- OpenAI is not connected because `AI_PROVIDER=mock` and OpenAI key/model values are empty.
- Google Calendar credentials are present, but live Google Calendar API behavior remains `NEEDS_VERIFICATION`.
- Default Docker PostgreSQL can fail if an existing local named volume was initialized with a different password than the current `.env`.
- Details: `docs/00_status/environment-connection-status.md`

## Roadmap

| 버전 | 목표 | 상태 |
| --- | --- | --- |
| v0.1.0 | 프로젝트 기반, Docker Compose, Health API | 완료 |
| v0.1.1 | 회원 및 인증 | 완료 |
| v0.1.2 | 커리어 프로필 | 완료 |
| v0.1.3 | 소셜 로그인과 계정 연결 | 완료 |
| v0.1.4 | 계정 보안과 복구 | 완료 |
| v0.2.0 | 채용공고 관리 | 완료 |
| v0.2.1 | AI 채용공고 분석 | 완료 |
| v0.2.2 | 사용자-공고 적합도 분석 | 완료 |
| v0.3.0 | 이력서 파일 관리 | 완료 |
| v0.3.1 | 이력서 텍스트 추출 | 완료 |
| v0.3.2 | AI 이력서 구조화 분석 | 완료 |
| v0.3.3 | 맞춤 지원 문서 생성 | 완료 |
| v0.4.0 | 지원 현황 관리 | 완료 |
| v0.4.1 | 일정 관리 | 완료 |
| v0.4.2 | 대시보드 | 완료 |
| v0.5.0 | Google Calendar 연동 | 완료 |
| v0.5.1 | Gmail 채용 메일 분석 기반 | 완료 |
| v0.6.0 | 일일 맞춤 채용공고 추천 | 진행 중 |
| v0.7.0 | AI 자기소개서 개선 루프 | 예정 |
| v0.8.0 | 알림/리마인더 운영화 | 예정 |
| v0.9.0 | E2E/성능/보안 안정화 | 예정 |
| v1.0.0 | MVP 릴리스 | 예정 |

## v0.5.1 방향

- Gmail OAuth scope는 사용자가 명시적으로 승인할 때만 요청한다.
- 채용 관련 메일 후보를 추출하되 사용자의 확인 없이 지원 상태나 일정을 변경하지 않는다.
- 면접/과제/결과 일정 후보를 생성하고 사용자가 승인한 뒤 내부 일정에 반영한다.
- 실제 Gmail API 호출은 운영 credentials가 준비된 뒤 `NEEDS_VERIFICATION`으로 검증한다.
