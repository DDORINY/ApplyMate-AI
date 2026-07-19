# ApplyMate AI

현재 버전: `v0.3.1`

ApplyMate AI는 개인용 AI 취업 매니저입니다. 현재는 회원/인증, 커리어 프로필, 채용공고 관리, AI 채용공고 분석, 사용자-공고 적합도 분석, 이력서 파일 업로드와 텍스트 추출 기반까지 구현되어 있습니다.

## v0.3.1 주요 기능

- PDF/DOCX 이력서 업로드
- 이력서 메타데이터 관리
- 기본 이력서 지정
- 파일 다운로드/삭제
- 확장자/MIME/크기 검증
- 사용자별 중복 파일 해시 차단
- PDF/DOCX 이력서 텍스트 추출
- 추출 결과 사용자 수정
- 재추출 및 실행 이력 조회
- OCR 필요 PDF 상태 표시

## 문서

- [문서 인덱스](docs/README.md)
- [현재 상태](docs/00_status/current-project-status.md)
- [버전 로드맵](docs/05_development-plan/version-roadmap.md)
- [v1.0.0 완성 마스터 플랜](docs/05_development-plan/master-completion-plan.md)
- [API 명세](docs/04_api/api-specification.md)
- [DB 설계](docs/06_database/database-design.md)

현재 버전: v0.2.2

ApplyMate AI는 개인용 AI 취업 매니저입니다. 사용자의 커리어 프로필, 기술, 경력, 프로젝트, 희망 조건을 기반으로 채용공고를 관리하고, AI 채용공고 분석과 사용자-공고 적합도 분석을 지원합니다.

## 현재 완성된 사용자 흐름

```text
회원가입
  -> 이메일 인증
  -> 로그인 또는 OAuth 로그인
  -> 커리어 프로필 작성
  -> 채용공고 등록
  -> AI 채용공고 분석
  -> 사용자-공고 적합도 분석
  -> 결과 확인과 피드백
```

## 핵심 기능

- 이메일 회원가입/로그인
- JWT Access Token, Refresh Token rotation
- Google/GitHub OAuth 로그인과 계정 연결
- 이메일 인증, 비밀번호 복구, 세션 관리, 보안 이벤트
- 커리어 프로필, 기술, 경력, 프로젝트, 희망 조건, 지원 제외 조건, 포트폴리오 링크
- 채용공고 직접 등록, URL 등록, 목록/상세/수정/삭제
- AI 채용공고 분석
- 규칙 기반 사용자-공고 적합도 분석
- 적합도 분석 피드백

## 기술 스택

| 영역 | 기술 |
| --- | --- |
| Frontend | Next.js, TypeScript, Tailwind CSS, TanStack Query |
| Backend | Python, FastAPI, SQLAlchemy, Alembic, Pydantic, JWT |
| Database | PostgreSQL |
| Cache | Redis |
| Infra | Docker, Docker Compose |
| AI | disabled/mock/openai Provider abstraction |

## Architecture 요약

```text
Frontend(Next.js)
  -> Backend(FastAPI /api/v1)
    -> PostgreSQL
    -> Redis
    -> AI Provider
```

## 실행

```bash
cp .env.example .env
docker compose up --build
```

기본 포트:

- Frontend: `3000`
- Backend: `8000`
- PostgreSQL: `5432`
- Redis: `6379`

## 환경변수

주요 환경변수:

- `DATABASE_URL`
- `REDIS_URL`
- `JWT_SECRET_KEY`
- `JWT_REFRESH_SECRET_KEY`
- `AI_PROVIDER`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GITHUB_CLIENT_ID`
- `GITHUB_CLIENT_SECRET`
- `EMAIL_PROVIDER`
- `SMTP_*`

전체 예시는 [.env.example](.env.example)를 참고합니다.

## Frontend 경로

```text
/
/signup
/login
/auth/callback
/me
/profile
/jobs
/jobs/new
/jobs/{jobId}
/settings/accounts
/settings/security
/verify-email
/forgot-password
/reset-password
```

## API 그룹

Base URL: `/api/v1`

- Health
- Auth
- OAuth
- Account Security
- Career Profile
- Jobs
- AI Providers
- Job Analysis
- Job Matching
- Job Match Feedback

상세 API는 [docs/04_api/api-specification.md](docs/04_api/api-specification.md)를 참고합니다.

## Database

현재 migration head: `20260719_1400`

주요 테이블:

- `users`, `refresh_tokens`
- `oauth_accounts`, `oauth_states`, `oauth_login_tickets`
- `career_profiles`, `skills`, `user_skills`, `experiences`, `projects`, `project_skills`, `job_preferences`, `excluded_conditions`, `portfolio_links`
- `email_verification_tokens`, `password_reset_tokens`, `security_events`
- `companies`, `job_postings`
- `job_analyses`, `job_analysis_runs`
- `job_matches`, `job_match_runs`, `job_match_feedback`

상세 DB 문서는 [docs/06_database/database-design.md](docs/06_database/database-design.md)를 참고합니다.

## AI Provider

- `disabled`: AI 분석 비활성. 적합도 분석은 template 설명으로 동작.
- `mock`: 개발/테스트용 구조화 응답.
- `openai`: OpenAI API 사용. 실제 호출은 API key와 model 설정 필요.

적합도 분석의 숫자 점수는 AI가 만들지 않습니다. v0.2.2 기준 점수는 deterministic rule-based 산식으로 계산합니다.

## 검증

Backend:

```bash
cd backend
python -m ruff check .
python -m pytest -p no:cacheprovider
```

Frontend:

```bash
cd frontend
npm run lint
npm run type-check
npm run build
```

Docker:

```bash
docker compose config
docker compose up --build -d
docker compose down
```

Migration:

```bash
cd backend
alembic upgrade head
alembic downgrade -1
alembic upgrade head
```

## 문서 구조

문서 인덱스는 [docs/README.md](docs/README.md)를 참고합니다.

특히 다음 문서를 먼저 확인하세요.

- [현재 프로젝트 상태](docs/00_status/current-project-status.md)
- [완료 기능 목록](docs/00_status/completed-features.md)
- [기능 상태 매트릭스](docs/00_status/feature-status-matrix.md)
- [버전별 상세 문서](docs/11_releases/v0.2.2-job-matching.md)
- [미검증 항목](docs/00_status/unverified-items.md)

## 미검증 항목

- 실제 OpenAI API 호출
- 실제 Google/GitHub OAuth 운영 로그인
- 운영 SMTP 발송
- 운영 HTTPS Cookie
- 운영 배포
- 브라우저 E2E 자동화
- 부하 테스트

자세한 내용은 [docs/00_status/unverified-items.md](docs/00_status/unverified-items.md)를 참고합니다.

## 다음 버전

v0.3.x에서는 이력서 파일 업로드, 이력서 텍스트 추출, AI 이력서 구조화 분석, 맞춤 지원 문서 생성을 진행합니다.
