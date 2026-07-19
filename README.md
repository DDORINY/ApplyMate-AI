# ApplyMate AI

현재 버전: v0.2.0

ApplyMate AI는 개인용 AI 취업 매니저입니다. 사용자의 계정, 커리어 프로필, 기술 스택, 경력, 프로젝트, 희망 조건을 기반으로 채용공고 관리, 적합도 분석, 지원 문서 생성, 지원 현황 관리를 단계적으로 구현합니다.

## 기술 스택

- Frontend: Next.js, TypeScript, Tailwind CSS, App Router, TanStack Query, React Hook Form, Zod
- Backend: Python, FastAPI, SQLAlchemy, Alembic, Pydantic
- Database: PostgreSQL
- Cache: Redis
- Infrastructure: Docker, Docker Compose

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
/auth/callback
/me
/profile
/jobs
/jobs/new
/jobs/{jobId}
/settings/accounts
```

## v0.2.0 구현 범위

- 채용공고 직접 등록
- URL 기반 채용공고 등록
  - `http`, `https`만 허용
  - 사설망, loopback, link-local, multicast, reserved IP 차단
  - redirect 대상 재검증
  - HTML 응답과 최대 수집 크기 제한
  - 제목, meta description, 본문 텍스트의 제한적 추출
- 기업 정보 저장 및 재사용
- 채용공고 목록/상세 조회
- 검색, 상태/고용형태/근무형태/관심 필터, 정렬, 페이지네이션
- 채용공고 수정, 삭제
- 공고 상태와 관심 공고 관리
- 사용자별 소유권 검증
- URL, 내용 hash, 기업-제목-마감일 기준 중복 감지
- `/jobs`, `/jobs/new`, `/jobs/{jobId}` 프론트 화면
- Alembic migration과 Backend 테스트

## v0.2.0 제외 범위

- AI 공고 분석
- 사용자-공고 적합도 분석
- 지원 현황 관리
- 일정/Google Calendar 연동
- 사이트별 scraper와 대규모 crawling

## v0.1.4 구현 범위

- 이메일 인증 메일 생성/재발송/검증
- 비밀번호 찾기와 재설정
- 로그인 사용자 비밀번호 변경
- 소셜 로그인 전용 사용자 비밀번호 설정
- 로그인 세션 목록 조회
- 개별 세션, 다른 모든 세션, 전체 세션 로그아웃
- 로그인 실패 횟수 제한
- 보안 이벤트 기록
- 개발/SMTP 이메일 발송 Adapter와 설정 문서
- `/verify-email`, `/forgot-password`, `/reset-password`, `/settings/security` 화면

## v0.1.3 구현 범위

- Google, GitHub OAuth 로그인
- OAuth provider authorize URL 생성, provider callback 처리, 1회용 login ticket 교환
- OAuth access token/provider token 미저장 정책
- 기존 이메일 계정과 같은 이메일의 소셜 계정은 자동 병합하지 않고 명시적 계정 연결 요구
- 로그인 사용자의 소셜 계정 연결/목록/해제 화면
- 마지막 로그인 수단 해제 방지
- `users.email_verified`, nullable `users.password_hash`, OAuth 계정/state/ticket 테이블
- 프론트 `/auth/callback`, `/settings/accounts` 화면 추가
- Backend test, ruff, Frontend lint/type-check/build 검증

## API

Base URL은 `/api/v1`입니다.

### 인증

```text
POST /auth/signup
POST /auth/login
POST /auth/refresh
POST /auth/logout
GET  /auth/me
POST /auth/email-verification/send
POST /auth/email-verification/verify
POST /auth/password/forgot
POST /auth/password/reset
POST /auth/password/change
POST /auth/password/set
GET  /auth/sessions
DELETE /auth/sessions/{sessionId}
DELETE /auth/sessions/others
DELETE /auth/sessions
GET  /auth/security-events
```

Access Token은 응답 본문으로 반환하고, Refresh Token은 `applymate_refresh_token` HttpOnly Cookie로 전달합니다. 보호 API는 `Authorization: Bearer {access_token}` 헤더를 사용합니다.

### 소셜 로그인

```text
GET    /auth/oauth/providers
GET    /auth/oauth/{provider}/authorize
GET    /auth/oauth/{provider}/callback
POST   /auth/oauth/exchange
GET    /auth/oauth/accounts
GET    /auth/oauth/{provider}/link/authorize
DELETE /auth/oauth/accounts/{provider}
```

지원 provider는 `google`, `github`입니다.

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

### 채용공고

```text
POST   /jobs
POST   /jobs/import-url
GET    /jobs
GET    /jobs/{jobId}
PATCH  /jobs/{jobId}
DELETE /jobs/{jobId}
```

## Migration

```bash
cd backend
alembic upgrade head
alembic downgrade -1
alembic upgrade head
```

v0.1.3 migration:

```text
backend/alembic/versions/20260718_2100_add_social_auth.py
```

v0.1.4 migration:

```text
backend/alembic/versions/20260719_1000_add_account_security.py
```

v0.2.0 migration:

```text
backend/alembic/versions/20260719_1200_create_job_posting_tables.py
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

볼륨 삭제가 필요한 명령(`docker compose down -v`)은 사용하지 않습니다.

## 다음 버전

v0.2.1에서는 AI 채용공고 분석 기능을 구현합니다.
