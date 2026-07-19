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
| Dashboard | `/dashboard` | v0.4.2 | Read-only application dashboard |

## v0.4.2 Dashboard API

Base path: `/api/v1/dashboard`

| Method | Path | Auth | Version | Description |
| --- | --- | --- | --- | --- |
| GET | `/dashboard` | Access Token | v0.4.2 | Aggregate current user dashboard data |

### Query parameters

| Name | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `period` | `7d`, `30d`, `90d`, `all`, `custom` | No | `30d` | Activity aggregation period. |
| `start_date` | `YYYY-MM-DD` | No | - | Custom period start date. Must be used with `end_date`. |
| `end_date` | `YYYY-MM-DD` | No | - | Custom period end date. Must be used with `start_date`. |
| `timezone` | IANA timezone | No | `Asia/Seoul` | Timezone for today/week/custom date boundaries. |
| `recent_limit` | integer `1~20` | No | `5` | Maximum items per recent/deadline widget. |

When `start_date` and `end_date` are provided, they override `period` for activity aggregation.

### Response data

```json
{
  "summary": {
    "total_applications": 6,
    "preparing_applications": 1,
    "in_progress_applications": 2,
    "interview_applications": 1,
    "offer_applications": 1,
    "rejected_applications": 1,
    "withdrawn_applications": 0,
    "closed_applications": 0,
    "week_events": 3,
    "upcoming_deadlines": 1,
    "due_soon_jobs": 1
  },
  "application_status_counts": [],
  "application_activity": {},
  "today_events": [],
  "week_events": [],
  "upcoming_deadlines": [],
  "due_soon_jobs": [],
  "preparing_applications": [],
  "recent_job_analyses": [],
  "recent_matches": [],
  "recent_resume_analyses": [],
  "recent_documents": [],
  "recent_activities": [],
  "generated_at": "2026-07-20T00:00:00Z",
  "timezone": "Asia/Seoul",
  "period": "30d",
  "period_start": "2026-06-20T00:00:00Z",
  "period_end": "2026-07-20T00:00:00Z"
}
```

### Status grouping

The backend owns grouping logic.

| Dashboard group | Application statuses |
| --- | --- |
| `PREPARING` | `SAVED`, `PREPARING` |
| `APPLIED` | `APPLIED` |
| `IN_PROGRESS` | `DOCUMENT_REVIEW`, `CODING_TEST`, `ASSIGNMENT` |
| `INTERVIEW` | `INTERVIEW`, `FINAL_INTERVIEW` |
| `OFFER` | `OFFER` |
| `REJECTED` | `REJECTED` |
| `WITHDRAWN` | `WITHDRAWN` |
| `CLOSED` | `CLOSED` |

### Ownership and filtering rules

- Every widget is scoped to `current_user.id`.
- Archived applications are excluded from counts and recent application activity.
- Archived/cancelled schedule events are excluded from dashboard schedule widgets.
- Today and week widgets use timezone-aware boundaries.
- Deadline widgets use a 7-day upcoming window.

## v0.4.1 Calendar API

Base path: `/api/v1/calendar`

| Method | Path | Auth | Version | Description |
| --- | --- | --- | --- | --- |
| GET | `/calendar/options` | Access Token | v0.4.1 | List schedule creation options |
| POST | `/calendar/events` | Access Token | v0.4.1 | Create schedule event |
| GET | `/calendar/events` | Access Token | v0.4.1 | List schedule events |
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
