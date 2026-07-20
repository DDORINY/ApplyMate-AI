# Backup and Restore Guide

## PostgreSQL backup

운영 migration 전에는 PostgreSQL dump를 먼저 생성한다.

```bash
pg_dump "$DATABASE_URL" > applymate_backup.sql
```

## Restore

복구는 별도 검증 DB에서 먼저 수행한다.

```bash
psql "$DATABASE_URL" < applymate_backup.sql
```

## Migration rollback

- Alembic downgrade 가능 여부를 staging에서 검증한다.
- 운영 DB에서는 백업 없이 downgrade를 실행하지 않는다.

## File storage

이력서 파일 storage는 DB와 별도 백업 대상이다. DB row와 파일 storage 시점이 어긋나지 않도록 같은 배포 창에서 백업한다.

## Redis

현재 Redis는 cache, rate limit, 작업 보조 성격으로 본다. 영구 데이터로 승격하는 경우 별도 백업 정책을 작성한다.

## v0.9.0 상태

문서화 완료. 실제 운영 복구 리허설은 `NEEDS_VERIFICATION`이다.
