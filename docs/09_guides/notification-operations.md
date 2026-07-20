# Notification Operations Guide

문서 기준 버전: `v0.8.0`

## Local operation

알림 due 처리는 인증된 사용자 API로 수동 실행할 수 있다.

```text
POST /api/v1/notifications/run-due
```

Docker Compose에는 `worker` service가 추가되어 있다.

```bash
docker compose run --rm worker
```

## Email provider

v0.8.0에서 `EMAIL_PROVIDER=development` 또는 `mock`은 mock notification email provider로 처리된다.

실제 SMTP 발송은 다음 값이 필요하지만, 운영 검증 전까지 완료로 표시하지 않는다.

```env
EMAIL_PROVIDER=smtp
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
EMAIL_FROM_ADDRESS=
EMAIL_FROM_NAME=ApplyMate AI
```

## Safety

- `.env`는 커밋하지 않는다.
- 알림 본문에 secret, token, raw provider error를 포함하지 않는다.
- Push provider는 v0.8.0에서 실발송하지 않는다.
