# Functional Specification

Current implemented version: `v0.7.0`

## v0.7.0 AI Document Improvement Loop Functional Specification

### Purpose

기존 지원 문서 버전을 기준으로 AI 개선안을 생성하고, 사용자가 문장별 제안을 검토·승인한 뒤 새 문서 버전으로 저장한다.

### Requirements

- v0.3.3 지원 문서 생성/버전 기능을 확장하고 중복 생성 기능을 만들지 않는다.
- 개선 실행은 기준 문서 버전, 개선 유형, 사용자 요청, 목표 톤/길이, provider metadata를 저장한다.
- 개선 유형은 명확성, 간결화, 전문적 톤, 직무/기업 연결, 기술/경력/프로젝트/성과 강조, 구조, 문법, 길이 조정, 직접 요청을 지원한다.
- AI 출력은 전체 개선안과 문장별 원문/개선 문장/변경 이유/근거/위험도/선택 상태를 포함한다.
- 승인 전 기존 문서 버전은 변경하지 않는다.
- 사용자가 적용하면 승인 또는 선택된 제안만 반영한 새 `application_document_versions`를 생성한다.
- 개선 실행 이후 최신 문서 버전이 바뀌면 outdated로 표시하고 적용을 차단한다.
- 모든 개선 실행, 제안, source, action은 `user_id` 소유권을 검증한다.
- 근거 없는 회사명, 기술, 성과 수치, 날짜, 자격증, 프로젝트는 생성하지 않는다.
- source와 사용자 입력의 prompt injection 지시는 따르지 않는다.

### Prohibited

- 사용자 승인 없는 문서 변경
- 지원자 실제 경험에 없는 사실 생성
- 선택하지 않은 외부 source 자동 추가
- 외부 웹 검색 기반 기업 인재상 추정
- 기존 문서 생성 API 응답 구조 변경

## v0.6.1 Recommendation Automation Foundation Functional Specification

### Purpose

추천 실행 설정, 실행 조건 판단, Snapshot, 변화 판정, 알림 후보 저장을 제공해 일일 맞춤 추천 자동화 기반을 만든다.

### Requirements

- 기본 추천 실행 설정은 비활성화와 `MANUAL`이다.
- `run-if-due`는 인증된 사용자만 호출할 수 있다.
- 실행 조건을 충족하지 않으면 `DISABLED`, `NOT_DUE`, `PROFILE_MISSING`, `NO_ACTIVE_JOBS`, `DUPLICATE_INPUT`, `ALREADY_RUNNING` 중 하나를 반환한다.
- 추천 실행 후 Snapshot과 Snapshot item을 저장한다.
- 신규 추천, 점수 상승/하락, 등급 상승/하락, 오래된 추천을 Backend에서 판정한다.
- 추천 결과 응답에는 최신 변화 타입, 점수 변화, 순위, 데이터 완성도, 추천 confidence를 포함할 수 있다.
- 알림 후보는 저장만 하며 실제 이메일·푸시 발송은 하지 않는다.
- 모든 설정, Snapshot, 알림 후보는 사용자 소유권을 검증한다.
- 대시보드는 Snapshot을 읽기만 하며 추천을 자동 실행하지 않는다.

### Prohibited

- 외부 채용공고 자동 수집
- 실제 이메일·푸시 알림 발송 완료 표시
- AI/ML 추천 호출
- 사용자 승인 없는 지원 상태 변경
- 자동 지원 제출

## v0.6.0 Rule-Based Job Recommendation Functional Specification

### Purpose

사용자의 저장된 채용공고와 커리어 프로필을 비교해 외부 크롤링이나 AI/ML 호출 없이 설명 가능한 추천 목록을 제공한다.

### Requirements

- 추천 후보는 사용자가 저장한 채용공고만 사용한다.
- 추천 방식은 `RULE_BASED`로 표시한다.
- 커리어 프로필, 경력, 프로젝트, 기술, 희망 조건과 공고 분석/공고 원문 정보를 점수화한다.
- 추천 결과는 점수, 등급, 추천 이유, 부족 조건, 필수 조건 불일치 여부를 포함한다.
- 추천 실행 이력은 상태, 정책 버전, 후보 수, 생성/완료/실패 시각을 저장한다.
- 프로필, 공고, 정책 hash가 달라진 기존 추천은 오래된 추천으로 표시할 수 있어야 한다.
- 사용자는 추천 상세를 조회하고 관심/비관심/숨김/지원함/나중에 보기 피드백을 남길 수 있어야 한다.
- 숨김 또는 비관심 피드백을 남긴 공고는 기본 재추천에서 제외한다.
- 모든 추천 조회, 생성, 피드백 API는 `user_id` 소유권을 검증한다.
- `/recommendations`와 `/recommendations/{recommendationId}` 화면은 로딩, 오류, 빈 상태를 제공한다.

### Prohibited

- 외부 채용 사이트 자동 크롤링
- 사용자 저장 공고 외부의 임의 추천 생성
- OpenAI 또는 다른 AI provider 호출
- ML 모델 추천이라고 표현
- 사용자 승인 없는 지원 상태 변경
- 지원 확률을 확정적으로 표현

## v0.5.1 Gmail Recruitment Email Analysis Functional Specification

### Purpose

사용자가 명시적으로 연결한 Gmail 계정에서 채용 관련 메일을 읽기 전용으로 분석하여 지원 상태와 일정 후보를 생성한다.

### Requirements

- Gmail OAuth는 로그인 OAuth 및 Calendar OAuth와 분리한다.
- Gmail scope는 읽기 전용 `gmail.readonly`로 제한한다.
- 동일 메일은 중복 저장하지 않는다.
- 메일 원문 전체 HTML과 첨부파일은 저장하지 않는다.
- 후보는 유형, 근거, 신뢰도, 검토 필요 여부를 가진다.
- 지원 상태 변경과 일정 생성은 사용자 승인 후에만 수행한다.
- 승인 처리 중 상태 변경, 일정 생성, 후보 action 기록은 transaction으로 처리한다.
- 모든 조회/승인 API는 `user_id` 소유권을 검증한다.
- 실제 Gmail API 호출은 운영 credentials 검증 전까지 `NEEDS_VERIFICATION`으로 표시한다.

### Prohibited

- 사용자 승인 없는 Gmail 메일 수정/삭제/발송
- 사용자 승인 없는 지원 상태 변경
- 사용자 승인 없는 일정 생성
- 메일 내 prompt injection 문자열을 시스템 명령으로 실행

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
