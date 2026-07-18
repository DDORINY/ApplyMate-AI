# 데이터베이스 설계

## 현재 구현 스키마

v0.1.3 기준 구현 테이블:

```text
users
refresh_tokens
oauth_accounts
oauth_states
oauth_login_tickets
email_verification_tokens
password_reset_tokens
security_events
career_profiles
skills
user_skills
experiences
projects
project_skills
job_preferences
excluded_conditions
portfolio_links
```

## Migration

| 버전 | 파일 |
| --- | --- |
| v0.1.1 | `backend/alembic/versions/20260718_1501_create_auth_tables.py` |
| v0.1.2 | `backend/alembic/versions/20260718_1900_create_career_profile_tables.py` |
| v0.1.3 | `backend/alembic/versions/20260718_2100_add_social_auth.py` |
| v0.1.4 | `backend/alembic/versions/20260719_1000_add_account_security.py` |

## v0.1.4 계정 보안 테이블

### email_verification_tokens

이메일 인증용 1회용 token hash를 저장합니다. token 원문은 저장하지 않습니다.

- `user_id` FK, `ondelete=CASCADE`
- `token_hash` unique
- `expires_at`, `used_at`, `created_at`

### password_reset_tokens

비밀번호 재설정용 1회용 token hash를 저장합니다. token 원문은 저장하지 않습니다.

- `user_id` FK, `ondelete=CASCADE`
- `token_hash` unique
- `expires_at`, `used_at`, `created_at`

### security_events

로그인, 로그아웃, 비밀번호 변경, 이메일 인증 등 주요 보안 이벤트를 기록합니다.

- 민감 정보, token 원문, 비밀번호, secret은 저장하지 않습니다.
- `metadata`에는 민감하지 않은 제한된 JSON만 저장합니다.

### refresh_tokens 확장

세션 관리를 위해 다음 컬럼을 추가합니다.

- `session_id`
- `device_name`
- `user_agent`
- `ip_address_hash`
- `last_used_at`

v0.1.3 downgrade는 social-only 사용자(`users.password_hash IS NULL`)가 있으면 중단합니다. 비밀번호 없는 사용자가 남아 있는 상태에서 `users.password_hash`를 다시 NOT NULL로 되돌리면 데이터 정합성이 깨지기 때문입니다.

## 공통 원칙

- 사용자 소유 데이터는 `user_id`를 기준으로 격리합니다.
- 모든 보호 API는 현재 인증된 사용자의 데이터만 조회/수정합니다.
- 날짜/시간은 timezone-aware UTC 기준으로 저장합니다.
- 상태 값은 Enum으로 제한합니다.
- 중복 방지가 필요한 조합에는 unique constraint를 둡니다.
- 자주 조회하는 `user_id`, FK, 만료 시간, token/state hash에는 index를 둡니다.

## users

서비스 사용자 계정입니다.

주요 컬럼:

```text
id
email
password_hash
name
status
email_verified
last_login_at
created_at
updated_at
```

정책:

- `email`은 unique입니다.
- v0.1.3부터 `password_hash`는 nullable입니다. 소셜 로그인으로만 생성된 계정은 비밀번호가 없을 수 있습니다.
- `email_verified`는 provider 검증 이메일로 생성된 소셜 계정에서 true가 됩니다.

## refresh_tokens

Refresh Token의 원문이 아니라 hash를 저장합니다.

정책:

- refresh token rotation을 적용합니다.
- 로그아웃 또는 재발급 시 기존 token은 `revoked_at`으로 폐기합니다.

## oauth_accounts

사용자와 OAuth provider 계정의 연결 정보를 저장합니다. provider access token은 저장하지 않습니다.

주요 컬럼:

```text
id
user_id
provider
provider_user_id
provider_email
provider_username
provider_display_name
email_verified
created_at
updated_at
last_login_at
```

제약:

- `(provider, provider_user_id)` unique
- `(user_id, provider)` unique
- `users.id` FK, `ondelete=CASCADE`
- `provider`: `GOOGLE`, `GITHUB`

## oauth_states

OAuth CSRF 방지용 state의 hash와 목적을 임시 저장합니다.

주요 컬럼:

```text
id
state_hash
provider
purpose
user_id
redirect_path
created_at
expires_at
consumed_at
```

정책:

- state 원문은 DB에 저장하지 않고 hash만 저장합니다.
- `purpose`: `LOGIN`, `LINK`
- 만료 또는 이미 사용된 state는 거부합니다.

## oauth_login_tickets

Provider callback 이후 프론트가 서비스 토큰으로 교환하는 1회용 ticket의 hash입니다.

주요 컬럼:

```text
id
ticket_hash
user_id
provider
redirect_path
created_at
expires_at
consumed_at
```

정책:

- ticket 원문은 DB에 저장하지 않고 hash만 저장합니다.
- ticket은 1회만 사용할 수 있습니다.
- 기본 만료 시간은 60초입니다.

## career_profiles 이하

v0.1.2에서 구현된 커리어 프로필 도메인입니다.

- `career_profiles`: 사용자당 1개의 기본 커리어 프로필
- `skills`: 기술 마스터
- `user_skills`: 사용자 보유 기술과 숙련도
- `experiences`: 경력
- `projects`: 프로젝트
- `project_skills`: 프로젝트-기술 연결
- `job_preferences`: 희망 근무 조건
- `excluded_conditions`: 지원 제외 조건
- `portfolio_links`: GitHub, 블로그, 포트폴리오 등 외부 링크

## 향후 스키마

- v0.2.x: `job_postings`, `companies`, `job_requirements`
- v0.2.x: `job_matches`, `match_findings`
- v0.3.x: `resumes`, `generated_documents`, `document_evidence`
- v0.4.x: `applications`, `calendar_events`
- v0.5.x: `external_accounts`, `calendar_sync_logs`
