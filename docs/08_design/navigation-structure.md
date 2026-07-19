# Navigation Structure

## Main navigation

주요 기능 화면은 헤더의 왼쪽/중앙 주요 네비게이션 영역에 배치한다.

1. Home: `/`
2. Dashboard: `/dashboard`
3. Profile: `/profile`
4. Jobs: `/jobs`
5. Resumes: `/resumes`
6. Documents: `/documents`
7. Applications: `/applications`
8. Calendar: `/calendar`

## Account navigation

회원가입, 로그인, 회원/계정 관리는 주요 기능 네비게이션 앞에 두지 않고 오른쪽 계정 영역에 둔다.

- Login: `/login`
- Signup: `/signup`
- My account: `/me`
- Connected accounts: `/settings/accounts`
- Security: `/settings/security`

## v0.4.2 dashboard screen

- `/dashboard`: 지원 상태, 일정, 마감, AI 분석, 지원 문서, 최근 활동을 요약하는 읽기 전용 화면
- 대시보드의 각 카드와 목록 항목은 가능한 경우 원본 화면으로 연결한다.
  - 지원 현황: `/applications`, `/applications/{applicationId}`
  - 일정: `/calendar`, `/calendar/events/{eventId}`
  - 채용공고/AI 분석/적합도: `/jobs/{jobId}`
  - 이력서 분석: `/resumes/{resumeId}`
  - 지원 문서: `/documents/{documentId}`

## v0.4.1 calendar screens

- `/calendar`: 월간/주간/목록 기준 일정 목록과 예정 일정
- `/calendar/new`: 일정 생성
- `/calendar/events/{eventId}`: 일정 상세, 상태 변경, 알림, 변경 이력

## Cross-links

- `/applications/{applicationId}` links to create and view schedules for the application.
- `/jobs/{jobId}` links to create and view schedules for the job posting.
