# Feature Status Matrix

## 2026-07-20 latest status summary

| Area | Feature | Implementation | Current environment status |
| --- | --- | --- | --- |
| Release | v0.5.1 Gmail recruitment email analysis | Done, merged, tagged `v0.5.1` | Mock flow verified; real Gmail is not connected in current `.env`. |
| Planning | v0.6.0 daily job recommendations | Branch and plan created | `feature/v0.6.0-job-recommendations` is active. |
| AI | AI provider abstraction | Done | Current `.env` uses `AI_PROVIDER=mock`; real OpenAI is not connected. |
| Calendar | Google Calendar integration foundation | Done | `CALENDAR_PROVIDER=google` and credentials exist; live Google API verification remains. |
| Infrastructure | Docker Compose backend/PostgreSQL/Redis | Done | Clean Compose project connects; default local PostgreSQL volume has password mismatch. |

Detailed environment notes: [Environment Connection Status](environment-connection-status.md)

문서 기준일: 2026-07-20
현재 릴리스: `v0.5.1`

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
| 추천 | 일일 맞춤 채용공고 추천 | 예정 | v0.6.0 | 추천 규칙/피드백 기반 |
| Release | MVP 안정화, E2E, 운영 문서, v1.0.0 태그 | 예정 | v1.0.0 | 운영 검증 필요 |

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
| 브라우저 E2E 자동화 | 예정 | v0.9.0 이후 강화 |
