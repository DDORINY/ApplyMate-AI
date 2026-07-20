# Deployment Checklist

## 환경변수

- `APP_ENV`
- `DATABASE_URL`
- `REDIS_URL`
- `JWT_SECRET_KEY`
- `JWT_REFRESH_SECRET_KEY`
- `FRONTEND_URL`
- `BACKEND_URL`
- `CORS_ALLOWED_ORIGINS`
- `EXTERNAL_TOKEN_ENCRYPTION_KEY`
- Provider별 credential

## 배포 전

- Backend test 통과
- Frontend lint/type-check/build 통과
- Alembic `heads` 단일 head 확인
- 새 DB 기준 `alembic upgrade head` 확인
- Secret scan 확인
- Docker Compose config 확인

## 운영 보안

- HTTPS 적용
- `COOKIE_SECURE=true`
- 운영 CORS origin 명시
- HSTS 적용 여부 결정
- SMTP/Gmail/Calendar/OpenAI live provider 검증 여부 기록

## 배포

- DB backup
- migration 적용
- backend/frontend/worker 배포
- `/api/v1/health/live` 확인
- `/api/v1/health/ready` 확인
- smoke test 실행

## Nginx / Reverse Proxy

예시 설정은 `deploy/nginx/`에 둔다.

- `/api/`는 backend로 proxy한다.
- 그 외 route는 frontend로 proxy한다.
- 업로드 제한은 `client_max_body_size`로 관리한다.
- HTTPS termination, 인증서 갱신, HSTS는 실제 운영 도메인에서 별도 검증한다.

## Rollback

- 이미지/커밋 rollback
- migration rollback 가능 여부 확인
- 필요한 경우 DB restore

## Monitoring

- API 오류율
- worker 실패 run
- notification delivery 실패
- OAuth callback 실패
- rate limit 429 빈도
