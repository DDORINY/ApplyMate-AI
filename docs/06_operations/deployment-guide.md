# 배포 가이드

## 현재 배포 상태

v0.1.1은 로컬 개발 환경과 Docker Compose 실행 검증까지 완료한 상태다. 운영 서버 배포는 아직 범위에 포함하지 않는다.

## 로컬 Docker 실행

루트에서 실행한다.

```bash
docker compose up --build -d
```

상태 확인:

```bash
docker compose ps
```

종료:

```bash
docker compose down
```

주의: 개발 데이터 volume을 삭제하지 않으려면 `docker compose down -v`를 사용하지 않는다.

## 환경변수

운영 또는 로컬 `.env`에 다음 값을 설정한다.

```env
JWT_SECRET_KEY=replace_with_secure_secret
JWT_REFRESH_SECRET_KEY=replace_with_secure_refresh_secret
COOKIE_SECURE=false
COOKIE_SAMESITE=lax
```

운영 HTTPS 환경에서는 다음을 권장한다.

```env
COOKIE_SECURE=true
COOKIE_SAMESITE=lax
```

## Migration

Backend 컨테이너 또는 로컬 Backend 환경에서 실행한다.

```bash
cd backend
alembic upgrade head
```

downgrade 검증:

```bash
alembic downgrade -1
alembic upgrade head
```

운영 DB migration은 별도 승인과 백업 정책 없이 실행하지 않는다.

## Health Check

Backend:

```http
GET http://localhost:8000/api/v1/health
```

Frontend:

```http
GET http://localhost:3000
```

## 운영 배포 전 체크리스트

* Secret 환경변수 설정
* HTTPS 적용
* `COOKIE_SECURE=true` 설정
* 운영 DB 백업 정책 수립
* Alembic migration 적용 계획 수립
* CORS origin 운영 도메인으로 제한
* 로그에 개인정보와 토큰이 남지 않는지 확인
* 모니터링과 알림 구성
