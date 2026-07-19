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
