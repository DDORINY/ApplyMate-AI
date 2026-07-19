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
