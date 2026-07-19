# Database Design

## v0.5.1 Gmail Recruitment Email Analysis Database

v0.5.1은 Gmail 채용 메일 분석 후보 생성을 위해 다음 테이블을 추가한다.

- `gmail_oauth_states`: Gmail OAuth state hash, redirect path, expiry, consumed timestamp
- `gmail_connections`: Gmail 연결 상태, search query, lookback days, sync enabled, last sync timestamp
- `email_sync_runs`: scanned, matched, candidate, ignored, error count를 가진 Gmail 동기화 실행 이력
- `email_messages`: 메일 metadata, snippet, 제한된 sanitized text/hash. `connection_id + provider_message_id` unique
- `email_analysis_runs`: 분석 provider/model/prompt/schema/input hash/result snapshot
- `email_candidates`: candidate type, status, company/job, event/status payload, evidence, confidence, review flag
- `email_candidate_actions`: 승인, 거절, 지원 항목 연결, 상태 변경, 일정 생성 action 이력

Migration:

- 신규 revision: `20260719_2200`
- 이전 revision: `20260719_2100`

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

# v0.5.0 Google Calendar Integration Database

v0.5.0은 Google Calendar 연동 기반을 위해 다음 테이블을 추가한다.

## calendar_oauth_states

- Calendar OAuth 전용 CSRF state 저장
- state 원문은 저장하지 않고 hash만 저장
- 만료와 1회 사용(`consumed_at`) 적용

## external_accounts

- Calendar 연동용 외부 계정
- 로그인 OAuth 계정(`oauth_accounts`)과 분리
- access/refresh token은 암호화된 값만 저장
- `provider + purpose + provider_account_id` unique
- `user_id + provider + purpose` unique

## calendar_connections

- 사용자의 Calendar 연결 상태와 선택 Calendar 저장
- `sync_direction`
- `sync_enabled`
- `status`
- `last_sync_at`

## calendar_sync_mappings

- 내부 `schedule_events`와 외부 Calendar event 매핑
- `connection_id + schedule_event_id` unique
- `connection_id + external_event_id` unique
- 내부/외부 hash, etag, sync status 저장

## sync_runs

- 동기화 실행 이력
- 생성/수정/삭제/skip/conflict/error count 저장

## sync_errors

- 사용자에게 노출 가능한 safe error만 저장
- token, provider raw response, secret은 저장하지 않음

## Migration

- 신규 revision: `20260719_2100`
- 이전 revision: `20260719_2000`
