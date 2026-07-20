# Database Design Overview

문서 기준 버전: `v1.0.0`
최신 migration head: `20260720_0300`

상세 DB 문서는 [docs/06_database/database-design.md](../06_database/database-design.md)를 기준으로 한다. v1.0.0은 신규 migration을 추가하지 않고 v0.9.0의 `audit_logs`까지 포함한 schema를 MVP 기준으로 확정한다.

## 기술 기준

- DB: PostgreSQL
- ORM: SQLAlchemy
- Migration: Alembic
- Cache/worker support: Redis
- 날짜/시간 저장: UTC 기준
- 사용자 소유 데이터: `user_id` 기반 소유권 검증

## 주요 테이블

```text
users
refresh_tokens
email_verification_tokens
password_reset_tokens
security_events
audit_logs
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
job_recommendation_runs
job_recommendations
job_recommendation_reasons
job_recommendation_feedback
job_recommendation_settings
job_recommendation_snapshots
job_recommendation_snapshot_items
recommendation_notification_candidates
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
document_improvement_runs
document_improvement_suggestions
document_improvement_sources
document_improvement_actions
notification_settings
notifications
notification_deliveries
notification_processing_runs
applications
application_status_history
application_notes
schedule_events
schedule_reminders
schedule_event_history
calendar_oauth_states
external_accounts
calendar_connections
calendar_sync_mappings
sync_runs
sync_errors
gmail_oauth_states
gmail_connections
email_sync_runs
email_messages
email_analysis_runs
email_candidates
email_candidate_actions
```

## 설계 원칙

- 모든 사용자 소유 데이터는 현재 사용자 기준으로 조회·수정·삭제 권한을 검증한다.
- 상태값은 자유 문자열이 아니라 제한된 enum/상수 값으로 관리한다.
- DB 변경은 Alembic migration으로만 반영한다.
- AI 결과는 결과 본문과 실행 이력, provider metadata, 근거 정보를 분리해 저장한다.
- 업로드 파일은 원본 파일명과 내부 저장명을 분리하고, 경로 조작을 방지한다.
- 제출된 지원 문서는 `application_document_version_id`로 고정해 이후 문서 변경과 분리한다.
- 문서 개선 루프는 기존 버전을 직접 수정하지 않고, 사용자 승인 후 새 버전을 생성한다.
- 알림 중복은 `deduplication_key`와 처리 이력으로 방지한다.
- 운영 전 backup/restore 절차를 확인하고, migration downgrade 가능성을 검토한다.

## v1.0.0 DB 변경

- 신규 테이블/컬럼 없음
- 최신 head: `20260720_0300`
- 검증: Docker Compose 환경에서 `upgrade head`, `downgrade -1`, `upgrade head` 왕복 확인
