# Feature Status Matrix

## 2026-07-20 latest status summary

| Area | Feature | Implementation | Current environment status |
| --- | --- | --- | --- |
| Release | v0.9.0 stability hardening | Done locally | Request ID, security headers, rate limit, health ready/live, audit logs, E2E smoke verified locally. |
| Release | v0.8.0 notification operations | Done, merged, tagged `v0.8.0` | In-app notifications, settings, due reminders, mock email delivery verified locally. |
| Release | v0.7.0 AI document improvement loop | Done locally | Improvement run, sentence suggestions, approval-based versioning verified locally with mock AI. |
| Release | v0.6.1 recommendation automation foundation | Done locally | Settings, run-if-due, snapshots, changes, notification candidates verified locally. |
| Release | v0.6.0 rule-based job recommendations | Done, merged, tagged `v0.6.0` | Saved-job-only rule-based flow verified. |
| Release | v0.5.1 Gmail recruitment email analysis | Done, merged, tagged `v0.5.1` | Mock flow verified; real Gmail is not connected in current `.env`. |
| AI | AI provider abstraction | Done | Current `.env` uses `AI_PROVIDER=mock`; real OpenAI is not connected. |
| Calendar | Google Calendar integration foundation | Done | `CALENDAR_PROVIDER=google` and credentials exist; live Google API verification remains. |
| Infrastructure | Docker Compose backend/PostgreSQL/Redis | Done | Clean Compose project connects; default local PostgreSQL volume has password mismatch. |

Detailed environment notes: [Environment Connection Status](environment-connection-status.md)

문서 기준일: 2026-07-20
현재 릴리스: `v0.9.0`

## 버전별 기능 상태

| 영역 | 기능 | 상태 | 버전 | 검증/비고 |
| --- | --- | --- | --- | --- |
| Foundation | 프로젝트 기반, Docker Compose, Health API | 완료 | v0.1.0 | 기본 구조 |
| 인증 | 이메일 회원가입, 로그인, JWT, Refresh Token | 완료 | v0.1.1 | backend tests |
| 프로필 | 커리어 프로필, 경력, 프로젝트, 기술, 희망 조건 | 완료 | v0.1.2 | backend/frontend 검증 |
| 인증 | Google/GitHub OAuth 로그인 및 계정 연결 | 완료 | v0.1.3 | mock/local 검증 |
| 계정 보안 | 이메일 인증, 비밀번호 복구, 세션 관리, 보안 이벤트 | 완료 | v0.1.4 | backend tests |
| 채용공고 | 공고 등록/목록/상세/수정/삭제, URL 등록 | 완료 | v0.2.0 | backend/frontend 검증 |
| AI | AI 채용공고 분석 | 완료 | v0.2.1 | mock provider 검증 |
| AI | 사용자-공고 적합도 분석 | 완료 | v0.2.2 | backend tests |
| 이력서 | PDF/DOCX 업로드, 다운로드, 삭제 | 완료 | v0.3.0 | 파일 정책 검증 |
| 이력서 | 이력서 텍스트 추출, 사용자 편집, 재추출 이력 | 완료 | v0.3.1 | backend/frontend 검증 |
| AI | AI 이력서 구조화 분석, 후보 데이터, 실행 이력 | 완료 | v0.3.2 | mock provider 검증 |
| 지원 문서 | 근거 기반 지원 문서 생성, 버전, 출처, 실행 이력 | 완료 | v0.3.3 | backend tests, frontend build |
| 지원 현황 | 지원 항목 CRUD, 상태 이력, 메모, 문서 버전 고정 | 완료 | v0.4.0 | backend tests, frontend build |
| 일정 | 일정 CRUD, 알림 저장, 충돌 표시, 예정 일정, 변경 이력 | 완료 | v0.4.1 | backend tests, frontend lint/type-check/build |
| 대시보드 | 지원/일정/마감/AI/문서/활동 요약 화면 | 완료 | v0.4.2 | backend tests, frontend type-check |
| 연동 | Google Calendar OAuth, Calendar 선택, mock 동기화, mapping/run/error | 완료 | v0.5.0 | mock provider 검증, 실제 Google은 NEEDS_VERIFICATION |
| 연동 | Gmail 채용 메일 분석, 후보 생성, 사용자 승인 반영 | 완료 | v0.5.1 | mock provider 검증, 실제 Gmail은 NEEDS_VERIFICATION |
| 추천 | 저장된 채용공고 기반 규칙 추천 | 완료 | v0.6.0 | RULE_BASED 점수/등급/이유/피드백 |
| 추천 | 추천 실행 설정, Snapshot, 변화 판정, 알림 후보 | 완료 | v0.6.1 | 실제 알림 발송/외부 수집 제외 |
| 지원 문서 | AI 지원 문서 개선 루프, 문장별 제안, 승인 기반 새 버전 생성 | 완료 | v0.7.0 | backend tests, frontend lint/type-check/build |
| 알림 | In-app 알림, 사용자 설정, worker, mock email delivery | 완료 | v0.8.0 | backend tests, frontend lint/type-check/build |
| 안정화 | Request ID, 보안 헤더, rate limit, live/ready health, audit logs, E2E smoke | 완료 | v0.9.0 | backend tests 171 passed, Playwright E2E 3 passed |
| Release | MVP 릴리스, 인수 테스트, 운영 검증, v1.0.0 태그 | 예정 | v1.0.0 | 운영 검증 필요 |

## v0.8.0 세부 상태

| 기능 | 상태 | 검증 |
| --- | --- | --- |
| `GET /api/v1/notifications` | 완료 | `backend/tests/test_notifications.py` |
| `GET /api/v1/notifications/unread-count` | 완료 | unread count 테스트 |
| `PATCH /api/v1/notifications/{notificationId}/read` | 완료 | 읽음 처리 테스트 |
| `PATCH /api/v1/notifications/{notificationId}/dismiss` | 완료 | 해제 처리 테스트 |
| `PATCH /api/v1/notifications/{notificationId}/archive` | 완료 | 보관 처리 테스트 |
| `POST /api/v1/notifications/run-due` | 완료 | due reminder/idempotency 테스트 |
| `GET/PATCH /api/v1/notification-settings` | 완료 | 기본값/수정/invalid timezone 테스트 |
| `GET /api/v1/notification-deliveries` | 완료 | mock email delivery 테스트 |
| `/notifications` | 완료 | frontend lint/type-check/build |
| `/settings/notifications` | 완료 | frontend lint/type-check/build |

## v0.9.0 세부 상태

| 기능 | 상태 | 검증 |
| --- | --- | --- |
| Request ID middleware | 완료 | `backend/tests/test_health.py` |
| 공통 오류 응답 `request_id` | 완료 | unknown path 테스트 |
| 보안 헤더 | 완료 | `X-Content-Type-Options`, `X-Frame-Options` 테스트 |
| CORS origin 설정 | 완료 | preflight 테스트 |
| 주요 API rate limit | 완료 | 429/header 테스트 |
| `/health/live`, `/health/ready` | 완료 | health 테스트 |
| `audit_logs` | 완료 | 알림 설정 변경 감사 로그 테스트 |
| Playwright E2E smoke | 완료 | 3 passed |

## v0.7.0 세부 상태

| 기능 | 상태 | 검증 |
| --- | --- | --- |
| `POST /api/v1/documents/{documentId}/improvements` | 완료 | `backend/tests/test_document_improvements.py` |
| `GET /api/v1/documents/{documentId}/improvements` | 완료 | 목록 응답/소유권 검증 |
| `GET /api/v1/documents/{documentId}/improvements/{runId}` | 완료 | 상세 응답/소유권 검증 |
| `POST /api/v1/documents/{documentId}/improvements/{runId}/retry` | 완료 | 적용 완료 실행 재시도 차단 |
| `PATCH /api/v1/documents/{documentId}/improvements/{runId}/suggestions/{suggestionId}` | 완료 | 승인/거절 상태 변경 검증 |
| `POST /api/v1/documents/{documentId}/improvements/{runId}/apply` | 완료 | 승인 시 새 문서 버전 생성 |
| `POST /api/v1/documents/{documentId}/improvements/{runId}/reject` | 완료 | 실행 거절 기록 |
| `/documents/{documentId}/improve` | 완료 | frontend lint/type-check/build |
| `/documents/{documentId}/improvements/{runId}` | 완료 | frontend lint/type-check/build |

## v0.6.1 세부 상태

| 기능 | 상태 | 검증 |
| --- | --- | --- |
| `GET/PATCH /api/v1/recommendations/settings` | 완료 | `backend/tests/test_job_recommendation_automation.py` |
| `POST /api/v1/recommendations/jobs/run-if-due` | 완료 | 실행/skip reason 테스트 |
| 추천 Snapshot 저장 | 완료 | 최초 실행/신규 추천 테스트 |
| 추천 변화 응답 | 완료 | 목록 응답 `latest_change_type` 테스트 |
| 추천 알림 후보 | 완료 | 목록/소유권 테스트 |
| `/recommendations/history` | 완료 | frontend lint/type-check/build |
| `/settings/recommendations` | 완료 | frontend lint/type-check/build |
| 대시보드 Snapshot 요약 | 완료 | frontend lint/type-check/build |

## v0.6.0 세부 상태

| 기능 | 상태 | 검증 |
| --- | --- | --- |
| `POST /api/v1/recommendations/jobs/generate` | 완료 | `backend/tests/test_job_recommendations.py` |
| `GET /api/v1/recommendations/jobs` | 완료 | 목록/필터 테스트 |
| `GET /api/v1/recommendations/jobs/{recommendationId}` | 완료 | 소유권 테스트 |
| 추천 정책 메타데이터 | 완료 | `RULE_BASED`, 정책 버전 응답 |
| 추천 피드백 | 완료 | 숨김 후 재추천 제외 테스트 |
| `/recommendations` 목록 화면 | 완료 | frontend lint/type-check/build |
| `/recommendations/{recommendationId}` 상세 화면 | 완료 | frontend lint/type-check/build |
| 대시보드 상위 추천 카드 | 완료 | frontend lint/type-check/build |

## v0.4.2 세부 상태

| 기능 | 상태 | 검증 |
| --- | --- | --- |
| `GET /api/v1/dashboard` | 완료 | `backend/tests/test_dashboard.py` |
| 지원 상태 그룹 집계 | 완료 | 상태 그룹/아카이브 제외 테스트 |
| 기간 필터 `7d/30d/90d/all` | 완료 | 기본/전체/사용자 지정 날짜 테스트 |
| 사용자 지정 날짜 `start_date/end_date` | 완료 | 날짜 범위 오류 테스트 |
| 시간대 처리 | 완료 | `Asia/Seoul`, invalid timezone 테스트 |
| 오늘/이번 주 일정 | 완료 | 일정 조회 테스트 |
| 취소/아카이브 일정 제외 | 완료 | 취소 일정 제외 테스트 |
| 일정 마감/공고 마감 | 완료 | 7일 이내 마감 테스트 |
| 최근 AI 분석/적합도/문서/활동 | 완료 | recent limit/소유권 테스트 |
| `/dashboard` 화면 | 완료 | frontend type-check |
| 헤더 네비게이션 | 완료 | 주요 네비와 계정 네비 분리 |

## 미검증 또는 운영 확인 필요

| 항목 | 상태 | 이유 |
| --- | --- | --- |
| 실제 OpenAI 호출 | NEEDS_VERIFICATION | API key/model 필요, 비용 발생 가능 |
| 운영 Google/GitHub OAuth | NEEDS_VERIFICATION | 운영 client/secret/redirect URI 필요 |
| Google Calendar 실제 일정 생성 | NEEDS_VERIFICATION | 운영 Google credentials 필요 |
| Gmail 실제 메일 조회/분석 | NEEDS_VERIFICATION | 운영 Google Gmail API credentials 필요 |
| 이메일/푸시 알림 실제 발송 | 예정 | 현재는 알림 저장 중심 |
| 운영 SMTP | NEEDS_VERIFICATION | 운영 SMTP 계정 필요 |
| 실제 운영 부하 테스트 | NEEDS_VERIFICATION | 로컬 smoke 기준만 문서화 |
| `pip-audit` | NEEDS_VERIFICATION | 현재 로컬에 미설치 |
| npm audit moderate 2건 | NEEDS_REVIEW | Next 내부 PostCSS advisory, 자동 fix가 major downgrade 제안 |
