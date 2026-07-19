# Frontend Navigation Structure

## 기준

이 문서는 실제 `frontend/src/app` App Router 기준으로 작성한다.

## 현재 경로

| 경로 | 인증 | 구현 버전 | 화면/컴포넌트 | 설명 |
| --- | --- | --- | --- | --- |
| `/` | 불필요 | v0.1.0 | `service-status-panel` | 랜딩/서비스 상태 |
| `/signup` | 불필요 | v0.1.1 | `signup-form` | 회원가입 |
| `/login` | 불필요 | v0.1.1 | `login-form`, `oauth-buttons` | 로그인 |
| `/auth/callback` | 불필요 | v0.1.3 | `oauth-callback-panel` | OAuth ticket 교환 |
| `/me` | 필요 | v0.1.1 | `protected-user-panel` | 현재 사용자 |
| `/profile` | 필요 | v0.1.2 | `profile-manager` | 커리어 프로필 관리 |
| `/jobs` | 필요 | v0.2.0 | `job-list-panel` | 채용공고 목록 |
| `/jobs/new` | 필요 | v0.2.0 | `job-create-panel` | 채용공고 등록 |
| `/jobs/{jobId}` | 필요 | v0.2.0~v0.2.2 | `job-detail-panel`, `job-analysis-panel`, `job-match-panel` | 공고 상세/분석/적합도 |
| `/settings/accounts` | 필요 | v0.1.3 | `oauth-accounts-manager` | 소셜 계정 관리 |
| `/settings/security` | 필요 | v0.1.4 | `account-security-panel` | 계정 보안/세션 |
| `/verify-email` | 불필요 | v0.1.4 | `verify-email-panel` | 이메일 인증 |
| `/forgot-password` | 불필요 | v0.1.4 | `forgot-password-form` | 비밀번호 찾기 |
| `/reset-password` | 불필요 | v0.1.4 | `reset-password-form` | 비밀번호 재설정 |

## 주요 사용자 흐름

```text
signup
  -> verify-email
  -> login
  -> profile
  -> jobs
  -> jobs/new
  -> jobs/{jobId}
  -> AI job analysis
  -> job matching
  -> feedback
```

## 보호 화면

다음 화면은 access token이 필요하다.

- `/me`
- `/profile`
- `/jobs`
- `/jobs/new`
- `/jobs/{jobId}`
- `/settings/accounts`
- `/settings/security`

## 아직 없는 경로

다음은 계획 단계이며 현재 App Router에 존재하지 않는다.

- `/resumes`
- `/documents`
- `/applications`
- `/calendar`
- `/dashboard`
- `/recommendations`
