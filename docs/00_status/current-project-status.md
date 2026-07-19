# Current Project Status

## 현재 버전

- 버전: `v0.3.0`
- migration head: `20260719_1500`
- AI provider 검증 기준: `AI_PROVIDER=mock`

## 현재 구현 완료 기능

- 프로젝트 기반
- 회원가입/로그인/JWT
- 이메일 인증/비밀번호 복구/세션 관리
- Google/GitHub OAuth 로그인 및 계정 연결 구조
- 커리어 프로필 관리
- 채용공고 등록/관리
- AI 채용공고 분석
- 사용자-공고 적합도 분석
- 이력서 PDF/DOCX 업로드와 파일 관리

## 현재 주요 화면

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
- `/settings/accounts`
- `/settings/security`

## 현재 DB

- 최신 migration: `20260719_1500_create_resume_upload_tables.py`
- 신규 테이블: `resumes`, `resume_files`

## 미검증

- 실제 OpenAI API 호출
- 실제 Google/GitHub 운영 OAuth
- 운영 SMTP
- 운영 HTTPS Cookie
- 운영 배포
- 브라우저 E2E
- 파일 바이러스 스캔
- 운영 파일 스토리지
