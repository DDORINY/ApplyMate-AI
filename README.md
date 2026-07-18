# ApplyMate AI

현재 버전: v0.1.1

ApplyMate AI는 개인용 AI 취업 매니저입니다. 사용자의 경력, 기술, 프로젝트 경험을 기반으로 채용공고 추천, 지원 문서 작성, 지원 현황 및 일정 관리를 단계적으로 구현합니다.

## 기술 스택

* Frontend: Next.js, TypeScript, Tailwind CSS, App Router, TanStack Query, React Hook Form, Zod
* Backend: Python, FastAPI, SQLAlchemy, Alembic, Pydantic
* Database: PostgreSQL
* Cache: Redis
* Infrastructure: Docker, Docker Compose

## 폴더 구조

```text
frontend/   Next.js 프론트엔드
backend/    FastAPI 백엔드
docs/       프로젝트 문서
infra/      인프라 보조 문서 및 설정
```

## 사전 요구사항

* Python 3.12 이상
* Node.js 22 이상
* Docker 및 Docker Compose

## 환경변수 설정

```bash
cp .env.example .env
```

`.env`에는 실제 Secret을 저장할 수 있지만 Git에는 포함하지 않습니다. 공개 예시는 `.env.example`만 사용합니다.

## Docker Compose 실행

```bash
docker compose up --build
```

기본 포트는 Frontend `3000`, Backend `8000`, PostgreSQL `5432`, Redis `6379`입니다.

## 로컬 실행

Backend:

```bash
cd backend
alembic upgrade head
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## 테스트 및 검증

Backend:

```bash
cd backend
pytest
```

Frontend:

```bash
cd frontend
npm run lint
npm run type-check
npm run build
```

Docker Compose:

```bash
docker compose config
```

## Health API

```http
GET http://localhost:8000/api/v1/health
```

응답 예시:

```json
{
  "success": true,
  "data": {
    "status": "UP",
    "database": "UP",
    "redis": "UP"
  },
  "message": "서비스가 정상적으로 실행 중입니다."
}
```

## 인증 API

Base URL은 `/api/v1`입니다.

```text
POST /auth/signup
POST /auth/login
POST /auth/refresh
POST /auth/logout
GET  /auth/me
```

로그인은 Access Token을 응답 본문으로 반환하고 Refresh Token은 HttpOnly Cookie로 전달합니다. 보호 API는 `Authorization: Bearer {access_token}` 헤더를 사용합니다.

## 회원가입 및 로그인

Frontend 실행 후 다음 화면을 사용합니다.

```text
http://localhost:3000/signup
http://localhost:3000/login
http://localhost:3000/me
```

`/me`는 인증이 필요한 보호 화면이며, 미인증 사용자는 로그인 화면으로 이동합니다.

## Migration

```bash
cd backend
alembic upgrade head
alembic downgrade -1
alembic upgrade head
```

## v0.1.1 구현 범위

* 이메일 회원가입 및 로그인
* PBKDF2 기반 비밀번호 해시 저장
* JWT Access Token 발급 및 검증
* HttpOnly Cookie 기반 Refresh Token 발급, 저장, rotation, 폐기
* 현재 로그인 사용자 조회
* 사용자 및 Refresh Token 테이블과 Alembic migration
* 회원가입, 로그인, 보호 페이지 Frontend 연결
* 인증 오류 코드 및 테스트

## 현재 구현 범위

v0.1.1에서는 v0.1.0 프로젝트 기반 위에 회원 및 인증 기능을 구현했습니다.

## 다음 개발 버전

v0.1.2에서는 커리어 프로필 기능을 구현합니다.
