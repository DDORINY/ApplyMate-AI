# Error Codes

## Common

| Code | HTTP | Description |
| --- | --- | --- |
| `VALIDATION_ERROR` | 422 | Invalid request payload |
| `AUTH_TOKEN_MISSING` | 401 | Missing auth token |
| `AUTH_TOKEN_INVALID` | 401 | Invalid auth token |
| `RESOURCE_NOT_FOUND` | 404 | Resource or route not found |
| `INTERNAL_SERVER_ERROR` | 500 | Internal server error |

## v0.7.0 Document Improvement Error Codes

| Code | HTTP | Description |
| --- | --- | --- |
| `DOCUMENT_IMPROVEMENT_BASE_VERSION_NOT_FOUND` | 404 | Base application document version was not found |
| `DOCUMENT_IMPROVEMENT_NOT_FOUND` | 404 | Improvement run was not found or does not belong to user |
| `DOCUMENT_IMPROVEMENT_SUGGESTION_NOT_FOUND` | 404 | Sentence suggestion was not found |
| `DOCUMENT_IMPROVEMENT_INVALID_LENGTH` | 400 | Target length range is invalid |
| `DOCUMENT_IMPROVEMENT_INVALID_REQUEST` | 400 | Improvement update/apply request is invalid |
| `DOCUMENT_IMPROVEMENT_OUTDATED` | 409 | A newer document version exists after the improvement base version |
| `DOCUMENT_IMPROVEMENT_ALREADY_APPLIED` | 409 | Improvement run has already been applied or cannot be changed |
| `AI_PROVIDER_DISABLED` | 503 | AI provider is disabled |
| `AI_PROVIDER_CONFIG_INVALID` | 503 | AI provider credentials/model are missing |
| `AI_PROVIDER_INVALID_RESPONSE` | 502 | AI output did not match the required structured schema |

## v0.6.1 Recommendation Automation Error Codes

| Code | HTTP | Description |
| --- | --- | --- |
| `RECOMMENDATION_SETTINGS_NOT_FOUND` | 404 | Recommendation settings were not found |
| `RECOMMENDATION_FREQUENCY_INVALID` | 400 | Recommendation execution frequency is invalid |
| `RECOMMENDATION_RUN_NOT_DUE` | 409 | Recommendation execution is not due |
| `RECOMMENDATION_RUN_ALREADY_RUNNING` | 409 | Recommendation execution is already running |
| `RECOMMENDATION_SNAPSHOT_NOT_FOUND` | 404 | Recommendation snapshot was not found |
| `RECOMMENDATION_NOTIFICATION_NOT_FOUND` | 404 | Recommendation notification candidate was not found |
| `RECOMMENDATION_NOTIFICATION_ALREADY_DISMISSED` | 409 | Recommendation notification candidate is already dismissed |
| `RECOMMENDATION_AUTOMATION_FORBIDDEN` | 403 | Recommendation automation resource access is forbidden |

## v0.6.0 Job Recommendation Error Codes

| Code | HTTP | Description |
| --- | --- | --- |
| `JOB_RECOMMENDATION_NOT_FOUND` | 404 | Recommendation was not found or does not belong to user |
| `JOB_RECOMMENDATION_RUN_NOT_FOUND` | 404 | Recommendation run was not found |
| `JOB_RECOMMENDATION_PROFILE_INSUFFICIENT` | 409 | Profile data is insufficient for strict generation |
| `JOB_RECOMMENDATION_JOB_NOT_FOUND` | 404 | Job for recommendation refresh was not found |
| `JOB_RECOMMENDATION_JOB_ALREADY_APPLIED` | 409 | Job is already applied and excluded |
| `JOB_RECOMMENDATION_POLICY_INVALID` | 400 | Recommendation policy is invalid |
| `JOB_RECOMMENDATION_GENERATION_FAILED` | 500 | Recommendation generation failed safely |
| `JOB_RECOMMENDATION_FEEDBACK_INVALID` | 400 | Feedback payload is invalid |
| `JOB_RECOMMENDATION_FEEDBACK_NOT_FOUND` | 404 | Feedback was not found |
| `JOB_RECOMMENDATION_FORBIDDEN` | 403 | Recommendation access is forbidden |

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

## v0.5.1 Gmail Integration Error Codes

| Code | HTTP | Description |
| --- | --- | --- |
| `GMAIL_CONNECTION_NOT_FOUND` | 404 | Gmail connection does not exist |
| `GMAIL_PROVIDER_DISABLED` | 503/409 | Gmail provider or sync is disabled |
| `GMAIL_PROVIDER_UNAVAILABLE` | 503 | Gmail provider call failed or needs verification |
| `GMAIL_OAUTH_STATE_INVALID` | 400 | Gmail OAuth state is invalid or already consumed |
| `GMAIL_OAUTH_STATE_EXPIRED` | 400 | Gmail OAuth state expired |
| `GMAIL_TOKEN_REFRESH_FAILED` | 503 | Gmail token refresh failed |
| `GMAIL_REAUTH_REQUIRED` | 409 | Gmail account must be reauthorized |
| `GMAIL_SYNC_FAILED` | 503 | Gmail sync failed |
| `GMAIL_MESSAGE_NOT_FOUND` | 404 | Gmail message was not found |
| `GMAIL_MESSAGE_ALREADY_PROCESSED` | 409 | Gmail message was already processed |
| `GMAIL_ANALYSIS_FAILED` | 502 | Gmail analysis failed |
| `GMAIL_ANALYSIS_INVALID_OUTPUT` | 502 | Gmail analysis output is invalid |
| `EMAIL_CANDIDATE_NOT_FOUND` | 404 | Email candidate was not found |
| `EMAIL_CANDIDATE_ALREADY_APPLIED` | 409 | Email candidate was already applied |
| `EMAIL_CANDIDATE_EXPIRED` | 409 | Email candidate expired |
| `EMAIL_CANDIDATE_APPLICATION_REQUIRED` | 400 | Application id is required |
| `EMAIL_CANDIDATE_APPLICATION_MISMATCH` | 404 | Application does not belong to user |
| `EMAIL_CANDIDATE_SCHEDULE_CONFLICT` | 400/409 | Candidate schedule payload is invalid or conflicts |
| `EMAIL_CANDIDATE_FORBIDDEN` | 403 | Candidate access is forbidden |

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
