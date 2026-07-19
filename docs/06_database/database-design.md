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
# v0.2.0 채용공고 데이터베이스

## companies

기업 기본 정보를 저장한다. 여러 사용자가 같은 기업의 공고를 등록할 수 있으므로 사용자 소유 테이블이 아니다.

| 컬럼 | 타입 | 설명 |
| --- | --- | --- |
| `id` | bigint pk | 기업 ID |
| `name` | varchar(160) | 표시 기업명 |
| `normalized_name` | varchar(160), unique | 중복 재사용을 위한 정규화 기업명 |
| `website_url` | varchar(500), nullable | 기업 홈페이지 |
| `industry` | varchar(120), nullable | 산업 |
| `company_size` | enum | 기업 규모 |
| `description` | text, nullable | 기업 설명 |
| `created_at` | timestamptz | 생성일 |
| `updated_at` | timestamptz | 수정일 |

## job_postings

사용자별 채용공고 보관함이다. 모든 조회/수정/삭제는 `user_id` 소유권 검사를 수행한다.

| 컬럼 | 타입 | 설명 |
| --- | --- | --- |
| `id` | bigint pk | 채용공고 ID |
| `user_id` | bigint fk users.id | 소유 사용자 |
| `company_id` | bigint fk companies.id | 기업 |
| `title` | varchar(200) | 공고 제목 |
| `position` | varchar(160), nullable | 직무 |
| `employment_type` | enum | 고용 형태 |
| `career_requirement` | varchar(255), nullable | 경력 조건 |
| `education_requirement` | varchar(255), nullable | 학력 조건 |
| `location` | varchar(200), nullable | 근무 지역 |
| `work_type` | enum | 근무 형태 |
| `salary_min`, `salary_max` | integer, nullable | 급여 범위 |
| `salary_text` | varchar(200), nullable | 급여 설명 |
| `description` | text, nullable | 주요 업무/본문 |
| `requirements` | text, nullable | 필수 조건 |
| `preferred_qualifications` | text, nullable | 우대 조건 |
| `benefits` | text, nullable | 복지 |
| `recruitment_process` | text, nullable | 채용 절차 |
| `source_type` | enum | `MANUAL`, `URL` |
| `source_url` | varchar(1000), nullable | 원문 URL |
| `source_site` | varchar(120), nullable | 원문 host |
| `original_content` | text, nullable | URL에서 추출한 원문 텍스트 |
| `content_hash` | varchar(128) | 중복 감지용 hash |
| `published_at` | timestamptz, nullable | 게시일 |
| `deadline_at` | timestamptz, nullable | 마감일 |
| `deadline_type` | enum | 마감 유형 |
| `status` | enum | 관리 상태 |
| `is_favorite` | boolean | 관심 여부 |
| `notes` | text, nullable | 사용자 메모 |
| `collected_at` | timestamptz, nullable | URL 수집 시각 |
| `created_at` | timestamptz | 생성일 |
| `updated_at` | timestamptz | 수정일 |

## 중복 감지

- `user_id + source_url`
- `user_id + content_hash`
- `user_id + company_id + title + deadline_at`

다른 사용자는 같은 원문 URL의 공고를 각자 저장할 수 있다.

## Migration

```text
backend/alembic/versions/20260719_1200_create_job_posting_tables.py
```
# v0.2.1 AI 채용공고 분석

## job_analyses

채용공고별 현재 AI 분석 결과를 저장합니다.

- `id`: PK
- `job_posting_id`: `job_postings.id`, unique, cascade delete
- `user_id`: `users.id`, cascade delete
- `status`: `PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`
- `schema_version`, `prompt_version`
- `input_hash`, `input_length`
- `summary`
- `position_data`, `responsibilities`, `required_qualifications`, `preferred_qualifications`
- `technical_skills`, `experience_data`, `education_data`, `work_conditions`
- `recruitment_process`, `deadline_data`, `company_values`, `keywords`, `warnings`, `confidence`
- `is_user_edited`, `analyzed_at`, `created_at`, `updated_at`

## job_analysis_runs

분석 실행 이력을 저장합니다.

- `id`: PK
- `job_posting_id`, `job_analysis_id`, `user_id`
- `status`, `provider`, `model`
- `schema_version`, `prompt_version`, `input_hash`, `input_length`
- `request_id`, token 사용량, latency
- `error_code`, `error_message`, 선택적 `raw_response`
- `started_at`, `completed_at`, `created_at`

Migration: `backend/alembic/versions/20260719_1300_create_job_analysis_tables.py`
# v0.2.2 사용자-공고 적합도 분석

## job_matches

채용공고 1개에 대한 현재 적합도 분석 결과입니다.

| 컬럼 | 설명 |
| --- | --- |
| `id` | PK |
| `user_id` | 사용자 소유권 검사용 FK |
| `job_posting_id` | 대상 채용공고 FK |
| `job_analysis_id` | 사용한 공고 분석 FK |
| `status` | `PENDING`, `PROCESSING`, `COMPLETED`, `FAILED` |
| `total_score` | 0~100 종합 점수 |
| `grade` | `EXCELLENT`, `GOOD`, `MODERATE`, `LOW`, `VERY_LOW` |
| `recommendation_status` | 추천/검토/비추천/정보부족 상태 |
| `role_score` | 직무 적합도 점수 |
| `skill_score` | 기술 적합도 점수 |
| `experience_score` | 경력 적합도 점수 |
| `project_score` | 프로젝트 근거 점수 |
| `preference_score` | 희망 조건 일치 점수 |
| `risk_score` | 위험/제외 조건 점수 |
| `matched_skills`, `missing_skills`, `matched_projects` | JSON 근거 |
| `strengths`, `gaps`, `risks` | JSON 판단 근거 |
| `profile_hash`, `job_analysis_hash` | 최신성 판단 hash |
| `calculation_version` | 산식 버전 |
| `explanation_provider` | 설명 생성 방식 |

제약:

- `(user_id, job_posting_id)` unique
- 점수 컬럼은 0~100 check constraint

## job_match_runs

적합도 분석 실행 이력입니다. 재계산마다 새 run을 저장합니다.

## job_match_feedback

사용자 피드백입니다. 피드백 타입은 `ACCURATE`, `TOO_HIGH`, `TOO_LOW`, `MISSING_STRENGTH`, `MISSING_RISK`, `OTHER`입니다.

Migration: `backend/alembic/versions/20260719_1400_create_job_match_tables.py`
