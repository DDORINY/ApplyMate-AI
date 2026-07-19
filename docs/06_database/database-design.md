# Database 설계

## 기준

- 현재 버전: v0.2.2
- 현재 migration head: `20260719_1400`
- ORM: SQLAlchemy
- Migration: Alembic
- DB: PostgreSQL

## Migration 목록

| 버전 | 파일 | 목적 |
| --- | --- | --- |
| v0.1.1 | `20260718_1501_create_auth_tables.py` | users, refresh_tokens |
| v0.1.2 | `20260718_1900_create_career_profile_tables.py` | 커리어 프로필 도메인 |
| v0.1.3 | `20260718_2100_add_social_auth.py` | OAuth 계정/state/ticket |
| v0.1.4 | `20260719_1000_add_account_security.py` | 이메일 인증/비밀번호 복구/보안 이벤트 |
| v0.2.0 | `20260719_1200_create_job_posting_tables.py` | 회사/채용공고 |
| v0.2.1 | `20260719_1300_create_job_analysis_tables.py` | 공고 분석/분석 실행 이력 |
| v0.2.2 | `20260719_1400_create_job_match_tables.py` | 적합도 분석/실행 이력/피드백 |

## 공통 설계 원칙

- 사용자 소유 데이터는 `user_id`를 가진다.
- 보호 API는 현재 인증 사용자의 `user_id`로 소유권을 검증한다.
- token 원문은 저장하지 않고 hash만 저장한다.
- 상태값은 Enum으로 제한한다.
- 주요 데이터는 생성/수정 시각을 가진다.
- schema 변경은 Alembic migration으로만 관리한다.

## users

사용자 계정 테이블.

주요 컬럼:

- `id`
- `email`
- `password_hash`
- `name`
- `email_verified`
- `status`
- `last_login_at`
- `created_at`
- `updated_at`

## refresh_tokens

Refresh Token hash와 세션 정보를 저장한다.

주요 컬럼:

- `user_id`
- `token_hash`
- `session_id`
- `expires_at`
- `revoked_at`
- `last_used_at`
- `device_name`
- `user_agent`
- `ip_address_hash`

## OAuth 테이블

### oauth_accounts

사용자와 OAuth provider 계정 연결 정보.

- `(provider, provider_user_id)` unique
- `(user_id, provider)` unique
- provider access token은 저장하지 않는다.

### oauth_states

OAuth CSRF 방어용 state hash.

### oauth_login_tickets

Provider callback 이후 frontend가 token으로 교환하는 1회용 ticket hash.

## 커리어 프로필 테이블

### career_profiles

사용자당 1개의 기본 커리어 프로필.

### skills / user_skills

기술 master와 사용자 보유 기술. `skills.normalized_name`으로 중복을 줄인다.

### experiences

경력 데이터.

### projects / project_skills

프로젝트와 프로젝트 사용 기술 연결.

### job_preferences

희망 고용 형태, 지역, 회사 규모, 원격 선호, 최소 급여, 희망 직무, 우선 키워드.

### excluded_conditions

지원 제외 조건. v0.2.2 적합도 분석의 위험/제외 조건에 사용된다.

### portfolio_links

GitHub, 블로그, 포트폴리오 등 외부 링크.

## 채용공고 테이블

### companies

회사 기본 정보. 여러 사용자가 같은 회사를 등록할 수 있으므로 사용자 소유 테이블이 아니다.

### job_postings

사용자별 저장 채용공고.

주요 제약:

- `user_id + source_url` unique
- `user_id + content_hash` unique
- `user_id` index
- status/deadline/favorite/source type index

## AI 채용공고 분석 테이블

### job_analyses

공고별 현재 분석 결과. `job_posting_id` unique.

주요 컬럼:

- `status`
- `schema_version`
- `prompt_version`
- `input_hash`
- `input_length`
- `summary`
- `position_data`
- `responsibilities`
- `required_qualifications`
- `preferred_qualifications`
- `technical_skills`
- `experience_data`
- `education_data`
- `work_conditions`
- `recruitment_process`
- `deadline_data`
- `company_values`
- `keywords`
- `warnings`
- `confidence`
- `is_user_edited`

### job_analysis_runs

분석 실행 이력. provider, model, token 사용량, latency, 오류 정보를 저장한다.

## 사용자-공고 적합도 테이블

### job_matches

공고별 현재 적합도 분석 결과.

주요 컬럼:

- `total_score`
- `grade`
- `recommendation_status`
- `role_score`
- `skill_score`
- `experience_score`
- `project_score`
- `preference_score`
- `risk_score`
- `matched_skills`
- `missing_skills`
- `matched_projects`
- `strengths`
- `gaps`
- `risks`
- `profile_hash`
- `job_analysis_hash`
- `calculation_version`
- `explanation_provider`

제약:

- `(user_id, job_posting_id)` unique
- 점수 컬럼 0~100 check constraint

### job_match_runs

적합도 분석 실행 이력.

### job_match_feedback

사용자 피드백.

피드백 타입:

- `ACCURATE`
- `TOO_HIGH`
- `TOO_LOW`
- `MISSING_STRENGTH`
- `MISSING_RISK`
- `OTHER`

## 현재 테이블 목록

```text
users
refresh_tokens
oauth_accounts
oauth_states
oauth_login_tickets
career_profiles
skills
user_skills
experiences
projects
project_skills
job_preferences
excluded_conditions
portfolio_links
email_verification_tokens
password_reset_tokens
security_events
companies
job_postings
job_analyses
job_analysis_runs
job_matches
job_match_runs
job_match_feedback
```
