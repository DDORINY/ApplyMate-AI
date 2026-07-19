# Current Project Status

## 현재 버전

- 버전: `v0.4.0`
- migration head: `20260719_1900`
- AI provider 검증 기준: `AI_PROVIDER=mock`

## 구현 완료 기능

- 프로젝트 기반, Docker Compose, Health API
- 회원가입/로그인/JWT/Refresh Token
- 이메일 인증, 비밀번호 복구, 세션 관리
- Google/GitHub OAuth 로그인 및 계정 연결 구조
- 커리어 프로필 관리
- 채용공고 등록/관리
- AI 채용공고 분석
- 사용자-공고 적합도 분석
- 이력서 PDF/DOCX 업로드 및 파일 관리
- 이력서 텍스트 추출 및 사용자 수정
- AI 이력서 구조화 분석
- 맞춤 지원 문서 생성, 편집, 버전 관리, 근거 조회
- 지원 현황 관리, 상태 이력, 지원 메모, 제출 문서 버전 고정

## 주요 화면

- `/`
- `/signup`
- `/login`
- `/me`
- `/profile`
- `/jobs`
- `/jobs/new`
- `/jobs/{jobId}`
- `/resumes`
- `/resumes/new`
- `/resumes/{resumeId}`
- `/documents`
- `/documents/new`
- `/documents/{documentId}`
- `/applications`
- `/applications/new`
- `/applications/{applicationId}`
- `/settings/accounts`
- `/settings/security`

## 현재 DB

최신 migration: `20260719_1900_create_application_tracking_tables.py`

신규 v0.4.0 테이블:

- `applications`
- `application_status_history`
- `application_notes`

## 최근 검증

- Backend ruff: passed
- Backend tests: 128 passed
- Frontend lint: passed
- Frontend type-check: passed
- Frontend build: passed
- Docker compose config: passed
- Alembic upgrade/current/downgrade/re-upgrade: passed

## 미검증

- 실제 OpenAI API 호출
- 실제 Google/GitHub 운영 OAuth
- 운영 SMTP
- 운영 HTTPS Cookie
- 운영 배포
- 브라우저 E2E 자동화
