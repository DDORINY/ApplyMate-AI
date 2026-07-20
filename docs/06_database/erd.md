# ERD

## v0.8.0 Notification Operations ERD

```mermaid
erDiagram
    users ||--o| notification_settings : configures
    users ||--o{ notifications : receives
    notifications ||--o{ notification_deliveries : delivered_by

    notification_settings {
      int id PK
      int user_id FK
      bool in_app_enabled
      bool email_enabled
      bool push_enabled
      string timezone
      bool quiet_hours_enabled
    }

    notifications {
      int id PK
      int user_id FK
      string event_type
      string priority
      string status
      string source_type
      string source_id
      string deduplication_key
    }

    notification_deliveries {
      int id PK
      int notification_id FK
      int user_id FK
      string channel
      string status
      string provider
      int attempt_count
    }
```

## v0.7.0 Document Improvement ERD

```mermaid
erDiagram
    users ||--o{ document_improvement_runs : owns
    application_documents ||--o{ document_improvement_runs : improved_by
    application_document_versions ||--o{ document_improvement_runs : base_version
    document_improvement_runs ||--o{ document_improvement_suggestions : proposes
    document_improvement_runs ||--o{ document_improvement_sources : uses
    document_improvement_runs ||--o{ document_improvement_actions : records
    document_improvement_suggestions ||--o{ document_improvement_actions : acted_on

    document_improvement_runs {
      int id PK
      int user_id FK
      int application_document_id FK
      int base_version_id FK
      int result_version_id FK
      string status
      string improvement_type
      string provider
      string prompt_version
      string schema_version
      bool outdated
    }

    document_improvement_suggestions {
      int id PK
      int run_id FK
      int paragraph_index
      int sentence_index
      text original_text
      text suggested_text
      string risk_level
      string status
      bool selected
    }
```

## v0.6.1 Recommendation Automation ERD

```mermaid
erDiagram
    users ||--o| job_recommendation_settings : configures
    users ||--o{ job_recommendation_snapshots : owns
    job_recommendation_runs ||--o{ job_recommendation_snapshots : creates
    job_recommendation_snapshots ||--o{ job_recommendation_snapshot_items : contains
    job_recommendations ||--o{ job_recommendation_snapshot_items : captured_as
    job_recommendation_snapshots ||--o{ recommendation_notification_candidates : produces
    job_recommendation_snapshot_items ||--o{ recommendation_notification_candidates : explains

    job_recommendation_settings {
      int id PK
      int user_id FK
      bool enabled
      string frequency
      int preferred_run_hour
      string timezone
      int minimum_score
      bool exclude_applied_jobs
      bool exclude_hidden_jobs
      datetime last_run_at
      datetime next_run_at
    }

    job_recommendation_snapshots {
      int id PK
      int user_id FK
      int run_id FK
      string profile_hash
      string policy_version
      int recommended_count
      int new_count
      int changed_count
      int removed_count
      datetime generated_at
    }

    job_recommendation_snapshot_items {
      int id PK
      int snapshot_id FK
      int recommendation_id FK
      int job_id FK
      int score
      string grade
      int rank
      string change_type
      int previous_score
      int score_delta
      int rank_delta
      int data_completeness_score
      string recommendation_confidence
    }

    recommendation_notification_candidates {
      int id PK
      int user_id FK
      int recommendation_id FK
      int snapshot_id FK
      string notification_type
      string status
      string title
      json payload
    }
```

## v0.6.0 Job Recommendations ERD

```mermaid
erDiagram
    users ||--o{ job_recommendation_runs : owns
    users ||--o{ job_recommendations : receives
    users ||--o{ job_recommendation_feedback : records
    job_recommendation_runs ||--o{ job_recommendations : produces
    job_postings ||--o{ job_recommendations : recommended
    job_recommendations ||--o{ job_recommendation_reasons : explains
    job_recommendations ||--o{ job_recommendation_feedback : has

    job_recommendation_runs {
      int id PK
      int user_id FK
      string status
      string recommendation_type
      string policy_version
      int input_job_count
      int recommended_count
      int excluded_count
      int failed_count
      datetime started_at
      datetime completed_at
    }

    job_recommendations {
      int id PK
      int user_id FK
      int job_id FK
      int run_id FK
      int score
      string grade
      string status
      string recommendation_type
      bool has_blocking_mismatch
      string profile_hash
      string job_hash
      string policy_version
    }

    job_recommendation_reasons {
      int id PK
      int recommendation_id FK
      string reason_type
      string requirement_type
      string match_status
      string severity
      string label
      int score_delta
    }

    job_recommendation_feedback {
      int id PK
      int user_id FK
      int recommendation_id FK
      int job_id FK
      string feedback_type
      string feedback_reason
    }
```

## v0.5.1 Gmail Analysis ERD

```mermaid
erDiagram
    users ||--o{ external_accounts : owns
    external_accounts ||--o{ gmail_connections : has
    gmail_connections ||--o{ email_sync_runs : runs
    gmail_connections ||--o{ email_messages : messages
    email_messages ||--o{ email_analysis_runs : analyzed_by
    email_messages ||--o{ email_candidates : creates
    email_analysis_runs ||--o{ email_candidates : produces
    email_candidates ||--o{ email_candidate_actions : records
    applications ||--o{ email_candidates : linked
    applications ||--o{ email_candidate_actions : changed_by
    schedule_events ||--o{ email_candidate_actions : created_by
```

## v0.4.1 Schedule ERD

```mermaid
erDiagram
    users ||--o{ schedule_events : owns
    applications ||--o{ schedule_events : links
    job_postings ||--o{ schedule_events : links
    schedule_events ||--o{ schedule_reminders : has
    schedule_events ||--o{ schedule_event_history : records

    schedule_events {
      int id PK
      int user_id FK
      int application_id FK
      int job_id FK
      string title
      string event_type
      string status
      string confidence
      datetime start_at
      datetime end_at
      bool all_day
      string timezone
      bool is_archived
    }

    schedule_reminders {
      int id PK
      int event_id FK
      int user_id FK
      string reminder_type
      int minutes_before
      datetime scheduled_at
      string status
    }

    schedule_event_history {
      int id PK
      int event_id FK
      int user_id FK
      string action
      json previous_values
      json new_values
      json changed_fields
      string source
    }
```

## v0.5.0 Calendar Integration ERD

```mermaid
erDiagram
    users ||--o{ calendar_oauth_states : owns
    users ||--o{ external_accounts : owns
    external_accounts ||--o{ calendar_connections : authorizes
    calendar_connections ||--o{ calendar_sync_mappings : maps
    schedule_events ||--o{ calendar_sync_mappings : syncs
    calendar_connections ||--o{ sync_runs : records
    sync_runs ||--o{ sync_errors : records

    external_accounts {
      int id PK
      int user_id FK
      string provider
      string purpose
      string provider_account_id
      string email
      text access_token_encrypted
      text refresh_token_encrypted
      bool is_active
    }

    calendar_connections {
      int id PK
      int user_id FK
      int external_account_id FK
      string selected_calendar_id
      string sync_direction
      bool sync_enabled
      string status
    }

    calendar_sync_mappings {
      int id PK
      int user_id FK
      int connection_id FK
      int schedule_event_id FK
      string external_event_id
      string sync_status
      datetime last_synced_at
    }

    sync_runs {
      int id PK
      int user_id FK
      int connection_id FK
      string direction
      string status
      int created_count
      int updated_count
      int error_count
    }

    sync_errors {
      int id PK
      int user_id FK
      int connection_id FK
      int sync_run_id FK
      string error_code
      string safe_message
    }
```
