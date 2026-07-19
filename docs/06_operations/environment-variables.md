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

| 변수 | 설명 |
| --- | --- |
| `JWT_SECRET_KEY` | Access Token signing secret |
| `JWT_REFRESH_SECRET_KEY` | Refresh Token signing secret |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access Token expiry minutes |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh Token expiry days |
| `COOKIE_SECURE` | HTTPS cookie secure flag |
| `COOKIE_SAMESITE` | Cookie SameSite |

## Login OAuth

| 변수 | 설명 |
| --- | --- |
| `GOOGLE_CLIENT_ID` | Login Google OAuth client id |
| `GOOGLE_CLIENT_SECRET` | Login Google OAuth secret |
| `GOOGLE_REDIRECT_URI` | Login Google OAuth callback |
| `GITHUB_CLIENT_ID` | GitHub OAuth client id |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth secret |
| `GITHUB_REDIRECT_URI` | GitHub OAuth callback |
| `OAUTH_FRONTEND_CALLBACK_URL` | Frontend OAuth callback |
| `OAUTH_ALLOWED_REDIRECT_PATHS` | Allowed redirect paths CSV |

## Google Calendar Integration

| 변수 | 설명 |
| --- | --- |
| `CALENDAR_PROVIDER` | `disabled`, `mock`, or `google` |
| `GOOGLE_CALENDAR_CLIENT_ID` | Calendar OAuth client id |
| `GOOGLE_CALENDAR_CLIENT_SECRET` | Calendar OAuth secret |
| `GOOGLE_CALENDAR_REDIRECT_URI` | Calendar OAuth callback |
| `GOOGLE_CALENDAR_SCOPES` | Calendar OAuth scopes CSV |
| `EXTERNAL_TOKEN_ENCRYPTION_KEY` | External token encryption key |
| `EXTERNAL_TOKEN_ENCRYPTION_KEY_VERSION` | Encryption key version |
| `CALENDAR_OAUTH_STATE_EXPIRE_SECONDS` | Calendar OAuth state expiry seconds |

## Gmail Integration

| 변수 | 설명 |
| --- | --- |
| `GMAIL_PROVIDER` | `disabled`, `mock`, or `google` |
| `GOOGLE_GMAIL_CLIENT_ID` | Gmail OAuth client id |
| `GOOGLE_GMAIL_CLIENT_SECRET` | Gmail OAuth secret |
| `GOOGLE_GMAIL_REDIRECT_URI` | Gmail OAuth callback |
| `GOOGLE_GMAIL_SCOPES` | Gmail OAuth scopes CSV; v0.5.1 uses read-only |
| `GMAIL_OAUTH_STATE_EXPIRE_SECONDS` | Gmail OAuth state expiry seconds |
| `GMAIL_DEFAULT_SEARCH_QUERY` | Default Gmail search query |
| `GMAIL_DEFAULT_LOOKBACK_DAYS` | Default Gmail lookback window |
| `GMAIL_MAX_MESSAGES_PER_SYNC` | Maximum messages per sync |

## AI

| 변수 | 설명 |
| --- | --- |
| `AI_PROVIDER` | `disabled`, `mock`, or `openai` |
| `OPENAI_API_KEY` | OpenAI API key |
| `OPENAI_MODEL` | OpenAI model |

## Resume Upload

| 변수 | 설명 |
| --- | --- |
| `RESUME_STORAGE_DIR` | Resume file storage directory |
| `RESUME_MAX_FILE_SIZE_BYTES` | Maximum file size |
| `RESUME_ALLOWED_EXTENSIONS` | Allowed extensions |
| `RESUME_ALLOWED_CONTENT_TYPES` | Allowed MIME types |
