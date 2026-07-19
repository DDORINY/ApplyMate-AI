# Current Project Status

## 현재 버전

- 버전: `v0.3.3`
- migration head: `20260719_1800`
- AI provider 검증 기준: `AI_PROVIDER=mock`

## 구현 완료 기능

- 프로젝트 기반
- 회원가입/로그인/JWT
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
- `/settings/accounts`
- `/settings/security`

## 현재 DB

최신 migration: `20260719_1800_create_application_document_tables.py`

신규 테이블:

- `application_documents`
- `application_document_versions`
- `application_document_sources`
- `generation_runs`

## 최근 검증

- Backend ruff: passed
- Backend tests: 120 passed
- Frontend lint: passed
- Frontend type-check: passed
- Frontend build: passed

## 미검증

- 실제 OpenAI API 호출
- 실제 Google/GitHub 운영 OAuth
- 운영 SMTP
- 운영 HTTPS Cookie
- 운영 배포
- 브라우저 E2E 자동화
