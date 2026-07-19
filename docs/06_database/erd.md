# ERD

문서 기준 버전: `v0.4.0`

## 1. 인증/계정

```text
users 1 ── N refresh_tokens
users 1 ── N email_verification_tokens
users 1 ── N password_reset_tokens
users 1 ── N security_events
users 1 ── N oauth_accounts
users 1 ── N oauth_states
users 1 ── N oauth_login_tickets
```

## 2. 커리어 프로필

```text
users 1 ── 1 career_profiles
users 1 ── N user_skills
skills 1 ── N user_skills
users 1 ── N experiences
users 1 ── N projects
projects 1 ── N project_skills
skills 1 ── N project_skills
users 1 ── N job_preferences
users 1 ── N excluded_conditions
users 1 ── N portfolio_links
```

## 3. 채용공고/분석/적합도

```text
users 1 ── N job_postings
companies 1 ── N job_postings
job_postings 1 ── 1 job_analyses
job_postings 1 ── N job_analysis_runs
job_analyses 1 ── N job_analysis_runs
job_postings 1 ── 1 job_matches
job_analyses 1 ── N job_matches
job_matches 1 ── N job_match_runs
job_matches 1 ── N job_match_feedback
```

## 4. 이력서

```text
users 1 ── N resumes
resumes 1 ── N resume_files
resume_files 1 ── 1 resume_file_extractions
resume_file_extractions 1 ── N resume_extraction_runs
resume_files 1 ── 1 resume_analyses
resume_analyses 1 ── N resume_analysis_runs
```

## 5. 지원 문서

```text
users 1 ── N application_documents
job_postings 1 ── N application_documents
resumes 1 ── N application_documents
resume_files 1 ── N application_documents
resume_analyses 1 ── N application_documents
job_analyses 1 ── N application_documents
job_matches 1 ── N application_documents
application_documents 1 ── N application_document_versions
application_documents 1 ── N application_document_sources
application_document_versions 1 ── N application_document_sources
application_documents 1 ── N generation_runs
```

## 6. 지원 현황

```text
users 1 ── N applications
job_postings 1 ── N applications
resumes 1 ── N applications
resume_files 1 ── N applications
application_documents 1 ── N applications
application_document_versions 1 ── N applications
applications 1 ── N application_status_history
applications 1 ── N application_notes
```

## 7. v0.4.1 예정

```text
users 1 ── N schedule_events
applications 1 ── N schedule_events
schedule_events 1 ── N schedule_reminders
schedule_events 1 ── N schedule_event_history
```
