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
| Calendar Integration | `/integrations/calendar` | v0.5.0 | Google Calendar connection and sync |
| Gmail Integration | `/integrations/gmail`, `/email-candidates` | v0.5.1 | Gmail recruitment email analysis candidates |
| Job Recommendations | `/recommendations/jobs` | v0.6.0 | Rule-based saved job recommendations |
| Recommendation Automation | `/recommendations/settings`, `/recommendations/jobs/snapshots`, `/recommendation-notifications` | v0.6.1 | Recommendation settings, snapshots, change detection, notification candidates |

## v0.6.1 Recommendation Automation API

Base path: `/api/v1`

| Method | Path | Auth | Version | Description |
| --- | --- | --- | --- | --- |
| GET | `/recommendations/settings` | Access Token | v0.6.1 | Get user's recommendation execution settings |
| PATCH | `/recommendations/settings` | Access Token | v0.6.1 | Update recommendation execution settings |
| POST | `/recommendations/jobs/run-if-due` | Access Token | v0.6.1 | Run recommendation generation only when execution conditions are met, or when forced by the user |
| GET | `/recommendations/jobs/snapshots` | Access Token | v0.6.1 | List recommendation snapshots |
| GET | `/recommendations/jobs/snapshots/{snapshotId}` | Access Token | v0.6.1 | Get one recommendation snapshot |
| GET | `/recommendations/jobs/changes` | Access Token | v0.6.1 | List snapshot item changes |
| GET | `/recommendation-notifications` | Access Token | v0.6.1 | List recommendation notification candidates |
| PATCH | `/recommendation-notifications/{notificationId}` | Access Token | v0.6.1 | Mark notification candidate as read, dismissed, pending, or expired |
| DELETE | `/recommendation-notifications/{notificationId}` | Access Token | v0.6.1 | Dismiss notification candidate |

Rules:

- v0.6.1 stores notification candidates only; it does not send email or push notifications.
- `run-if-due` is authenticated and is not a public scheduler endpoint.
- The default execution setting is disabled and `MANUAL`.
- Backend owns change detection; Frontend does not calculate score deltas.
- External job crawling, AI/ML recommendation calls, and automatic application submission remain excluded.

## v0.6.0 Rule-based Job Recommendations API

Base path: `/api/v1/recommendations/jobs`

| Method | Path | Auth | Version | Description |
| --- | --- | --- | --- | --- |
| POST | `/generate` | Access Token | v0.6.0 | Generate rule-based recommendations from saved jobs |
| GET | `` | Access Token | v0.6.0 | List recommendations with filters |
| GET | `/{recommendationId}` | Access Token | v0.6.0 | Get recommendation detail |
| POST | `/{recommendationId}/feedback` | Access Token | v0.6.0 | Create or update user feedback |
| DELETE | `/{recommendationId}/feedback` | Access Token | v0.6.0 | Delete user feedback |
| POST | `/{recommendationId}/refresh` | Access Token | v0.6.0 | Recalculate one recommendation |
| GET | `/runs` | Access Token | v0.6.0 | List recommendation generation runs |
| GET | `/runs/{runId}` | Access Token | v0.6.0 | Get one generation run |
| GET | `/policy` | Access Token | v0.6.0 | Get rule-based policy and weights |

Rules:

- Recommendation type is always `RULE_BASED`.
- No AI, machine learning, external crawling, or automatic application submission is used.
- Scores are calculated by backend only.
- User ownership is checked for recommendation, run, feedback, and job data.
- Hidden and not-interested feedback can exclude jobs from later generation.

## v0.5.1 Gmail Integration API

Base path: `/api/v1`

| Method | Path | Auth | Version | Description |
| --- | --- | --- | --- | --- |
| GET | `/integrations/gmail/status` | Access Token | v0.5.1 | Get Gmail connection status |
| POST | `/integrations/gmail/connect` | Access Token | v0.5.1 | Create Gmail OAuth authorization URL |
| GET | `/integrations/gmail/callback` | OAuth state | v0.5.1 | Complete Gmail OAuth callback |
| PATCH | `/integrations/gmail/settings` | Access Token | v0.5.1 | Update Gmail search/sync settings |
| DELETE | `/integrations/gmail/connection` | Access Token | v0.5.1 | Disconnect Gmail integration |
| POST | `/integrations/gmail/sync` | Access Token | v0.5.1 | Search and analyze Gmail messages |
| GET | `/integrations/gmail/sync-runs` | Access Token | v0.5.1 | List Gmail sync runs |
| GET | `/integrations/gmail/sync-runs/{runId}` | Access Token | v0.5.1 | Get Gmail sync run detail |
| GET | `/email-candidates` | Access Token | v0.5.1 | List email candidates |
| GET | `/email-candidates/{candidateId}` | Access Token | v0.5.1 | Get email candidate detail |
| POST | `/email-candidates/{candidateId}/approve` | Access Token | v0.5.1 | Approve candidate actions |
| POST | `/email-candidates/{candidateId}/reject` | Access Token | v0.5.1 | Reject candidate |
| POST | `/email-candidates/{candidateId}/link-application` | Access Token | v0.5.1 | Link candidate to application |
| GET | `/email-candidates/{candidateId}/application-options` | Access Token | v0.5.1 | Suggest application links |

Security rules:

- Gmail OAuth is separate from login and Calendar OAuth.
- Gmail uses read-only scope only.
- Token values and raw provider errors are never returned.
- Status changes and schedule creation require explicit approval request flags.
- Actual Gmail API calls remain `NEEDS_VERIFICATION`.

## v0.5.0 Calendar Integration API

Base path: `/api/v1`

| Method | Path | Auth | Version | Description |
| --- | --- | --- | --- | --- |
| GET | `/integrations/calendar/status` | Access Token | v0.5.0 | Get current Calendar connection status |
| POST | `/integrations/calendar/connect` | Access Token | v0.5.0 | Create Calendar OAuth authorization URL |
| GET | `/integrations/calendar/callback` | OAuth state | v0.5.0 | Complete Calendar OAuth callback |
| GET | `/integrations/calendar/calendars` | Access Token | v0.5.0 | List provider calendars |
| PATCH | `/integrations/calendar/settings` | Access Token | v0.5.0 | Select calendar and sync direction |
| DELETE | `/integrations/calendar/connection` | Access Token | v0.5.0 | Disconnect Calendar integration |
| POST | `/integrations/calendar/sync` | Access Token | v0.5.0 | Sync internal schedules to selected Calendar |
| GET | `/integrations/calendar/sync-runs` | Access Token | v0.5.0 | List sync runs |
| GET | `/integrations/calendar/errors` | Access Token | v0.5.0 | List safe sync errors |
| POST | `/calendar/events/{eventId}/sync` | Access Token | v0.5.0 | Sync one internal schedule event |
| GET | `/calendar/events/{eventId}/sync-status` | Access Token | v0.5.0 | Get one event sync mapping/status |

Security rules:

- Login OAuth and Calendar OAuth are separate flows.
- Calendar token values are never returned by API.
- All connection, mapping, run, and error data is scoped by `current_user.id`.
- Actual Google Calendar API calls require operational credentials and remain `NEEDS_VERIFICATION`.

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
