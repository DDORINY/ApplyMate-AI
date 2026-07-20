# Version Roadmap

## 2026-07-20 현재 상태

- 최신 완료 버전: `v0.7.0`
- 현재 작업 브랜치: `feature/v0.7.0-document-improvement`
- 다음 개발 버전: `v0.8.0`
- 현재 migration head: `20260720_0100`
- `v0.5.1`은 `main` 병합 및 `v0.5.1` 태그 push가 완료되었다.
- `v0.6.0`은 저장된 공고 기반 규칙 추천으로 완료되었다.
- `v0.7.0`은 AI 지원 문서 개선 루프 구현 단계이며, 계획 문서는 `docs/05_development-plan/releases/v0.7.0-plan.md`를 기준으로 한다.

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
| v0.6.0 | 저장된 채용공고 기반 규칙 추천 | 완료 |
| v0.6.1 | 추천 UX 개선과 추천 실행 자동화 기반 | 완료 |
| v0.7.0 | AI 지원 문서 개선 루프 | 완료 |
| v0.8.0 | 알림/리마인더 운영화 | 예정 |
| v0.9.0 | E2E/성능/보안 안정화 | 예정 |
| v1.0.0 | MVP 릴리스 | 예정 |

## v0.6.0 완료 방향

- 추천 후보는 사용자가 저장한 채용공고만 사용한다.
- 추천 계산은 AI/ML 호출 없이 `RULE_BASED` 정책으로 수행한다.
- 추천 결과는 점수뿐 아니라 추천 이유, 부족 조건, 정책 버전, 입력 snapshot을 함께 저장한다.
- 사용자가 숨긴 공고는 기본 재추천에서 제외한다.
- 대시보드와 공고 상세에서 추천 화면으로 이동할 수 있게 한다.

## v0.7.0 완료 방향

- 기존 지원 문서 생성 기능을 확장해 개선 실행, 문장별 제안, source/action 이력을 저장한다.
- 사용자가 승인하기 전까지 기존 문서 버전을 변경하지 않는다.
- 승인 시 새 문서 버전을 생성하고 적용 이력을 연결한다.
- 근거 없는 사실 생성과 prompt injection을 방어한다.

## v0.8.0 예정 방향

- 알림/리마인더 운영화를 진행한다.
- 추천 알림 후보와 일정/지원 상태 이벤트를 사용자 알림 UX로 연결한다.
- 실제 이메일/푸시 발송 여부는 운영 정책과 사용자 설정을 기준으로 결정한다.
