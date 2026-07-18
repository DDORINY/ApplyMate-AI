# ERD

v0.1.3 기준 핵심 관계입니다.

```mermaid
erDiagram
  users ||--o{ refresh_tokens : has
  users ||--o{ oauth_accounts : links
  users ||--o{ oauth_states : creates
  users ||--o{ oauth_login_tickets : receives
  users ||--o| career_profiles : owns
  users ||--o{ user_skills : owns
  users ||--o{ experiences : owns
  users ||--o{ projects : owns
  users ||--o| job_preferences : owns
  users ||--o{ excluded_conditions : owns
  users ||--o{ portfolio_links : owns

  skills ||--o{ user_skills : referenced_by
  projects ||--o{ project_skills : uses
  skills ||--o{ project_skills : referenced_by

  users {
    bigint id PK
    string email UK
    string password_hash
    string name
    enum status
    boolean email_verified
    datetime last_login_at
    datetime created_at
    datetime updated_at
  }

  refresh_tokens {
    bigint id PK
    bigint user_id FK
    string token_hash UK
    string token_id UK
    datetime expires_at
    datetime revoked_at
    datetime created_at
  }

  oauth_accounts {
    bigint id PK
    bigint user_id FK
    enum provider
    string provider_user_id
    string provider_email
    string provider_username
    string provider_display_name
    boolean email_verified
    datetime last_login_at
    datetime created_at
    datetime updated_at
  }

  oauth_states {
    bigint id PK
    string state_hash UK
    enum provider
    enum purpose
    bigint user_id FK
    string redirect_path
    datetime expires_at
    datetime consumed_at
  }

  oauth_login_tickets {
    bigint id PK
    string ticket_hash UK
    bigint user_id FK
    enum provider
    string redirect_path
    datetime expires_at
    datetime consumed_at
  }

  career_profiles {
    bigint id PK
    bigint user_id FK
    string display_name
    string headline
    enum career_level
    int years_of_experience
    string desired_job_title
  }

  skills {
    bigint id PK
    string name
    string normalized_name UK
    enum category
  }

  user_skills {
    bigint id PK
    bigint user_id FK
    bigint skill_id FK
    enum proficiency_level
    int years_of_experience
    boolean is_primary
  }

  experiences {
    bigint id PK
    bigint user_id FK
    string company_name
    string position
    enum employment_type
    date start_date
    date end_date
    boolean is_current
  }

  projects {
    bigint id PK
    bigint user_id FK
    string name
    string summary
    string role
    date start_date
    date end_date
    boolean is_ongoing
  }

  project_skills {
    bigint id PK
    bigint project_id FK
    bigint skill_id FK
  }

  job_preferences {
    bigint id PK
    bigint user_id FK
    json preferred_employment_types
    json preferred_locations
    json preferred_company_sizes
    enum remote_preference
    int minimum_salary
  }

  excluded_conditions {
    bigint id PK
    bigint user_id FK
    enum condition_type
    string value
    boolean is_active
  }

  portfolio_links {
    bigint id PK
    bigint user_id FK
    enum link_type
    string title
    string url
    boolean is_primary
  }
```

## OAuth unique constraints

- `oauth_accounts(provider, provider_user_id)`는 provider 계정의 전역 중복 연결을 방지합니다.
- `oauth_accounts(user_id, provider)`는 사용자당 provider 1개만 연결하도록 제한합니다.
- `oauth_states.state_hash`, `oauth_login_tickets.ticket_hash`는 1회용 값을 hash로만 저장합니다.
