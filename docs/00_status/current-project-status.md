# Current Project Status

## 현재 버전

- 버전: `v0.4.1`
- 현재 migration head: `20260719_2000`
- 최신 릴리스 범위: 일정 관리
- AI provider 검증 기준: `AI_PROVIDER=mock`

## 구현 완료 기능

- 프로젝트 기반, Docker Compose, Health API
- 회원가입, 로그인, JWT/Refresh Token 인증
- 이메일 인증, 비밀번호 복구, 세션 관리
- Google/GitHub OAuth 로그인 및 계정 연결 구조
- 커리어 프로필, 경력, 프로젝트, 기술, 희망 조건 관리
- 채용공고 등록/관리, URL 기반 등록
- AI 채용공고 분석
- 사용자-공고 적합도 분석
- 이력서 PDF/DOCX 업로드와 파일 관리
- 이력서 텍스트 추출과 사용자 편집
- AI 이력서 구조화 분석
- 근거 기반 지원 문서 생성, 편집, 버전 관리, 출처 조회
- 지원 현황 관리, 상태 변경 이력, 지원 메모, 제출 문서 버전 고정
- 일정 관리, 일정 알림 저장, 충돌 표시, 임박 일정, 변경 이력

## 주요 화면

- `/applications`
- `/applications/new`
- `/applications/{applicationId}`
- `/calendar`
- `/calendar/new`
- `/calendar/events/{eventId}`

## 현재 DB

최신 migration: `20260719_2000_create_schedule_tables.py`

v0.4.1 신규 테이블:

- `schedule_events`
- `schedule_reminders`
- `schedule_event_history`

## 최근 검증

- Backend ruff: passed
- Backend pytest: 135 passed
- Frontend lint: passed
- Frontend type-check: passed
- Frontend build: passed
- Docker compose config: passed
- Alembic upgrade/current/downgrade/re-upgrade/current: passed

## 미검증

- 실제 OpenAI API 호출
- 운영 Google/GitHub OAuth
- 운영 SMTP
- 운영 HTTPS Cookie
- 운영 배포
- 브라우저 E2E 자동화
- 이메일/푸시 알림 실제 발송
- Google Calendar 실제 일정 생성
