# Database 설계 개요

상세 DB 문서는 [docs/06_database/database-design.md](../06_database/database-design.md)를 기준으로 한다.

## 현재 기준

- 버전: v0.3.0
- Migration head: `20260719_1500`
- DB: PostgreSQL
- ORM: SQLAlchemy
- Migration: Alembic

## 현재 구현 테이블

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
resumes
resume_files
```

## 설계 원칙

- 사용자 소유 데이터는 `user_id`로 분리한다.
- token/secret 원문은 DB에 저장하지 않는다.
- 상태값은 Enum으로 제한한다.
- DB 변경은 Alembic migration으로만 반영한다.
- AI 분석은 current result와 run history를 분리한다.
- 업로드 파일은 원본 파일명과 내부 저장명을 분리한다.
