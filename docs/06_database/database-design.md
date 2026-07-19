# Database Design

## Base policy

- Datetime values are stored in UTC.
- User-owned data has `user_id`.
- Schema changes are managed with Alembic migrations.
- Current migration head: `20260719_2000`.

## Main tables

| Domain | Tables |
| --- | --- |
| Auth | `users`, `refresh_tokens`, `email_verification_tokens`, `password_reset_tokens`, `security_events` |
| OAuth | `oauth_accounts`, `oauth_states`, `oauth_login_tickets` |
| Profile | `career_profiles`, `skills`, `user_skills`, `experiences`, `projects`, `job_preferences`, `excluded_conditions`, `portfolio_links` |
| Jobs | `companies`, `job_postings`, `job_analyses`, `job_analysis_runs`, `job_matches`, `job_match_runs`, `job_match_feedback` |
| Resumes | `resumes`, `resume_files`, `resume_file_extractions`, `resume_extraction_runs`, `resume_analyses`, `resume_analysis_runs` |
| Documents | `application_documents`, `application_document_versions`, `application_document_sources`, `generation_runs` |
| Applications | `applications`, `application_status_history`, `application_notes` |
| Calendar | `schedule_events`, `schedule_reminders`, `schedule_event_history` |

## v0.4.1 Schedule Tables

### `schedule_events`

Stores user schedule events linked to applications and job postings.

| Column | Type | Notes |
| --- | --- | --- |
| `id` | integer PK | Schedule event ID |
| `user_id` | FK users.id | Owner user |
| `application_id` | FK applications.id nullable | Linked application |
| `job_id` | FK job_postings.id nullable | Linked job posting |
| `title` | string(200) | Event title |
| `description` | text nullable | Event description |
| `event_type` | enum | Event type |
| `status` | enum | Event status |
| `confidence` | enum | Event confidence |
| `start_at` | timestamptz | UTC start time |
| `end_at` | timestamptz | UTC end time |
| `all_day` | boolean | All-day flag |
| `timezone` | string(64) | Display timezone |
| `location` | string(200) nullable | Offline location |
| `online_url` | string(1000) nullable | Online meeting URL |
| `source` | string(120) nullable | Input source |
| `source_reference` | string(500) nullable | Source reference |
| `is_archived` | boolean | Archive flag |
| `completed_at` | timestamptz nullable | Completion time |
| `cancelled_at` | timestamptz nullable | Cancellation time |
| `confirmation_required` | boolean | User confirmation flag |
| `created_at` | timestamptz | Created time |
| `updated_at` | timestamptz | Updated time |

### `schedule_reminders`

Stores reminder settings. v0.4.1 implements persistence and UI display only; real delivery is deferred.

### `schedule_event_history`

Stores schedule creation, update, status change, reminder change, completion, cancellation, and archive history.

Migration file: `backend/alembic/versions/20260719_2000_create_schedule_tables.py`
# v0.4.2 Dashboard Database Note

v0.4.2 대시보드는 신규 테이블, 컬럼, 인덱스를 추가하지 않는다.

현재 migration head는 `20260719_2000`이며, 대시보드는 다음 기존 테이블을 읽기 전용으로 조회해 집계한다.

- `applications`
- `application_status_history`
- `schedule_events`
- `job_postings`
- `job_analyses`
- `job_matches`
- `resume_analyses`
- `resume_files`
- `application_documents`

대시보드 조회는 사용자 소유권(`user_id`)을 기준으로 제한하며, 아카이브된 지원 항목과 취소/아카이브된 일정은 주요 집계에서 제외한다.
