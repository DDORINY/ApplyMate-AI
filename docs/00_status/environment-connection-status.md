# Environment Connection Status

Last updated: 2026-07-20  
Local branch at update time: `feature/v0.7.0-document-improvement`

This document summarizes the current local environment connection state without exposing secret values. It is based on `.env` key presence, provider modes, and the latest local Docker/API checks.

## Summary

| Area | Current local status | Reason |
| --- | --- | --- |
| Backend application | Connectable in a clean Compose project | Backend became healthy and `/api/v1/health` returned 200 when started with a fresh Compose project. |
| PostgreSQL | Not connectable in the default Compose project | The existing default Docker volume appears to have been initialized with an older PostgreSQL password, so the current `.env` credentials do not match that volume. |
| Redis | Connectable in a clean Compose project | Redis became healthy in the isolated Compose check. |
| AI / OpenAI | Mock only, not real OpenAI | `AI_PROVIDER=mock`; `OPENAI_API_KEY` and `OPENAI_MODEL` are empty. v0.7.0 document improvement uses mock AI locally. |
| Google Calendar | Configured for Google provider, live API still unverified | `CALENDAR_PROVIDER=google` and required Google Calendar credential variables are present, but live Google Calendar event operations still require OAuth consent/API verification. |
| Gmail | Not connected with current `.env` | `GMAIL_PROVIDER` is empty, so Compose falls back to disabled. Gmail client id/secret variables are missing. |
| Social login OAuth | Credentials present, live browser flow still needs verification | Google/GitHub login client and secret variables are present, but production-domain OAuth behavior is not yet verified. |
| SMTP email | Credentials present, live send still needs verification | `EMAIL_PROVIDER=smtp` and SMTP credentials are present, but real outbound email delivery has not been verified in this pass. |

## Current `.env` interpretation

Secret values are intentionally not recorded here.

| Variable group | Observed state | Effective result |
| --- | --- | --- |
| `AI_PROVIDER` | `mock` | AI features use deterministic/mock responses. |
| `OPENAI_API_KEY`, `OPENAI_MODEL` | Empty | Real OpenAI calls are not enabled. |
| `CALENDAR_PROVIDER` | `google` | Calendar integration attempts real Google provider behavior where implemented. |
| `GOOGLE_CALENDAR_CLIENT_ID`, `GOOGLE_CALENDAR_CLIENT_SECRET` | Set | Calendar OAuth configuration exists. |
| `GMAIL_PROVIDER` | Empty | Docker Compose default resolves this to `disabled`. |
| `GOOGLE_GMAIL_CLIENT_ID`, `GOOGLE_GMAIL_CLIENT_SECRET` | Missing | Real Gmail OAuth cannot be used. |
| `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | Set | Google login OAuth configuration exists. |
| `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET` | Set | GitHub login OAuth configuration exists. |
| `EMAIL_PROVIDER` | `smtp` | SMTP email provider is selected. |
| `SMTP_HOST`, `SMTP_USERNAME`, `SMTP_PASSWORD` | Set | SMTP configuration exists. |
| `EXTERNAL_TOKEN_ENCRYPTION_KEY` | Set | External OAuth token encryption is configured. |
| `DATABASE_URL`, `REDIS_URL` | Set | App has DB/Redis connection strings. |
| `JWT_SECRET_KEY`, `JWT_REFRESH_SECRET_KEY` | Set | JWT signing secrets are configured. |

## What is currently not connected

### 1. Default Docker PostgreSQL connection

The default Compose project failed on DB authentication:

```text
password authentication failed for user "applymate"
```

Likely cause: the named PostgreSQL Docker volume was created earlier with a different `POSTGRES_PASSWORD`. PostgreSQL only uses `POSTGRES_PASSWORD` when initializing a new data directory; changing `.env` later does not change the existing database password.

Recommended options:

- Keep the existing volume and align `.env`/`DATABASE_URL` with the password that initialized that volume.
- Or, after explicit approval, recreate the local development DB volume. This deletes local DB data, so it was not done automatically.
- Or use a separate Compose project/volume for validation, as done during v0.5.1 checks.

### 2. Gmail integration with current `.env`

Gmail is not connected because:

- `GMAIL_PROVIDER` is empty.
- `GOOGLE_GMAIL_CLIENT_ID` is missing.
- `GOOGLE_GMAIL_CLIENT_SECRET` is missing.

To test locally without Google:

```env
GMAIL_PROVIDER=mock
```

To test real Google Gmail OAuth:

```env
GMAIL_PROVIDER=google
GOOGLE_GMAIL_CLIENT_ID=...
GOOGLE_GMAIL_CLIENT_SECRET=...
GOOGLE_GMAIL_REDIRECT_URI=http://localhost:8000/api/v1/integrations/gmail/callback
```

The Gmail scope should remain read-only:

```env
GOOGLE_GMAIL_SCOPES=openid,email,profile,https://www.googleapis.com/auth/gmail.readonly
```

### 3. Real OpenAI calls

OpenAI is not connected because:

- `AI_PROVIDER=mock`
- `OPENAI_API_KEY` is empty
- `OPENAI_MODEL` is empty

This is expected if the project is being tested without paid or live AI calls.

### 4. Live Google Calendar and SMTP

Calendar and SMTP have credential-shaped environment values, but this pass did not verify real external calls. They remain operational verification items:

- Google OAuth consent and live Calendar API behavior
- SMTP provider login and actual email delivery

## Last verified behavior

- Backend tests: `163 passed`
- Frontend lint/type-check/build: passed
- Docker Compose config: passed
- Alembic head: `20260720_0100`
- v0.7.0 isolated Docker PostgreSQL migration upgrade/downgrade/upgrade: passed
- Clean Compose backend/PostgreSQL/Redis health: passed
- Gmail mock flow with temporary `GMAIL_PROVIDER=mock`: connect/callback/sync passed

## Do not commit

Do not commit `.env` or any real secret values. Keep only names and safe example formats in `.env.example` and documentation.
