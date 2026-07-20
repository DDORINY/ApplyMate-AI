# Notification Policy

문서 기준 버전: `v0.8.0`

## 기본 원칙

- In-app 알림은 기본 활성화한다.
- Email과 Push는 사용자 동의 없이 활성화하지 않는다.
- Push provider 실발송은 v0.8.0 범위에서 제외한다.
- 실제 SMTP 알림 발송은 운영 credential 검증 전까지 `NEEDS_VERIFICATION`이다.

## 중복 방지

모든 알림은 `deduplication_key`를 가진다. 중복 방지는 애플리케이션 코드만이 아니라 DB unique constraint로 보장한다.

## Source 정책

알림은 `source_type`, `source_id`, `source_url`을 가진다. 알림 본문에는 access token, OAuth token, raw provider error, 내부 prompt, secret 값을 포함하지 않는다.

## Delivery 정책

Notification은 사용자에게 보여줄 사건이고, Delivery는 채널별 전달 시도이다.

Delivery 상태:

- `PENDING`
- `PROCESSING`
- `SENT`
- `FAILED`
- `RETRY_SCHEDULED`
- `CANCELLED`
- `SKIPPED`

## Quiet hours

Quiet hours는 사용자 timezone 기준으로 해석한다. v0.8.0에서는 in-app 저장을 막지 않고, 외부 채널 발송 정책을 위한 설정 기반을 제공한다.
*** Add File: docs/09_guides/notification-operations.md
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
