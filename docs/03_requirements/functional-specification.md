# Functional Specification

Current implemented version: `v0.4.1`

## Completed features

| ID | Feature | Status | Version |
| --- | --- | --- | --- |
| AUTH-001 | Signup, login, token refresh, logout, current user | Done | v0.1.1 |
| AUTH-002 | Google/GitHub OAuth login and account linking | Done | v0.1.3 |
| SECURITY-001 | Email verification, password recovery, sessions, security events | Done | v0.1.4 |
| PROFILE-001 | Career profile, experiences, projects, skills, preferences | Done | v0.1.2 |
| JOB-001 | Job posting CRUD and URL import | Done | v0.2.0 |
| AI-JOB-001 | AI job posting analysis | Done | v0.2.1 |
| MATCH-001 | User-job matching analysis | Done | v0.2.2 |
| RESUME-001 | Resume metadata and PDF/DOCX file management | Done | v0.3.0 |
| RESUME-EXTRACT-001 | Resume text extraction and user editing | Done | v0.3.1 |
| RESUME-AI-001 | AI resume structured analysis | Done | v0.3.2 |
| DOCUMENT-001 | Application document generation, versions, sources | Done | v0.3.3 |
| APPLICATION-001 | Application tracking, status history, notes, fixed submitted document version | Done | v0.4.0 |
| SCHEDULE-001 | Schedule create, list, detail, update, archive | Done | v0.4.1 |
| SCHEDULE-002 | Link schedules to applications and job postings | Done | v0.4.1 |
| SCHEDULE-003 | Schedule event type, status, confidence | Done | v0.4.1 |
| SCHEDULE-004 | Reminder create, list, update, delete | Done | v0.4.1 |
| SCHEDULE-005 | Month, week, and list views | Done | v0.4.1 |
| SCHEDULE-006 | Due-soon and overdue calculations | Done | v0.4.1 |
| SCHEDULE-007 | Time conflict detection and warning | Done | v0.4.1 |
| SCHEDULE-008 | Schedule change history | Done | v0.4.1 |
| SCHEDULE-009 | Ownership checks for all schedule resources | Done | v0.4.1 |

## v0.4.1 exclusions

- Recurring schedules
- Real Google Calendar event creation
- Gmail schedule auto extraction
- Real email/push reminder delivery
- Automatic application status changes from schedule creation
