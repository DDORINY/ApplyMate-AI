# Database Design Overview

문서 기준 버전: `v0.4.0`

상세 DB 문서는 [docs/06_database/database-design.md](../06_database/database-design.md)를 기준으로 한다.

## 현재 기준

- DB: PostgreSQL
- ORM: SQLAlchemy
- Migration: Alembic
- 현재 migration head: `20260719_1900`

## 현재 구현 테이블

```text
users
refresh_tokens
email_verification_tokens
password_reset_tokens
security_events
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
companies
job_postings
job_analyses
job_analysis_runs
job_matches
job_match_runs
job_match_feedback
resumes
resume_files
resume_file_extractions
resume_extraction_runs
resume_analyses
resume_analysis_runs
application_documents
application_document_versions
application_document_sources
generation_runs
applications
application_status_history
application_notes
```

## 설계 원칙

- 사용자 소유 데이터는 `user_id`를 가진다.
- 사용자 소유 데이터 조회/수정은 현재 사용자 소유권을 검증한다.
- 상태값은 Enum 또는 제한된 값으로 관리한다.
- DB 변경은 Alembic migration으로만 반영한다.
- AI 결과는 현재 결과와 실행 이력을 분리한다.
- 업로드 파일은 원본 파일명과 내부 저장명을 분리한다.
- 지원 항목은 제출 문서 버전을 `application_document_version_id`로 고정한다.

## v0.4.1 예상 확장

v0.4.1 일정 관리에서는 다음 테이블을 추가할 예정이다.

```text
schedule_events
schedule_reminders
schedule_event_history
```
