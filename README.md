# ApplyMate AI

현재 버전: v0.2.2

ApplyMate AI는 개인용 AI 취업 매니저입니다. 사용자의 커리어 프로필, 기술, 경력, 프로젝트, 희망 조건을 기반으로 채용공고를 관리하고, 공고 분석과 사용자-공고 적합도 분석을 지원합니다.

## 현재 구현 범위

- 회원가입, 로그인, JWT 인증, refresh token rotation
- 이메일 인증, 비밀번호 복구, 세션/보안 이벤트 관리
- Google/GitHub OAuth 로그인과 계정 연결
- 커리어 프로필, 기술, 경력, 프로젝트, 희망 조건, 지원 제외 조건, 포트폴리오 링크 관리
- 채용공고 직접 등록, URL 등록, 목록/상세/수정/삭제, 중복 감지
- AI 채용공고 분석: 주요 업무, 조건, 기술, 경력, 마감, 키워드 추출
- 사용자-공고 적합도 분석: 규칙 기반 점수, 등급, 추천 상태, 근거, 실행 이력, 피드백

## v0.2.2 사용자-공고 적합도 분석

- 완료된 최신 채용공고 분석과 사용자 커리어 프로필을 비교합니다.
- 점수는 deterministic rule-based 방식으로 계산합니다.
- AI는 숫자 점수를 변경하지 않으며, `AI_PROVIDER=disabled`여도 template 설명으로 동작합니다.
- 점수 가중치:
  - 직무 25%
  - 기술 30%
  - 경력 15%
  - 프로젝트 15%
  - 희망 조건 10%
  - 위험/제외 조건 5%
- 결과는 `job_matches`, 실행 이력은 `job_match_runs`, 사용자 피드백은 `job_match_feedback`에 저장합니다.
- `/jobs/{jobId}` 상세 화면에서 적합도 분석과 피드백을 사용할 수 있습니다.

## 기술 스택

- Frontend: Next.js, TypeScript, Tailwind CSS, TanStack Query
- Backend: Python, FastAPI, SQLAlchemy, Alembic, Pydantic
- Database: PostgreSQL
- Cache: Redis
- Infrastructure: Docker, Docker Compose

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

## 주요 화면

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
```

## 주요 API

Base URL: `/api/v1`

### 인증/계정

```text
POST   /auth/signup
POST   /auth/login
POST   /auth/refresh
POST   /auth/logout
GET    /auth/me
POST   /auth/email-verification/send
POST   /auth/email-verification/verify
POST   /auth/password/forgot
POST   /auth/password/reset
POST   /auth/password/change
POST   /auth/password/set
GET    /auth/sessions
DELETE /auth/sessions/{sessionId}
DELETE /auth/sessions/others
DELETE /auth/sessions
GET    /auth/security-events
```

### 커리어 프로필

```text
GET    /profiles/me
POST   /profiles
PATCH  /profiles/me
GET    /profiles/me/skills
POST   /profiles/me/skills
GET    /profiles/me/experiences
POST   /profiles/me/experiences
GET    /profiles/me/projects
POST   /profiles/me/projects
GET    /profiles/me/preferences
PUT    /profiles/me/preferences
GET    /profiles/me/exclusions
POST   /profiles/me/exclusions
GET    /profiles/me/portfolio-links
POST   /profiles/me/portfolio-links
```

### 채용공고

```text
POST   /jobs
POST   /jobs/import-url
GET    /jobs
GET    /jobs/{jobId}
PATCH  /jobs/{jobId}
DELETE /jobs/{jobId}
```

### 채용공고 분석

```text
GET    /ai/providers
POST   /jobs/{jobId}/analysis
GET    /jobs/{jobId}/analysis
PATCH  /jobs/{jobId}/analysis
DELETE /jobs/{jobId}/analysis
GET    /jobs/{jobId}/analysis/runs
```

### 사용자-공고 적합도 분석

```text
POST   /jobs/{jobId}/match
GET    /jobs/{jobId}/match
DELETE /jobs/{jobId}/match
GET    /jobs/{jobId}/match/runs
POST   /jobs/{jobId}/match/feedback
GET    /jobs/{jobId}/match/feedback
PATCH  /jobs/{jobId}/match/feedback/{feedbackId}
DELETE /jobs/{jobId}/match/feedback/{feedbackId}
```

## Migration

```bash
cd backend
alembic upgrade head
alembic downgrade -1
alembic upgrade head
```

주요 migration:

```text
backend/alembic/versions/20260718_1501_create_auth_tables.py
backend/alembic/versions/20260718_1900_create_career_profile_tables.py
backend/alembic/versions/20260718_2100_add_social_auth.py
backend/alembic/versions/20260719_1000_add_account_security.py
backend/alembic/versions/20260719_1200_create_job_posting_tables.py
backend/alembic/versions/20260719_1300_create_job_analysis_tables.py
backend/alembic/versions/20260719_1400_create_job_match_tables.py
```

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
docker compose ps
docker compose down
```

볼륨 삭제가 필요한 명령(`docker compose down -v`)은 기본 검증에서 사용하지 않습니다.

## 다음 버전

v0.3.x에서는 이력서 업로드/분석과 근거 기반 지원 문서 생성을 구현합니다.
