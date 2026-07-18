# 오류 코드

API 오류 응답은 다음 공통 구조를 사용합니다.

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "오류 메시지"
  }
}
```

## 공통 오류

| 코드 | HTTP Status | 설명 |
| --- | --- | --- |
| `RESOURCE_NOT_FOUND` | 404 | 요청 경로 또는 리소스를 찾을 수 없음 |
| `VALIDATION_ERROR` | 400/422 | 요청 값 검증 실패 |
| `HTTP_ERROR` | 4xx/5xx | 명시적으로 분류되지 않은 HTTP 오류 |
| `INTERNAL_SERVER_ERROR` | 500 | 서버 내부 오류 |

## 인증 오류

| 코드 | HTTP Status | 설명 |
| --- | --- | --- |
| `AUTH_EMAIL_ALREADY_EXISTS` | 409 | 이미 가입된 이메일 |
| `AUTH_INVALID_CREDENTIALS` | 401 | 이메일 또는 비밀번호 오류 |
| `AUTH_PASSWORD_NOT_CONFIGURED` | 401 | 비밀번호가 없는 소셜 전용 계정의 이메일 로그인 시도 |
| `AUTH_EMAIL_ALREADY_VERIFIED` | 409 | 이미 이메일 인증이 완료됨 |
| `AUTH_EMAIL_NOT_VERIFIED` | 403 | 이메일 인증이 필요한 기능 |
| `AUTH_EMAIL_VERIFICATION_TOKEN_INVALID` | 400 | 이메일 인증 token 없음 또는 불일치 |
| `AUTH_EMAIL_VERIFICATION_TOKEN_EXPIRED` | 400 | 이메일 인증 token 만료 |
| `AUTH_EMAIL_VERIFICATION_TOKEN_USED` | 400 | 이미 사용된 이메일 인증 token |
| `AUTH_EMAIL_VERIFICATION_RESEND_LIMITED` | 429 | 이메일 인증 재발송 제한 |
| `AUTH_PASSWORD_RESET_TOKEN_INVALID` | 400 | 비밀번호 재설정 token 없음 또는 불일치 |
| `AUTH_PASSWORD_RESET_TOKEN_EXPIRED` | 400 | 비밀번호 재설정 token 만료 |
| `AUTH_PASSWORD_RESET_TOKEN_USED` | 400 | 이미 사용된 비밀번호 재설정 token |
| `AUTH_PASSWORD_MISMATCH` | 422 | 비밀번호 확인 불일치 |
| `AUTH_PASSWORD_SAME_AS_CURRENT` | 400 | 새 비밀번호가 기존 비밀번호와 같음 |
| `AUTH_PASSWORD_ALREADY_CONFIGURED` | 409 | 이미 비밀번호가 설정된 계정 |
| `AUTH_SESSION_NOT_FOUND` | 404 | 세션을 찾을 수 없음 |
| `AUTH_SESSION_NOT_OWNED` | 404 | 다른 사용자 세션 접근 |
| `AUTH_TOO_MANY_ATTEMPTS` | 429 | 시도 횟수 제한 초과 |
| `EMAIL_PROVIDER_DISABLED` | 503 | 이메일 발송 provider 비활성 |
| `EMAIL_DELIVERY_FAILED` | 502 | 이메일 발송 실패 |
| `AUTH_TOKEN_MISSING` | 401 | Access Token 없음 |
| `AUTH_TOKEN_INVALID` | 401 | Access Token 형식, 서명, 타입 오류 |
| `AUTH_TOKEN_EXPIRED` | 401 | Access Token 만료 |
| `AUTH_REFRESH_TOKEN_INVALID` | 401 | Refresh Token 없음, 형식 오류, DB 불일치 |
| `AUTH_REFRESH_TOKEN_EXPIRED` | 401 | Refresh Token 만료 |
| `AUTH_REFRESH_TOKEN_REVOKED` | 401 | 이미 폐기된 Refresh Token |
| `AUTH_USER_INACTIVE` | 403 | 비활성 사용자 |
| `AUTH_UNAUTHORIZED` | 401 | 인증되지 않은 사용자 |

## OAuth 오류

| 코드 | HTTP Status | 설명 |
| --- | --- | --- |
| `OAUTH_PROVIDER_NOT_SUPPORTED` | 404 | 지원하지 않는 OAuth provider |
| `OAUTH_PROVIDER_DISABLED` | 400 | provider client 설정이 없어 비활성화됨 |
| `OAUTH_REDIRECT_NOT_ALLOWED` | 400 | 허용되지 않은 `redirect_path` |
| `OAUTH_STATE_MISSING` | 400 | callback state 누락 |
| `OAUTH_STATE_INVALID` | 400 | state 불일치, 재사용 또는 존재하지 않음 |
| `OAUTH_STATE_EXPIRED` | 400 | state 만료 |
| `OAUTH_CODE_MISSING` | 400 | callback code 누락 |
| `OAUTH_CODE_EXCHANGE_FAILED` | 400 | provider code 교환 실패 |
| `OAUTH_PROVIDER_REQUEST_FAILED` | 400 | provider API 요청 실패 |
| `OAUTH_PROVIDER_USER_INVALID` | 400 | provider 사용자 식별 정보 누락 |
| `OAUTH_VERIFIED_EMAIL_REQUIRED` | 400 | 검증된 이메일을 제공하지 않는 소셜 계정 |
| `OAUTH_ACCOUNT_LINK_REQUIRED` | 409 | 같은 이메일의 기존 계정이 있어 명시적 연결 필요 |
| `OAUTH_ACCOUNT_LINKED_TO_OTHER_USER` | 409 | 소셜 계정이 다른 사용자에게 이미 연결됨 |
| `OAUTH_ACCOUNT_ALREADY_LINKED` | 409 | 해당 provider가 현재 사용자에게 이미 연결됨 |
| `OAUTH_TICKET_INVALID` | 401 | ticket 없음 또는 재사용 |
| `OAUTH_TICKET_EXPIRED` | 401 | ticket 만료 |
| `OAUTH_ACCOUNT_NOT_FOUND` | 404 | 연결된 소셜 계정을 찾을 수 없음 |
| `OAUTH_LAST_LOGIN_METHOD` | 400 | 마지막 로그인 수단 해제 시도 |

## 커리어 프로필 오류

| 코드 | HTTP Status | 설명 |
| --- | --- | --- |
| `PROFILE_NOT_FOUND` | 404 | 커리어 프로필 없음 |
| `PROFILE_ALREADY_EXISTS` | 409 | 이미 커리어 프로필이 있음 |
| `SKILL_ALREADY_REGISTERED` | 409 | 같은 사용자가 같은 기술을 이미 등록함 |
| `SKILL_NOT_FOUND` | 404 | 기술 마스터 없음 |
| `USER_SKILL_NOT_FOUND` | 404 | 사용자 기술 없음 또는 접근 불가 |
| `EXPERIENCE_NOT_FOUND` | 404 | 경력 없음 또는 접근 불가 |
| `EXPERIENCE_INVALID_DATE_RANGE` | 400 | 경력 시작일/종료일 정책 위반 |
| `PROJECT_NOT_FOUND` | 404 | 프로젝트 없음 또는 접근 불가 |
| `PROJECT_INVALID_DATE_RANGE` | 400 | 프로젝트 시작일/종료일 정책 위반 |
| `PREFERENCE_NOT_FOUND` | 404 | 희망 조건 없음 |
| `EXCLUDED_CONDITION_NOT_FOUND` | 404 | 지원 제외 조건 없음 또는 접근 불가 |
| `PORTFOLIO_LINK_NOT_FOUND` | 404 | 포트폴리오 링크 없음 또는 접근 불가 |

## 메시지 원칙

- 비밀번호, 토큰, Secret 값은 오류 응답에 포함하지 않습니다.
- 로그인 실패 시 이메일 존재 여부를 구체적으로 노출하지 않습니다.
- 다른 사용자의 리소스 접근은 존재 여부 노출을 최소화하기 위해 404로 처리합니다.
