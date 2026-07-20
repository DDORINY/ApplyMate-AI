# E2E Testing Guide

## 목적

v0.9.0부터 브라우저 E2E 테스트는 MVP 핵심 흐름이 화면 수준에서 깨지지 않는지 확인하는 안정화 장치로 관리한다.

## 실행 전제

- 테스트 환경은 운영 계정과 분리한다.
- 외부 provider는 `mock` 또는 `disabled`를 사용한다.
- 기존 로컬/운영 DB volume을 삭제하지 않는다.

## 권장 실행

```bash
cd frontend
npm run test:e2e
```

Docker 기반 검증은 별도 Compose project를 사용한다.

```bash
docker compose -p applymate_e2e --env-file .env.e2e up --build -d
docker compose -p applymate_e2e --env-file .env.e2e down
```

`.env.e2e`는 `.env.e2e.example`을 복사해 만들고, 운영 secret을 재사용하지 않는다.

## v0.9.0 시나리오

- 회원가입/로그인 화면 접근
- 인증 없는 보호 화면 접근
- 알림 화면 접근
- 알림 설정 화면 접근

도메인별 전체 데이터 생성 E2E는 v1.0.0 인수 테스트에서 확장한다.
