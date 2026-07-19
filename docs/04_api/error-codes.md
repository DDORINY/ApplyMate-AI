# Error Codes

## Common

| Code | HTTP | Description |
| --- | --- | --- |
| `VALIDATION_ERROR` | 422 | Invalid request payload |
| `AUTH_TOKEN_MISSING` | 401 | Missing auth token |
| `AUTH_TOKEN_INVALID` | 401 | Invalid auth token |
| `RESOURCE_NOT_FOUND` | 404 | Resource or route not found |
| `INTERNAL_SERVER_ERROR` | 500 | Internal server error |

## v0.4.2 Dashboard Error Codes

| Code | HTTP | Description |
| --- | --- | --- |
| `DASHBOARD_INVALID_TIMEZONE` | 400 | Dashboard timezone is not a valid IANA timezone |
| `DASHBOARD_INVALID_DATE_RANGE` | 400 | Dashboard custom date range is missing or invalid |

## v0.5.0 Calendar Integration Error Codes

| Code | HTTP | Description |
| --- | --- | --- |
| `CALENDAR_CONNECTION_NOT_FOUND` | 404 | Calendar connection was not found |
| `CALENDAR_PROVIDER_DISABLED` | 503/409 | Calendar provider or sync is disabled |
| `CALENDAR_PROVIDER_UNAVAILABLE` | 503 | Calendar provider is unavailable or not verified |
| `CALENDAR_OAUTH_STATE_INVALID` | 400 | OAuth state is invalid or already consumed |
| `CALENDAR_OAUTH_STATE_EXPIRED` | 400 | OAuth state expired |
| `CALENDAR_OAUTH_CALLBACK_FAILED` | 400 | OAuth callback payload is invalid |
| `CALENDAR_TOKEN_ENCRYPTION_FAILED` | 503 | Token encryption/decryption failed |
| `CALENDAR_TOKEN_REFRESH_FAILED` | 503 | Token refresh failed |
| `CALENDAR_REAUTH_REQUIRED` | 409 | User must reconnect Calendar |
| `CALENDAR_LIST_FAILED` | 400/404/503 | Calendar list or selected Calendar lookup failed |
| `CALENDAR_NOT_WRITABLE` | 400 | Selected Calendar is read-only |
| `CALENDAR_SYNC_FAILED` | 503 | Calendar sync failed safely |
| `CALENDAR_SYNC_CONFLICT` | 409 | Internal and external events conflict |
| `CALENDAR_MAPPING_NOT_FOUND` | 404 | Sync mapping was not found |
| `CALENDAR_EXTERNAL_EVENT_NOT_FOUND` | 404 | External Calendar event was not found |
| `CALENDAR_SYNC_TOKEN_EXPIRED` | 409 | Provider incremental sync token expired |
| `CALENDAR_CONNECTION_FORBIDDEN` | 403 | Calendar connection access is forbidden |

## v0.4.1 Calendar Error Codes

| Code | HTTP | Description |
| --- | --- | --- |
| `SCHEDULE_EVENT_NOT_FOUND` | 404 | Schedule event was not found |
| `SCHEDULE_EVENT_INVALID_TIME_RANGE` | 400 | Start/end time range is invalid |
| `SCHEDULE_EVENT_INVALID_TIMEZONE` | 400 | Datetime or timezone is invalid |
| `SCHEDULE_EVENT_APPLICATION_NOT_FOUND` | 404 | Linked application was not found |
| `SCHEDULE_EVENT_JOB_NOT_FOUND` | 404 | Linked job posting was not found |
| `SCHEDULE_EVENT_RELATION_INVALID` | 400 | Application and job relation is invalid |
| `SCHEDULE_EVENT_STATUS_INVALID` | 400 | Schedule status transition is invalid |
| `SCHEDULE_EVENT_ALREADY_CANCELLED` | 400 | Schedule event is already cancelled |
| `SCHEDULE_EVENT_ALREADY_COMPLETED` | 400 | Schedule event is already completed |
| `SCHEDULE_REMINDER_NOT_FOUND` | 404 | Schedule reminder was not found |
| `SCHEDULE_REMINDER_INVALID_TIME` | 400 | Reminder time must be before event start |
| `SCHEDULE_REMINDER_DUPLICATE` | 409 | Duplicate reminder exists |
| `SCHEDULE_EVENT_FORBIDDEN` | 403 | Schedule event access is forbidden |
