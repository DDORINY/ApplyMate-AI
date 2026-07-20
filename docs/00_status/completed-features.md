# Completed Features

## 완료 버전

| 버전 | 완료 기능 |
| --- | --- |
| v0.1.0 | 프로젝트 기반, Docker Compose, Health API |
| v0.1.1 | 회원가입, 로그인, JWT/Refresh Token 인증 |
| v0.1.2 | 커리어 프로필, 경력, 프로젝트, 기술, 희망 조건 |
| v0.1.3 | Google/GitHub OAuth 로그인과 계정 연결 |
| v0.1.4 | 이메일 인증, 비밀번호 복구, 비밀번호 변경, 세션 관리, 보안 이벤트 |
| v0.2.0 | 채용공고 등록/목록/상세/수정/삭제, URL 기반 등록 |
| v0.2.1 | AI 채용공고 분석과 분석 이력 |
| v0.2.2 | 사용자-공고 적합도 분석과 피드백 |
| v0.3.0 | 이력서 메타데이터, PDF/DOCX 업로드, 다운로드, 삭제 |
| v0.3.1 | 이력서 텍스트 추출, 사용자 편집, 재추출 이력 |
| v0.3.2 | AI 이력서 구조화 분석, 후보 데이터, 실행 이력 |
| v0.3.3 | 맞춤 지원 문서 생성, 버전 관리, 출처 조회, 실행 이력 |
| v0.4.0 | 지원 현황 CRUD, 상태 변경 이력, 지원 메모, 제출 문서 버전 고정 |
| v0.4.1 | 일정 CRUD, 상태/신뢰도, 알림 저장, 충돌 표시, 예정 일정, 변경 이력 |
| v0.4.2 | 지원/일정/마감/AI 분석/문서/활동을 모으는 읽기 전용 대시보드 |
| v0.5.0 | Google Calendar 전용 OAuth, token 암호화, Calendar 선택, mock 동기화, mapping/run/error 기록 |
| v0.5.1 | Gmail 전용 OAuth, 읽기 전용 메일 조회, 후보 생성, 사용자 승인 기반 상태/일정 반영 |
| v0.6.0 | 저장된 채용공고 기반 규칙 추천, 추천 점수/이유/부족 조건, 사용자 피드백 |
| v0.6.1 | 추천 실행 설정, run-if-due, Snapshot, 변화 판정, 알림 후보, 추천 UX 개선 |
| v0.7.0 | AI 지원 문서 개선 루프, 문장별 제안, 승인 기반 새 버전 생성 |
| v0.8.0 | In-app 알림, 알림 설정, 리마인더 worker, mock email delivery |
| v0.9.0 | Request ID, 보안 헤더, CORS, rate limit, live/ready health, audit logs, E2E smoke |
| v1.0.0 | MVP 릴리스 문서, 사용자/운영 가이드, E2E 확장, demo seed, release checklist |

## v0.4.2 완료 상세

- `GET /api/v1/dashboard` 추가
- 지원 상태를 백엔드 그룹 기준으로 집계
- 기본 기간 `30d`, 기간 옵션 `7d|30d|90d|all`, 사용자 지정 `start_date/end_date` 지원
- 시간대 기본값 `Asia/Seoul`
- 오늘 일정, 이번 주 일정, 다가오는 일정 마감, 마감 임박 공고 조회
- 준비 중인 지원 항목, 최근 공고 분석, 최근 적합도 분석, 최근 이력서 분석, 최근 지원 문서 조회
- 최근 활동 피드 구성
- `/dashboard` 프론트 화면 추가
- 헤더 주요 네비게이션에 대시보드 추가, 로그인/회원가입/계정 관리는 오른쪽 계정 네비게이션 유지

## v0.5.0 완료 상세

- `GET /api/v1/integrations/calendar/status`
- `POST /api/v1/integrations/calendar/connect`
- `GET /api/v1/integrations/calendar/callback`
- `GET /api/v1/integrations/calendar/calendars`
- `PATCH /api/v1/integrations/calendar/settings`
- `DELETE /api/v1/integrations/calendar/connection`
- `POST /api/v1/integrations/calendar/sync`
- `GET /api/v1/integrations/calendar/sync-runs`
- `GET /api/v1/integrations/calendar/errors`
- `POST /api/v1/calendar/events/{eventId}/sync`
- `GET /api/v1/calendar/events/{eventId}/sync-status`
- `/settings/integrations` 프론트 화면
- 신규 migration `20260719_2100`

## v0.5.1 완료 상세

- Gmail OAuth와 로그인/Calendar OAuth 분리
- `gmail.readonly` scope만 사용
- Mock Gmail Provider로 지원 접수, 면접, 불합격, 일정 변경 메일 검증
- 동일 메일 중복 저장 차단
- 후보 evidence 저장
- 후보 승인 transaction으로 지원 상태 변경과 일정 생성 처리
- 신규 migration `20260719_2200`

## v0.6.0 완료 상세

- 저장된 채용공고만 추천 후보로 사용
- 외부 크롤링, AI/ML 호출 없이 `RULE_BASED` 정책으로 점수 계산
- 커리어 프로필, 기술, 경력, 프로젝트, 희망 조건 기반 추천 점수/등급 산출
- 추천 이유와 부족 조건을 구조화해 저장
- 추천 실행 이력, 정책 버전, 입력 snapshot/hash 저장
- 사용자 피드백으로 관심/숨김/비관심을 기록하고 숨긴 공고는 재추천에서 제외
- `/recommendations` 목록 화면과 `/recommendations/{recommendationId}` 상세 화면 추가
- 대시보드에서 상위 추천 공고 카드 표시
- 신규 migration `20260719_2300`

## v0.6.1 완료 상세

- 사용자별 추천 실행 설정 추가
- 스케줄러가 호출 가능한 `run-if-due` API 추가
- 수동 추천 생성과 run-if-due 실행 시 Snapshot 저장
- Snapshot item에 신규/점수 상승/점수 하락/등급 변화/outdated 판정 저장
- 추천 알림 후보 저장, 읽음/해제 처리
- 추천 목록에 변화/피드백/최소 점수 필터와 변화 배지 추가
- `/recommendations/history` 추천 이력 화면 추가
- `/settings/recommendations` 추천 설정 화면 추가
- 신규 migration `20260720_0000`

## v0.7.0 완료 상세

- 기존 지원 문서 최신/선택 버전을 기준으로 AI 개선 실행 생성
- 개선 유형 `CLARITY`, `CONCISENESS`, `PROFESSIONAL_TONE`, `JOB_ALIGNMENT`, `COMPANY_ALIGNMENT`, `SKILL_EMPHASIS`, `EXPERIENCE_EMPHASIS`, `PROJECT_EMPHASIS`, `ACHIEVEMENT_EMPHASIS`, `STRUCTURE`, `GRAMMAR`, `LENGTH_REDUCTION`, `LENGTH_EXPANSION`, `CUSTOM` 지원
- 문장별 원문/개선안, 변경 유형, 근거, 위험도, 선택 상태 저장
- 승인 전 기존 문서 버전을 변경하지 않고, 적용 시 새 `application_document_versions` 생성
- 기준 버전보다 최신 문서가 있으면 적용 차단 및 outdated 표시
- 개선 실행 source/action 이력 저장
- `/documents/{documentId}/improve` 개선 요청 화면 추가
- `/documents/{documentId}/improvements/{runId}` before/after 비교와 제안 승인 화면 추가
- 신규 migration `20260720_0100`

## v0.8.0 완료 상세

- 사용자별 `notification_settings` 추가
- `notifications`, `notification_deliveries`, `notification_processing_runs` 추가
- 일정 리마인더 due 처리와 중복 방지
- 추천 알림 후보, Gmail 후보, 문서 개선 결과, 동기화 실패 알림 연결
- 알림 목록, 읽지 않은 개수, 읽음/전체 읽음/해제/보관 API 추가
- Email delivery mock provider와 retry 구조 추가
- `/notifications` 알림 센터 화면 추가
- `/settings/notifications` 알림 설정 화면 추가
- 신규 migration `20260720_0200`

## v0.9.0 완료 상세

- Request ID middleware 추가
- 공통 오류 응답에 `request_id` 추가
- 보안 헤더 middleware 추가
- CORS 허용 origin을 `CORS_ALLOWED_ORIGINS`로 분리
- 주요 민감 API rate limit과 429 응답 header 추가
- `/api/v1/health/live`, `/api/v1/health/ready` 추가
- 운영 필수 환경변수 readiness 검증 추가
- `audit_logs` 테이블과 감사 로그 서비스 추가
- 알림 설정 변경과 notification delivery retry 감사 기록
- Playwright E2E smoke test 추가
- E2E/성능/배포/백업 가이드 추가
- 신규 migration `20260720_0300`

## v1.0.0 완료 상세

- MVP 확정 범위와 제외 범위 문서화
- 사용자 가이드와 운영자 가이드 추가
- Known Limitations 문서 추가
- v1.0.0 security review와 release checklist 추가
- v1.0.0 릴리스 노트 추가
- Playwright E2E smoke를 MVP 주요 화면 10개 이상으로 확장
- demo seed payload 생성기 추가
- release smoke/performance smoke script 추가
- E2E 전용 Compose override와 Nginx reverse proxy 예시 추가
- GitHub Actions CI 초안 추가
