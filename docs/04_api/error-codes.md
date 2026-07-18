# 오류 코드

API 오류 응답은 다음 공통 구조를 사용한다.

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
| ---- | ----------- | ---- |
| `RESOURCE_NOT_FOUND` | 404 | 요청한 경로 또는 리소스를 찾을 수 없음 |
| `VALIDATION_ERROR` | 422 | 요청 값 검증 실패 |
| `HTTP_ERROR` | 4xx/5xx | 명시적으로 분류되지 않은 HTTP 오류 |
| `INTERNAL_SERVER_ERROR` | 500 | 서버 내부 오류 |

## 인증 오류

| 코드 | HTTP Status | 설명 |
| ---- | ----------- | ---- |
| `AUTH_EMAIL_ALREADY_EXISTS` | 409 | 이미 가입된 이메일 |
| `AUTH_INVALID_CREDENTIALS` | 401 | 이메일 또는 비밀번호 오류 |
| `AUTH_TOKEN_MISSING` | 401 | Access Token 없음 |
| `AUTH_TOKEN_INVALID` | 401 | Access Token 형식, 서명, 타입 오류 |
| `AUTH_TOKEN_EXPIRED` | 401 | Access Token 만료 |
| `AUTH_REFRESH_TOKEN_INVALID` | 401 | Refresh Token 없음, 형식 오류, DB 불일치 |
| `AUTH_REFRESH_TOKEN_EXPIRED` | 401 | Refresh Token 만료 |
| `AUTH_REFRESH_TOKEN_REVOKED` | 401 | 이미 폐기된 Refresh Token |
| `AUTH_USER_INACTIVE` | 403 | 비활성 또는 탈퇴 사용자 |
| `AUTH_UNAUTHORIZED` | 401 | 인증되지 않은 사용자 |

## 메시지 원칙

* 내부 예외 메시지를 그대로 반환하지 않는다.
* 비밀번호, 토큰, Secret 값은 오류 응답에 포함하지 않는다.
* 로그인 실패 시 이메일 존재 여부를 구체적으로 노출하지 않는다.
* 클라이언트가 사용자에게 표시할 수 있는 수준의 메시지만 반환한다.
