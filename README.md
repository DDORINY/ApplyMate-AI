# ApplyMate AI

현재 버전: v0.1.2

ApplyMate AI는 개인용 AI 취업 매니저입니다. 사용자의 커리어 프로필, 기술 스택, 경력, 프로젝트, 희망 조건을 기반으로 채용공고 관리, 적합도 분석, 지원 문서 생성, 지원 현황 관리를 단계적으로 구현합니다.

## 기술 스택

- Frontend: Next.js, TypeScript, Tailwind CSS, App Router, TanStack Query, React Hook Form, Zod
- Backend: Python, FastAPI, SQLAlchemy, Alembic, Pydantic
- Database: PostgreSQL
- Cache: Redis
- Infrastructure: Docker, Docker Compose

## 폴더 구조

```text
frontend/   Next.js 프론트엔드
backend/    FastAPI 백엔드
docs/       프로젝트 문서
infra/      인프라 보조 문서 및 설정
```

## 실행

```bash
cp .env.example .env
docker compose up --build
```

기본 포트는 Frontend `3000`, Backend `8000`, PostgreSQL `5432`, Redis `6379`입니다.

## 주요 화면

```text
/
/signup
/login
/me
/profile
```

`/profile`은 인증된 사용자의 커리어 프로필, 기술, 경력, 프로젝트, 희망 조건, 지원 제외 조건, 포트폴리오 링크를 관리하는 화면입니다.

## API

Base URL은 `/api/v1`입니다.

### Health

```text
GET /health
```

### 인증

```text
POST /auth/signup
POST /auth/login
POST /auth/refresh
POST /auth/logout
GET  /auth/me
```

Access Token은 응답 본문으로 반환하고, Refresh Token은 `applymate_refresh_token` HttpOnly Cookie로 전달합니다. 보호 API는 `Authorization: Bearer {access_token}` 헤더를 사용합니다.

### 커리어 프로필

```text
GET    /profiles/me
POST   /profiles
PATCH  /profiles/me

GET    /profiles/me/skills
POST   /profiles/me/skills
PATCH  /profiles/me/skills/{userSkillId}
DELETE /profiles/me/skills/{userSkillId}

GET    /profiles/me/experiences
POST   /profiles/me/experiences
GET    /profiles/me/experiences/{experienceId}
PATCH  /profiles/me/experiences/{experienceId}
DELETE /profiles/me/experiences/{experienceId}

GET    /profiles/me/projects
POST   /profiles/me/projects
GET    /profiles/me/projects/{projectId}
PATCH  /profiles/me/projects/{projectId}
DELETE /profiles/me/projects/{projectId}

GET    /profiles/me/preferences
PUT    /profiles/me/preferences
PATCH  /profiles/me/preferences

GET    /profiles/me/exclusions
POST   /profiles/me/exclusions
PATCH  /profiles/me/exclusions/{conditionId}
DELETE /profiles/me/exclusions/{conditionId}

GET    /profiles/me/portfolio-links
POST   /profiles/me/portfolio-links
PATCH  /profiles/me/portfolio-links/{linkId}
DELETE /profiles/me/portfolio-links/{linkId}
```

## v0.1.2 구현 범위

- 사용자별 기본 커리어 프로필 생성, 조회, 수정
- 기술 스택 마스터 및 사용자 기술 관리
- 경력 관리
- 프로젝트 및 프로젝트 기술 연결 관리
- 희망 근무 조건 관리
- 지원 제외 조건 관리
- 포트폴리오 URL 관리
- 사용자 소유권 기반 보호 API
- URL, 날짜, Enum, 중복 입력 검증
- `/profile` 프론트엔드 화면 연결
- v0.1.2 Alembic migration 및 테스트

교육 이력과 자격증은 v0.1.2에서 제외했으며, 이력서 업로드/공고 등록/AI 분석/문서 생성은 이후 버전 범위입니다.

## DB 테이블

v0.1.2 migration:

```text
backend/alembic/versions/20260718_1900_create_career_profile_tables.py
```

추가 테이블:

```text
career_profiles
skills
user_skills
experiences
projects
project_skills
job_preferences
excluded_conditions
portfolio_links
```

## Migration

```bash
cd backend
alembic upgrade head
alembic downgrade -1
alembic upgrade head
```

downgrade는 v0.1.2 테이블과 Enum만 제거하며, v0.1.1의 `users`, `refresh_tokens` 테이블은 유지합니다.

## 검증

Backend:

```bash
cd backend
pytest
ruff check .
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

볼륨 삭제가 필요한 명령(`docker compose down -v`)은 사용하지 않습니다.

## 다음 버전

v0.2.0에서는 채용공고 관리 기능을 구현합니다.
