# Frontend Navigation Structure

문서 기준 버전: `v0.4.0`

## 1. Header Navigation Policy

상단 네비게이션은 두 그룹으로 분리한다.

- 주요 서비스 메뉴: 왼쪽/중앙 영역
- 회원 및 계정 관리 메뉴: 오른쪽 계정 영역

회원가입과 로그인은 주요 서비스 메뉴 앞쪽에 배치하지 않는다.

## 2. 현재 Header 메뉴

### 주요 서비스 메뉴

| Label | Path | 구현 버전 | 설명 |
| --- | --- | --- | --- |
| 홈 | `/` | v0.1.0 | 서비스 상태/랜딩 |
| 프로필 | `/profile` | v0.1.2 | 커리어 프로필 관리 |
| 채용공고 | `/jobs` | v0.2.0 | 채용공고 목록/등록/분석/적합도 |
| 이력서 | `/resumes` | v0.3.0 | 이력서 목록/업로드/분석 |
| 지원 문서 | `/documents` | v0.3.3 | 지원 문서 생성/버전/출처 |
| 지원 현황 | `/applications` | v0.4.0 | 지원 상태/이력/메모 관리 |

### 회원 및 계정 관리 메뉴

| Label | Path | 구현 버전 | 설명 |
| --- | --- | --- | --- |
| 로그인 | `/login` | v0.1.1 | 이메일/OAuth 로그인 |
| 회원가입 | `/signup` | v0.1.1 | 이메일 회원가입 |
| 내 계정 | `/me` | v0.1.1 | 현재 사용자 정보 |
| 계정 연결 | `/settings/accounts` | v0.1.3 | OAuth 계정 연결 관리 |
| 보안 | `/settings/security` | v0.1.4 | 비밀번호/세션/보안 관리 |

## 3. 현재 구현된 주요 경로

| Path | 인증 | 구현 버전 | 주요 컴포넌트 | 설명 |
| --- | --- | --- | --- | --- |
| `/` | 불필요 | v0.1.0 | `service-status-panel` | 랜딩/상태 |
| `/signup` | 불필요 | v0.1.1 | `signup-form` | 회원가입 |
| `/login` | 불필요 | v0.1.1 | `login-form`, `oauth-buttons` | 로그인 |
| `/auth/callback` | 불필요 | v0.1.3 | `oauth-callback-panel` | OAuth ticket 교환 |
| `/verify-email` | 불필요 | v0.1.4 | `verify-email-panel` | 이메일 인증 |
| `/forgot-password` | 불필요 | v0.1.4 | `forgot-password-form` | 비밀번호 찾기 |
| `/reset-password` | 불필요 | v0.1.4 | `reset-password-form` | 비밀번호 재설정 |
| `/me` | 필요 | v0.1.1 | `protected-user-panel` | 내 계정 |
| `/profile` | 필요 | v0.1.2 | `profile-manager` | 커리어 프로필 |
| `/settings/accounts` | 필요 | v0.1.3 | `oauth-accounts-manager` | 계정 연결 |
| `/settings/security` | 필요 | v0.1.4 | `account-security-panel` | 계정 보안 |
| `/jobs` | 필요 | v0.2.0 | `job-list-panel` | 채용공고 목록 |
| `/jobs/new` | 필요 | v0.2.0 | `job-create-panel` | 채용공고 등록 |
| `/jobs/{jobId}` | 필요 | v0.2.0~v0.2.2, v0.4.0 | `job-detail-panel`, `job-analysis-panel`, `job-match-panel` | 공고 상세/분석/적합도/지원 추가 |
| `/resumes` | 필요 | v0.3.0 | `resume-list-panel` | 이력서 목록 |
| `/resumes/new` | 필요 | v0.3.0 | `resume-create-panel` | 이력서 업로드 |
| `/resumes/{resumeId}` | 필요 | v0.3.0~v0.3.2, v0.4.0 | `resume-detail-panel` | 이력서 상세/파일/분석/지원 준비 |
| `/documents` | 필요 | v0.3.3 | `document-list-panel` | 지원 문서 목록 |
| `/documents/new` | 필요 | v0.3.3, v0.4.0 | `document-create-panel` | 선택 UI 기반 지원 문서 생성 |
| `/documents/{documentId}` | 필요 | v0.3.3, v0.4.0 | `document-detail-panel` | 문서 상세/버전/지원 항목 생성 |
| `/applications` | 필요 | v0.4.0 | `application-list-panel` | 지원 현황 목록 |
| `/applications/new` | 필요 | v0.4.0 | `application-create-panel` | 지원 항목 생성 |
| `/applications/{applicationId}` | 필요 | v0.4.0 | `application-detail-panel` | 지원 항목 상세/상태/메모 |

## 4. 주요 사용자 흐름

```text
signup/login
  -> profile
  -> resumes/new
  -> resumes/{resumeId}
  -> jobs/new
  -> jobs/{jobId}
  -> job analysis
  -> job matching
  -> documents/new
  -> documents/{documentId}
  -> applications/new
  -> applications/{applicationId}
```

## 5. v0.4.0 연결 버튼

| 위치 | 버튼 | 이동 |
| --- | --- | --- |
| 채용공고 상세 | 지원 관리에 추가 | `/applications/new?jobId={jobId}` |
| 지원 문서 상세 | 이 문서로 지원 항목 생성 | `/applications/new?documentId={documentId}` |
| 이력서 상세 | 이 이력서로 지원 준비 | `/applications/new?resumeId={resumeId}` |

## 6. 아직 없는 경로

| Path | 예정 버전 | 설명 |
| --- | --- | --- |
| `/schedules` | v0.4.1 | 일정 월/주/목록 |
| `/schedules/new` | v0.4.1 | 일정 생성 |
| `/schedules/{eventId}` | v0.4.1 | 일정 상세 |
| `/dashboard` | v0.4.2 | 지원/일정/분석 요약 |
| `/recommendations` | v0.6.0 | 맞춤 공고 추천 |
