# ApplyMate AI 운영자 가이드

## 시작과 중지

```bash
docker compose up --build -d
docker compose down
```

운영 전 `.env.production.example`을 기준으로 secret을 안전하게 설정한다.

## Migration

```bash
cd backend
python -m alembic heads
python -m alembic upgrade head
```

운영 migration 전에는 DB backup을 먼저 수행한다.

## Worker

```bash
docker compose run --rm worker
```

현재 worker는 one-shot task 구조다. 장기 scheduler와 분산 lock은 후속 운영 설계 대상이다.

## Health

- `GET /api/v1/health/live`
- `GET /api/v1/health/ready`

Readiness는 DB, Redis, 운영 필수 설정을 확인한다.

## 감사 로그

`audit_logs`는 사용자 주요 action, request id, resource, 결과를 저장한다. Token, secret, 원문 이력서, 메일 본문은 저장하지 않는다.

## Backup/Restore

자세한 절차는 `docs/09_guides/backup-restore.md`를 따른다.

## Provider 설정

- OpenAI: `AI_PROVIDER=openai`, `OPENAI_API_KEY`, `OPENAI_MODEL`
- Calendar: `CALENDAR_PROVIDER=google`, Google Calendar credential
- Gmail: `GMAIL_PROVIDER=google`, Gmail credential
- SMTP: `EMAIL_PROVIDER=smtp`, SMTP credential

실제 provider 호출은 비용과 외부 side effect가 있으므로 별도 검증 환경에서 수행한다.

## Rollback

1. 신규 배포 중지
2. 이전 이미지/커밋으로 전환
3. migration rollback 가능성 확인
4. 필요한 경우 DB restore
5. smoke test 실행
