# Environment Variables

실제 secret 값은 `.env` 또는 운영 secret manager에만 저장한다. `.env.example`과 문서에는 변수명과 예시 형식만 기록한다.

## Common

| 변수 | 설명 | 예시 |
| --- | --- | --- |
| `APP_ENV` | 실행 환경 | `development` |
| `FRONTEND_URL` | Frontend origin | `http://localhost:3000` |
| `BACKEND_URL` | Backend origin | `http://localhost:8000` |
| `NEXT_PUBLIC_API_BASE_URL` | Browser API base URL | `http://localhost:8000/api/v1` |

## Database / Cache

| 변수 | 설명 | 예시 |
| --- | --- | --- |
| `DATABASE_URL` | SQLAlchemy DB URL | `postgresql+psycopg://applymate:change_me@postgres:5432/applymate` |
| `REDIS_URL` | Redis URL | `redis://redis:6379/0` |

## Auth

| 변수 | 설명 | 예시 |
| --- | --- | --- |
| `JWT_SECRET_KEY` | Access Token signing secret | 실제 값은 commit 금지 |
| `JWT_REFRESH_SECRET_KEY` | Refresh Token signing secret | 실제 값은 commit 금지 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access Token 만료 분 | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh Token 만료 일 | `14` |
| `COOKIE_SECURE` | HTTPS cookie secure 여부 | `false` |
| `COOKIE_SAMESITE` | Cookie SameSite | `lax` |

## Login OAuth

| 변수 | 설명 | 예시 |
| --- | --- | --- |
| `GOOGLE_CLIENT_ID` | 로그인용 Google OAuth client id | 실제 값은 commit 금지 |
| `GOOGLE_CLIENT_SECRET` | 로그인용 Google OAuth secret | 실제 값은 commit 금지 |
| `GOOGLE_REDIRECT_URI` | 로그인용 Google OAuth callback | `http://localhost:8000/api/v1/auth/oauth/google/callback` |
| `GITHUB_CLIENT_ID` | GitHub OAuth client id | 실제 값은 commit 금지 |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth secret | 실제 값은 commit 금지 |
| `GITHUB_REDIRECT_URI` | GitHub OAuth callback | `http://localhost:8000/api/v1/auth/oauth/github/callback` |
| `OAUTH_FRONTEND_CALLBACK_URL` | OAuth 완료 후 frontend callback | `http://localhost:3000/auth/callback` |
| `OAUTH_ALLOWED_REDIRECT_PATHS` | 허용 redirect path CSV | `/me,/profile,/settings/accounts` |

## Google Calendar Integration

| 변수 | 설명 | 예시 |
| --- | --- | --- |
| `CALENDAR_PROVIDER` | Calendar provider | `disabled`, `mock`, `google` |
| `GOOGLE_CALENDAR_CLIENT_ID` | Calendar 전용 Google OAuth client id | 실제 값은 commit 금지 |
| `GOOGLE_CALENDAR_CLIENT_SECRET` | Calendar 전용 Google OAuth secret | 실제 값은 commit 금지 |
| `GOOGLE_CALENDAR_REDIRECT_URI` | Calendar OAuth callback | `http://localhost:8000/api/v1/integrations/calendar/callback` |
| `GOOGLE_CALENDAR_SCOPES` | Calendar OAuth scopes CSV | `openid,email,profile,https://www.googleapis.com/auth/calendar.calendarlist.readonly,https://www.googleapis.com/auth/calendar.events` |
| `EXTERNAL_TOKEN_ENCRYPTION_KEY` | 외부 token 암호화 key | 실제 값은 commit 금지 |
| `EXTERNAL_TOKEN_ENCRYPTION_KEY_VERSION` | 암호화 key version | `v1` |
| `CALENDAR_OAUTH_STATE_EXPIRE_SECONDS` | Calendar OAuth state 만료 초 | `300` |

## AI

| 변수 | 설명 | 예시 |
| --- | --- | --- |
| `AI_PROVIDER` | AI provider | `disabled`, `mock`, `openai` |
| `OPENAI_API_KEY` | OpenAI API key | 실제 값은 commit 금지 |
| `OPENAI_MODEL` | OpenAI model | 운영 설정 필요 |

## Resume Upload

| 변수 | 설명 | 예시 |
| --- | --- | --- |
| `RESUME_STORAGE_DIR` | 이력서 파일 저장 경로 | `storage/resumes` |
| `RESUME_MAX_FILE_SIZE_BYTES` | 최대 파일 크기 | `5242880` |
| `RESUME_ALLOWED_EXTENSIONS` | 허용 확장자 | `.pdf,.docx` |
| `RESUME_ALLOWED_CONTENT_TYPES` | 허용 MIME | `application/pdf,...` |
