# Google Calendar Integration Guide

## Local mock mode

`.env`:

```env
CALENDAR_PROVIDER=mock
EXTERNAL_TOKEN_ENCRYPTION_KEY=replace-with-local-random-string
EXTERNAL_TOKEN_ENCRYPTION_KEY_VERSION=v1
GOOGLE_CALENDAR_REDIRECT_URI=http://localhost:8000/api/v1/integrations/calendar/callback
```

Mock mode supports:

- authorization URL generation
- callback completion
- Calendar list
- writable Calendar selection
- internal schedule sync
- mapping create/update
- sync run/error records
- disconnect

## Real Google mode

`.env`:

```env
CALENDAR_PROVIDER=google
GOOGLE_CALENDAR_CLIENT_ID=
GOOGLE_CALENDAR_CLIENT_SECRET=
GOOGLE_CALENDAR_REDIRECT_URI=https://your-domain.example/api/v1/integrations/calendar/callback
GOOGLE_CALENDAR_SCOPES=openid,email,profile,https://www.googleapis.com/auth/calendar.calendarlist.readonly,https://www.googleapis.com/auth/calendar.events
EXTERNAL_TOKEN_ENCRYPTION_KEY=
EXTERNAL_TOKEN_ENCRYPTION_KEY_VERSION=v1
```

Required Google Cloud setup:

1. Create or select a Google Cloud project.
2. Configure OAuth consent screen.
3. Create OAuth client for web application.
4. Register backend callback URI.
5. Review requested scopes.
6. Test with a non-production user.

## NEEDS_VERIFICATION

v0.5.0 includes a Google provider structure, but actual Google API event create/update/delete remains `NEEDS_VERIFICATION` until real credentials and consent configuration are available.

## Security checklist

- Do not commit `GOOGLE_CALENDAR_CLIENT_SECRET`.
- Do not commit `EXTERNAL_TOKEN_ENCRYPTION_KEY`.
- Do not log authorization code, access token, refresh token, or sync token.
- Do not use login OAuth tokens for Calendar API calls.
- Do not create/modify/delete Google Calendar events without explicit user action.

## Smoke flow

1. Sign up and log in.
2. Open `/settings/integrations`.
3. Click Google Calendar connect.
4. Complete callback.
5. Select `ApplyMate Mock Calendar`.
6. Create an internal schedule.
7. Run one-event sync from API or full sync from UI.
8. Confirm mapping and sync run.
9. Disconnect.
