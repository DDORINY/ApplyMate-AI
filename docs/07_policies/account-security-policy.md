# 계정 보안·복구 정책

v0.1.4 계정 보안·복구 기능의 정책입니다.

## 이메일 인증

- 이메일 회원가입 사용자는 기본적으로 `email_verified=false`입니다.
- Google/GitHub에서 검증된 이메일로 생성된 소셜 사용자는 `email_verified=true`를 유지합니다.
- 이메일 인증 token 원문은 DB에 저장하지 않고 hash만 저장합니다.
- token은 1회용이며 기본 만료 시간은 30분입니다.
- 이미 인증된 사용자의 재발송 요청은 거부합니다.

## 비밀번호 복구

- 비밀번호 찾기 API는 계정 존재 여부를 응답으로 노출하지 않습니다.
- 재설정 token 원문은 DB에 저장하지 않고 hash만 저장합니다.
- 재설정 성공 시 사용자의 기존 refresh token 세션은 모두 폐기합니다.
- 소셜 전용 사용자도 비밀번호 재설정으로 새 비밀번호를 설정할 수 있습니다.

## 비밀번호 변경·설정

- 기존 비밀번호가 있는 사용자는 현재 비밀번호를 검증해야 합니다.
- 비밀번호가 없는 소셜 전용 사용자는 `/auth/password/set`으로 비밀번호를 설정합니다.
- 새 비밀번호는 기존 비밀번호와 같을 수 없습니다.
- 비밀번호 변경 시 현재 세션을 제외한 다른 세션을 폐기합니다.

## 세션 관리

- refresh token은 `session_id`를 기준으로 세션을 구성합니다.
- refresh token rotation 후에도 같은 `session_id`를 유지합니다.
- 사용자는 본인 세션만 조회하거나 폐기할 수 있습니다.
- 전체 세션 로그아웃은 현재 세션을 포함한 모든 refresh token을 폐기합니다.

## 로그인 실패 제한

- Redis 기반 실패 횟수 제한을 우선 사용합니다.
- 기본 정책은 5회 실패 후 15분 제한입니다.
- 계정 존재 여부가 노출되지 않도록 동일한 오류 코드를 사용합니다.

## 보안 이벤트

기록 대상:

- `LOGIN_SUCCESS`
- `LOGIN_FAILED`
- `LOGOUT`
- `LOGOUT_ALL`
- `EMAIL_VERIFICATION_SENT`
- `EMAIL_VERIFIED`
- `PASSWORD_RESET_REQUESTED`
- `PASSWORD_RESET_COMPLETED`
- `PASSWORD_CHANGED`
- `PASSWORD_CONFIGURED`
- `SESSION_REVOKED`

보안 이벤트에는 비밀번호, token 원문, secret, IP 원문을 저장하지 않습니다.
