# ApplyMate AI

ApplyMate AI는 개인용 AI 취업 매니저입니다. 사용자의 경력, 기술, 프로젝트 경험을 기반으로 채용공고 추천, 지원 문서 작성, 지원 현황 및 일정 관리를 단계적으로 구현합니다.

## 기술 스택

* Frontend: Next.js, TypeScript, Tailwind CSS, App Router
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

## 현재 구현 범위

v0.1.0에서는 프로젝트 기반 구축, Backend Health API, Frontend 서비스 상태 화면, Docker Compose 개발 환경, 환경변수 예시, 기본 테스트를 구현했습니다.

## 다음 개발 버전

v0.1.1에서는 회원가입, 로그인, JWT 인증, 사용자 정보 조회를 구현합니다.
