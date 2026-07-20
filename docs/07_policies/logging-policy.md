# Logging and Audit Policy

## Request ID

모든 API 응답은 `X-Request-ID`를 포함한다. 클라이언트가 값을 제공하지 않으면 서버가 생성한다.

공통 오류 응답은 가능한 경우 `error.request_id`를 포함한다.

## 금지 로그

- Authorization header
- Cookie
- Access Token
- Refresh Token
- OAuth code
- OAuth refresh token
- API key
- SMTP password
- 메일 전체 본문
- 이력서 전체 본문

## 감사 로그

`audit_logs`는 중요한 사용자 작업을 기록한다.

- `user_id`
- `action`
- `resource_type`
- `resource_id`
- `result`
- `request_id`
- `ip_hash`
- `user_agent`
- `audit_metadata`

v0.9.0 기록 대상:

- 알림 설정 변경
- Notification delivery retry

추가 대상은 v1.0.0 운영 감사 설계에서 확장한다.
