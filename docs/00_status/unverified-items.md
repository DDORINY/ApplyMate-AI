# Unverified Items

문서 기준일: 2026-07-20
현재 릴리스: `v1.0.0`

이 문서는 구현은 존재하지만 현재 로컬/mock 환경에서만 확인되었거나, 운영 환경에서 추가 검증이 필요한 항목을 정리한다.

## 운영 검증 필요 항목

| 항목 | 상태 | 이유 |
| --- | --- | --- |
| 실제 OpenAI 호출 | NEEDS_VERIFICATION | 현재 기본 검증은 `AI_PROVIDER=mock` 기준이다. 운영 `OPENAI_API_KEY`, `OPENAI_MODEL`, 비용 한도 설정 후 live smoke가 필요하다. |
| 실제 Google Calendar API | NEEDS_VERIFICATION | Calendar 연동 기반은 구현되어 있으나 운영 OAuth consent, redirect URI, scope, 실제 일정 생성/수정 권한 확인이 필요하다. |
| 실제 Gmail API | NEEDS_VERIFICATION | Gmail 채용 메일 분석 기반은 구현되어 있으나 운영 OAuth scope와 실제 mailbox 읽기 권한 검증이 필요하다. |
| 실제 SMTP 발송 | NEEDS_VERIFICATION | mock email delivery는 검증되었으나 운영 SMTP 계정, 발송 도메인 인증, 발송 제한 정책 확인이 필요하다. |
| 운영 HTTPS/Cookie/SameSite | NEEDS_VERIFICATION | 로컬 smoke는 완료되었으나 운영 도메인과 HTTPS 환경에서 cookie/security header 동작 확인이 필요하다. |
| 운영 DB restore 리허설 | NEEDS_VERIFICATION | backup/restore 절차는 문서화했지만 staging 또는 production-like DB에서 복구 리허설이 필요하다. |
| 운영 배포 | NEEDS_VERIFICATION | Docker Compose/Nginx 예시는 준비되었고 로컬 smoke는 통과했지만 실제 서버 배포는 별도 승인 필요하다. |
| 다중 인스턴스 worker/rate limit | NEEDS_VERIFICATION | 단일 worker와 로컬 rate limit은 검증되었으나 분산 lock/분산 rate limit은 운영 구조에서 추가 검증 필요하다. |

## MVP 제외 항목

| 항목 | 상태 | 이유 |
| --- | --- | --- |
| 외부 채용 사이트 자동 크롤링 | EXCLUDED | 약관, robots, 수집 정책 검토 전까지 기본 기능에서 제외한다. |
| 자동 지원서 제출 | EXCLUDED | 사용자 명시 승인, 외부 사이트 정책, 법적 검토가 필요하다. |
| Push 알림 provider | NOT_IMPLEMENTED | v1.0.0은 in-app 알림과 mock email delivery 중심이다. |
| 네이티브 모바일 앱 | EXCLUDED | 웹 MVP 범위 외다. |
| 운영 자동 확장 | EXCLUDED | MVP 이후 인프라 단계에서 검토한다. |

## v1.0.0에서 검증 완료된 항목

| 항목 | 결과 |
| --- | --- |
| Backend test | 171 passed |
| Frontend lint/type-check/build | PASS |
| Playwright E2E | 15 passed |
| Docker Compose config | PASS |
| Migration upgrade/downgrade/upgrade | PASS, head `20260720_0300` |
| Worker dry run | PASS |
| Smoke test | live/ready/openapi 200 |
| Performance smoke | 15 requests, concurrency 3, errors 0 |
| npm audit | vulnerabilities 0 |
| pip-audit | 프로젝트 전용 임시 venv 기준 known vulnerabilities 0 |
| Secret scan | 저장소 추적 대상 기준 매칭 없음 |
