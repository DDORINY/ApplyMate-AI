# 테스트 체크리스트

## v0.1.1

* Backend test: `cd backend && pytest`
* Backend lint: `cd backend && ruff check .`
* Frontend lint: `cd frontend && npm run lint`
* Frontend type-check: `cd frontend && npm run type-check`
* Frontend build: `cd frontend && npm run build`
* Docker Compose config: `docker compose config`
* Docker Compose up: `docker compose up --build -d`
* Migration upgrade: `cd backend && alembic upgrade head`
* Migration downgrade: `cd backend && alembic downgrade -1`
* 인증 API 흐름: 회원가입, 로그인, `/auth/me`, refresh, logout, refresh 재사용 실패
