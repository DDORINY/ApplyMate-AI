# OAuth 계정 정책

v0.1.3의 소셜 로그인 정책입니다.

## 지원 provider

- Google
- GitHub

Kakao, Naver, Apple은 v0.1.3 범위가 아닙니다.

## 저장하지 않는 정보

다음 값은 DB에 저장하지 않습니다.

- Google/GitHub access token
- Google/GitHub refresh token
- provider token 원문
- OAuth state 원문
- OAuth login ticket 원문

State와 ticket은 hash만 저장합니다.

## 이메일 정책

- 소셜 로그인은 검증된 이메일이 있는 provider 계정만 허용합니다.
- 같은 이메일의 기존 이메일 계정이 있으면 자동 병합하지 않습니다.
- 기존 계정 사용자는 먼저 이메일로 로그인한 뒤 `/settings/accounts`에서 소셜 계정을 명시적으로 연결해야 합니다.
- 소셜 로그인으로 새로 만들어진 계정은 `users.email_verified=true`, `users.password_hash=NULL`일 수 있습니다.

## 계정 연결 정책

- 사용자 1명은 provider별로 1개 계정만 연결할 수 있습니다.
- 하나의 provider 계정은 한 사용자에게만 연결될 수 있습니다.
- 마지막 로그인 수단은 해제할 수 없습니다.
  - 비밀번호가 있는 계정은 모든 소셜 계정을 해제할 수 있습니다.
  - 비밀번호가 없는 social-only 계정은 최소 1개 소셜 계정을 유지해야 합니다.

## Redirect 정책

OAuth 완료 후 이동 가능한 경로는 `OAUTH_ALLOWED_REDIRECT_PATHS`에 정의된 내부 path로 제한합니다.

기본 허용 경로:

```text
/me
/profile
/settings/accounts
```

외부 URL, protocol-relative URL(`//example.com`)은 허용하지 않습니다.
