# 환경변수

실제 secret 값은 `.env` 또는 배포 환경의 secret manager에만 저장합니다. `.env.example`에는 이름과 형식만 기록합니다.

## 공통

| 변수 | 설명 | 예시 |
| --- | --- | --- |
| `APP_ENV` | 실행 환경 | `development` |
| `FRONTEND_URL` | 프론트엔드 origin | `http://localhost:3000` |
| `BACKEND_URL` | 백엔드 origin | `http://localhost:8000` |
| `NEXT_PUBLIC_API_BASE_URL` | 브라우저에서 호출할 API base URL | `http://localhost:8000/api/v1` |

## 데이터 저장소

| 변수 | 설명 | 예시 |
| --- | --- | --- |
| `POSTGRES_DB` | PostgreSQL DB 이름 | `applymate` |
| `POSTGRES_USER` | PostgreSQL 사용자 | `applymate` |
| `POSTGRES_PASSWORD` | PostgreSQL 비밀번호 | `change_me` |
| `DATABASE_URL` | SQLAlchemy DB 연결 문자열 | `postgresql+psycopg://applymate:change_me@postgres:5432/applymate` |
| `REDIS_URL` | Redis 연결 문자열 | `redis://redis:6379/0` |

## 인증

| 변수 | 설명 | 예시 |
| --- | --- | --- |
| `JWT_SECRET_KEY` | Access Token 서명 Secret | 실제 값은 `.env`에만 저장 |
| `JWT_REFRESH_SECRET_KEY` | Refresh Token 서명 Secret | 실제 값은 `.env`에만 저장 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access Token 만료 시간 | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh Token 만료 일수 | `14` |
| `COOKIE_SECURE` | HTTPS 환경 Cookie Secure 여부 | 개발 `false`, 운영 `true` |
| `COOKIE_SAMESITE` | Cookie SameSite 정책 | `lax` |

## OAuth v0.1.3

| 변수 | 설명 | 개발 기본값 |
| --- | --- | --- |
| `GOOGLE_CLIENT_ID` | Google OAuth Client ID | 빈 값이면 Google 비활성 |
| `GOOGLE_CLIENT_SECRET` | Google OAuth Client Secret | 빈 값이면 Google 비활성 |
| `GOOGLE_REDIRECT_URI` | Google provider callback URI | `http://localhost:8000/api/v1/auth/oauth/google/callback` |
| `GITHUB_CLIENT_ID` | GitHub OAuth Client ID | 빈 값이면 GitHub 비활성 |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth Client Secret | 빈 값이면 GitHub 비활성 |
| `GITHUB_REDIRECT_URI` | GitHub provider callback URI | `http://localhost:8000/api/v1/auth/oauth/github/callback` |
| `OAUTH_FRONTEND_CALLBACK_URL` | 서비스 프론트 callback URL | `http://localhost:3000/auth/callback` |
| `OAUTH_ALLOWED_REDIRECT_PATHS` | 로그인 완료 후 이동 가능한 내부 경로 CSV | `/me,/profile,/settings/accounts` |
| `OAUTH_STATE_EXPIRE_SECONDS` | OAuth state 만료 초 | `300` |
| `OAUTH_TICKET_EXPIRE_SECONDS` | Login ticket 만료 초 | `60` |

## 외부 AI

| 변수 | 설명 | 예시 |
| --- | --- | --- |
| `OPENAI_API_KEY` | 향후 AI 기능용 API key | 실제 값은 `.env`에만 저장 |
