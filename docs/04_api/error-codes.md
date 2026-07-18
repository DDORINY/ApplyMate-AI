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
| `AUTH_TOKEN_MISSING` | 401 | Access Token 없음 |
| `AUTH_TOKEN_INVALID` | 401 | Access Token 형식, 서명, 타입 오류 |
| `AUTH_TOKEN_EXPIRED` | 401 | Access Token 만료 |
| `AUTH_REFRESH_TOKEN_INVALID` | 401 | Refresh Token 없음, 형식 오류, DB 불일치 |
| `AUTH_REFRESH_TOKEN_EXPIRED` | 401 | Refresh Token 만료 |
| `AUTH_REFRESH_TOKEN_REVOKED` | 401 | 이미 폐기된 Refresh Token |
| `AUTH_USER_INACTIVE` | 403 | 비활성 사용자 |
| `AUTH_UNAUTHORIZED` | 401 | 인증되지 않은 사용자 |

## 커리어 프로필 오류

| 코드 | HTTP Status | 설명 |
| --- | --- | --- |
| `PROFILE_NOT_FOUND` | 404 | 커리어 프로필 없음 |
| `PROFILE_ALREADY_EXISTS` | 409 | 이미 커리어 프로필이 있음 |
| `SKILL_ALREADY_REGISTERED` | 409 | 동일 사용자가 같은 기술을 이미 등록함 |
| `SKILL_NOT_FOUND` | 404 | 기술 마스터 없음 |
| `USER_SKILL_NOT_FOUND` | 404 | 사용자 기술 없음 또는 접근 불가 |
| `EXPERIENCE_NOT_FOUND` | 404 | 경력 없음 또는 접근 불가 |
| `EXPERIENCE_INVALID_DATE_RANGE` | 400 | 경력 시작일/종료일 정책 위반 |
| `PROJECT_NOT_FOUND` | 404 | 프로젝트 없음 또는 접근 불가 |
| `PROJECT_INVALID_DATE_RANGE` | 400 | 프로젝트 시작일/종료일 정책 위반 |
| `PREFERENCE_NOT_FOUND` | 404 | 희망 조건 없음 |
| `EXCLUDED_CONDITION_NOT_FOUND` | 404 | 지원 제외 조건 없음 또는 접근 불가 |
| `PORTFOLIO_LINK_NOT_FOUND` | 404 | 포트폴리오 링크 없음 또는 접근 불가 |

중복 제외 조건, 중복 포트폴리오 URL, 위험 URL scheme 등은 `VALIDATION_ERROR`로 반환한다.

## 메시지 원칙

- 비밀번호, 토큰, Secret 값은 오류 응답에 포함하지 않는다.
- 로그인 실패 시 이메일 존재 여부를 구체적으로 노출하지 않는다.
- 타 사용자의 리소스 접근은 존재 여부 노출을 최소화하기 위해 404로 처리한다.
- DB 내부 오류 원문은 외부 응답에 그대로 반환하지 않는다.
