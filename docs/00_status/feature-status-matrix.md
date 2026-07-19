# Feature Status Matrix

문서 기준일: 2026-07-19
현재 릴리스: `v0.4.1`
현재 작업 브랜치: `feature/v0.4.1-schedule-management`

## 버전별 기능 상태

| 영역 | 기능 | 상태 | 버전 | 검증 비고 |
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
| 일정 | 일정 CRUD, 상태, 신뢰도, 알림 저장, 충돌, 임박 일정, 변경 이력 | 완료 | v0.4.1 | backend tests, frontend lint/type-check/build |
| 대시보드 | 지원·일정·분석 요약 화면 | 예정 | v0.4.2 | v0.4.1 이후 |
| 연동 | Google Calendar 연동 기반 | 예정 | v0.5.0 | 사용자 명시 승인 필요 |
| 연동 | Gmail 채용 메일 분석 기반 | 예정 | v0.5.1 | 실제 메일 변경/발송 금지 |
| 추천 | 일일 맞춤 채용공고 추천 | 예정 | v0.6.0 | 추천 규칙/피드백 기반 |
| Release | MVP 안정화, E2E, 운영 문서, v1.0.0 태그 | 예정 | v1.0.0 | 운영 검증 필요 |

## v0.4.1 내부 상태

| 기능 | 상태 | 검증 |
| --- | --- | --- |
| 일정 이벤트 API | 완료 | `backend/tests/test_schedule.py` |
| 일정 생성/목록/상세/수정/보관 | 완료 | backend tests |
| 지원 항목·채용공고 연결 검증 | 완료 | backend tests |
| 일정 상태 변경과 중복 완료/취소 방지 | 완료 | backend tests |
| 일정 신뢰도 저장 | 완료 | backend tests |
| 알림 생성/수정/삭제와 중복 방지 | 완료 | backend tests |
| 충돌 감지 | 완료 | backend tests |
| 임박 일정과 지난 일정 계산 | 완료 | backend tests |
| 소유권 검증 | 완료 | backend tests |
| `/calendar` 목록/월간/주간 화면 | 완료 | frontend lint/type-check/build |
| `/calendar/new` 생성 화면 | 완료 | frontend lint/type-check/build |
| `/calendar/events/{eventId}` 상세 화면 | 완료 | frontend lint/type-check/build |
| 지원/공고 상세 일정 진입점 | 완료 | frontend lint/type-check/build |

## 미검증·제외 상태

| 항목 | 상태 | 이유 |
| --- | --- | --- |
| 실제 OpenAI 호출 | NEEDS_VERIFICATION | API key/model 필요, 비용 발생 가능 |
| 운영 Google/GitHub OAuth | NEEDS_VERIFICATION | 운영 client/secret/redirect URI 필요 |
| Google Calendar 실제 일정 생성 | 예정 | v0.5.0 이후 |
| Gmail 실제 메일 분석 | 예정 | v0.5.1 이후 |
| 이메일/푸시 알림 실제 발송 | 예정 | v0.4.1은 알림 저장·표시만 구현 |
| 운영 SMTP | NEEDS_VERIFICATION | 운영 SMTP 계정 필요 |
| 브라우저 E2E 자동화 | 예정 | v0.9.0 안정화 단계에서 강화 |
