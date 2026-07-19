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
# v0.4.2 Dashboard Functional Specification

## 목적

대시보드는 사용자가 현재 취업 준비 상황을 빠르게 파악할 수 있도록 지원 현황, 일정, 마감, 최근 AI 분석 결과, 최근 문서, 최근 활동을 읽기 전용으로 집계한다.

## 기능 요구사항

- 사용자는 `/dashboard`에서 자신의 데이터만 확인할 수 있어야 한다.
- 대시보드는 새로운 데이터를 생성/수정/삭제하지 않는다.
- 지원 상태 집계는 백엔드가 다음 그룹 기준으로 계산한다.
  - `PREPARING`: `SAVED`, `PREPARING`
  - `APPLIED`: `APPLIED`
  - `IN_PROGRESS`: `DOCUMENT_REVIEW`, `CODING_TEST`, `ASSIGNMENT`
  - `INTERVIEW`: `INTERVIEW`, `FINAL_INTERVIEW`
  - `OFFER`: `OFFER`
  - `REJECTED`: `REJECTED`
  - `WITHDRAWN`: `WITHDRAWN`
  - `CLOSED`: `CLOSED`
- 기간 필터는 `7d`, `30d`, `90d`, `all`을 제공하고 기본값은 `30d`이다.
- `start_date`, `end_date`가 함께 제공되면 사용자 지정 기간으로 집계한다.
- 오늘 일정과 이번 주 일정은 `timezone` 기준으로 계산하며 기본값은 `Asia/Seoul`이다.
- 일정 마감과 공고 마감은 현재 시각부터 7일 이내 항목을 보여준다.
- 아카이브된 지원 항목과 취소/아카이브된 일정은 대시보드 주요 집계에서 제외한다.
- 최근 항목은 `recent_limit`으로 제한하며 최대 20개까지만 허용한다.
- 프론트 화면은 로딩, 오류, 빈 상태를 표시해야 한다.

## 대시보드 위젯

- 요약 카드
- 지원 상태 분포
- 선택 기간 신규 지원/상태 변경
- 오늘 일정
- 이번 주 일정
- 다가오는 일정 마감
- 마감 임박 공고
- 준비 중인 지원 항목
- 최근 공고 분석
- 최근 적합도 분석
- 최근 이력서 분석
- 최근 지원 문서
- 최근 활동

# v0.5.0 Google Calendar Integration Functional Specification

## 목적

사용자가 명시적으로 연결한 Google Calendar 계정에 ApplyMate AI 내부 일정을 동기화할 수 있는 기반을 제공한다.

## 기능 요구사항

- 로그인 OAuth와 Calendar OAuth를 분리해야 한다.
- Calendar 연결은 사용자가 명시적으로 시작해야 한다.
- Calendar OAuth state는 hash 저장, 만료, 1회 사용을 적용해야 한다.
- Calendar token은 암호화해 저장해야 하며 API 응답에 노출하면 안 된다.
- 사용자는 연결 상태를 조회할 수 있어야 한다.
- 사용자는 provider Calendar 목록을 조회할 수 있어야 한다.
- 사용자는 writable Calendar만 동기화 대상으로 선택할 수 있어야 한다.
- 사용자는 동기화 방향을 선택할 수 있어야 한다.
- 사용자는 전체 내부 일정 또는 단일 내부 일정을 동기화할 수 있어야 한다.
- 동일 내부 일정은 동일 connection에서 중복 external event를 만들면 안 된다.
- 동기화 실행 이력과 안전한 오류 이력을 저장해야 한다.
- 연결 해제 시 내부 일정은 보존해야 한다.
- 실제 Google API 호출은 운영 credentials가 있을 때 별도 검증해야 한다.

## 금지사항

- 사용자 승인 없는 외부 Calendar 일정 생성/수정/삭제
- 사용자 승인 없는 내부 일정 자동 생성
- 로그인 OAuth token을 Calendar API에 재사용
- token 평문 저장/응답/로그 출력
