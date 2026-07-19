# API Specification

## Base

- Base URL: `/api/v1`
- Auth: Bearer Access Token

Success response:

```json
{
  "success": true,
  "data": {},
  "message": "Request processed successfully."
}
```

Error response:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error message"
  }
}
```

## API groups

| Group | Base path | Version | Description |
| --- | --- | --- | --- |
| Auth | `/auth` | v0.1.1~v0.1.4 | Auth, account security, OAuth |
| Profile | `/profiles` | v0.1.2 | Career profile |
| Jobs | `/jobs` | v0.2.0~v0.2.2 | Job postings, analysis, matching |
| Resumes | `/resumes` | v0.3.0~v0.3.2 | Resumes, files, extraction, analysis |
| Documents | `/documents` | v0.3.3 | Application documents and versions |
| Applications | `/applications` | v0.4.0 | Application tracking |
| Calendar | `/calendar` | v0.4.1 | Schedule management |

## v0.4.1 Calendar API

Base path: `/api/v1/calendar`

| Method | Path | Auth | Version | Description |
| --- | --- | --- | --- | --- |
| GET | `/calendar/options` | Access Token | v0.4.1 | List schedule creation options |
| POST | `/calendar/events` | Access Token | v0.4.1 | Create schedule event |
| GET | `/calendar/events` | Access Token | v0.4.1 | List schedule events for month/week/list ranges |
| GET | `/calendar/events/{eventId}` | Access Token | v0.4.1 | Get schedule event detail |
| PATCH | `/calendar/events/{eventId}` | Access Token | v0.4.1 | Update schedule event |
| DELETE | `/calendar/events/{eventId}` | Access Token | v0.4.1 | Archive schedule event |
| POST | `/calendar/events/{eventId}/status` | Access Token | v0.4.1 | Change schedule event status |
| GET | `/calendar/events/{eventId}/history` | Access Token | v0.4.1 | List schedule change history |
| POST | `/calendar/events/{eventId}/reminders` | Access Token | v0.4.1 | Create schedule reminder |
| GET | `/calendar/events/{eventId}/reminders` | Access Token | v0.4.1 | List schedule reminders |
| PATCH | `/calendar/events/{eventId}/reminders/{reminderId}` | Access Token | v0.4.1 | Update schedule reminder |
| DELETE | `/calendar/events/{eventId}/reminders/{reminderId}` | Access Token | v0.4.1 | Delete schedule reminder |
| GET | `/calendar/conflicts` | Access Token | v0.4.1 | List schedule conflicts |
| GET | `/calendar/upcoming` | Access Token | v0.4.1 | List upcoming schedules |

List query parameters: `start_from`, `start_to`, `event_type`, `status`, `confidence`, `application_id`, `job_id`, `has_reminder`, `include_archived`, `keyword`, `page`, `size`, `sort`, `order`.

Time policy:

- Requests and responses use ISO 8601.
- `start_at` and `end_at` must be timezone-aware.
- Stored datetime is UTC.
- `start_at < end_at` is required.
