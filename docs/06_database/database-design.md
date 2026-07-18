# 데이터베이스 설계

## 현재 구현 스키마

v0.1.2 기준 구현 테이블:

```text
users
refresh_tokens
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

v0.1.1:

```text
backend/alembic/versions/20260718_1501_create_auth_tables.py
```

v0.1.2:

```text
backend/alembic/versions/20260718_1900_create_career_profile_tables.py
```

v0.1.2 downgrade는 커리어 프로필 관련 테이블과 Enum만 제거한다. `users`, `refresh_tokens`는 유지한다.

## 공통 원칙

- 사용자 소유 데이터는 `user_id`를 기준으로 격리한다.
- 모든 보호 API는 현재 인증된 사용자의 데이터만 조회/수정한다.
- 날짜/시간은 timezone-aware UTC 기준으로 저장한다.
- 상태값은 Enum으로 제한한다.
- 중복 방지가 필요한 조합에는 unique constraint를 둔다.
- 자주 조회하는 `user_id`, FK, 정렬 기준에는 index를 둔다.
- 운영 데이터 삭제는 migration으로 임의 수행하지 않는다.

## career_profiles

사용자당 하나의 기본 커리어 프로필을 저장한다.

주요 컬럼:

```text
id
user_id
display_name
headline
career_level
years_of_experience
desired_job_title
introduction
created_at
updated_at
```

제약:

- `user_id` unique
- `users.id` FK, `ondelete=CASCADE`
- `years_of_experience >= 0`
- `career_level`: `ENTRY`, `JUNIOR`, `MID`, `SENIOR`, `CAREER_CHANGE`

## skills

기술 마스터 테이블이다.

주요 컬럼:

```text
id
name
normalized_name
category
created_at
```

제약:

- `normalized_name` unique
- `category`: `LANGUAGE`, `FRAMEWORK`, `DATABASE`, `AI_ML`, `DEVOPS`, `CLOUD`, `FRONTEND`, `BACKEND`, `TOOL`, `ETC`

## user_skills

사용자가 보유한 기술과 숙련도를 저장한다.

주요 컬럼:

```text
id
user_id
skill_id
proficiency_level
years_of_experience
is_primary
created_at
updated_at
```

제약:

- `(user_id, skill_id)` unique
- `users.id` FK, `ondelete=CASCADE`
- `skills.id` FK, `ondelete=RESTRICT`
- `proficiency_level`: `BEGINNER`, `INTERMEDIATE`, `ADVANCED`, `EXPERT`

## experiences

사용자 경력 이력을 저장한다.

주요 컬럼:

```text
id
user_id
company_name
position
employment_type
start_date
end_date
is_current
description
achievements
created_at
updated_at
```

제약:

- `users.id` FK, `ondelete=CASCADE`
- `employment_type`: `FULL_TIME`, `CONTRACT`, `INTERN`, `FREELANCE`, `PART_TIME`, `SELF_EMPLOYED`, `OTHER`
- 서비스 계층에서 시작일/종료일과 재직 중 정책을 검증한다.

## projects

사용자 프로젝트 경험을 저장한다.

주요 컬럼:

```text
id
user_id
name
summary
role
start_date
end_date
is_ongoing
description
responsibilities
achievements
repository_url
service_url
created_at
updated_at
```

제약:

- `users.id` FK, `ondelete=CASCADE`
- 서비스 계층에서 날짜 범위와 URL scheme을 검증한다.

## project_skills

프로젝트와 기술 마스터의 연결 테이블이다.

주요 컬럼:

```text
id
project_id
skill_id
created_at
```

제약:

- `(project_id, skill_id)` unique
- `projects.id` FK, `ondelete=CASCADE`
- `skills.id` FK, `ondelete=RESTRICT`

## job_preferences

사용자 희망 근무 조건을 저장한다.

주요 컬럼:

```text
id
user_id
preferred_employment_types
preferred_locations
preferred_company_sizes
remote_preference
minimum_salary
desired_roles
priority_keywords
created_at
updated_at
```

제약:

- `user_id` unique
- 배열 성격의 값은 JSON 컬럼으로 저장한다.
- `remote_preference`: `ONSITE`, `HYBRID`, `REMOTE`, `ANY`
- 서비스 계층에서 최소 연봉 음수를 차단한다.

## excluded_conditions

지원 제외 조건을 저장한다.

주요 컬럼:

```text
id
user_id
condition_type
value
reason
is_active
created_at
updated_at
```

제약:

- `(user_id, condition_type, value)` unique
- `condition_type`: `EMPLOYMENT_TYPE`, `LOCATION`, `COMPANY_SIZE`, `REQUIRED_SKILL`, `EXCLUDED_KEYWORD`, `MINIMUM_EXPERIENCE`, `EDUCATION_REQUIREMENT`, `OTHER`

## portfolio_links

포트폴리오, GitHub, 블로그 등 외부 링크를 저장한다.

주요 컬럼:

```text
id
user_id
link_type
title
url
is_primary
display_order
created_at
updated_at
```

제약:

- `(user_id, url)` unique
- `link_type`: `GITHUB`, `NOTION`, `PORTFOLIO`, `BLOG`, `LINKEDIN`, `OTHER`
- 서비스 계층에서 `http`, `https` URL만 허용한다.
- 대표 링크는 서비스 계층에서 사용자당 하나만 유지한다.

## 향후 스키마

- v0.2.x: `job_postings`, `companies`, `job_requirements`
- v0.2.x: `job_matches`, `match_findings`
- v0.3.x: `resumes`, `generated_documents`, `document_evidence`
- v0.4.x: `applications`, `calendar_events`
- v0.5.x: `external_accounts`, `calendar_sync_logs`
