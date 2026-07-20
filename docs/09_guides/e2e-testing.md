# E2E Testing Guide

문서 기준 버전: `v1.0.0`

## 목적

Playwright E2E 테스트는 MVP 주요 화면이 브라우저 환경에서 깨지지 않고 접근 가능한지 확인하는 릴리스 안전장치다. v1.0.0에서는 기존 smoke를 확장해 15개 시나리오를 검증한다.

## 원칙

- 실제 OpenAI, Gmail, Google Calendar, SMTP provider를 호출하지 않는다.
- 테스트 환경은 `.env.e2e.example` 또는 이를 복사한 `.env.e2e`를 사용한다.
- 운영 DB volume을 삭제하거나 재사용하지 않는다.
- 보호 화면은 비로그인 상태에서 로그인 화면으로 안내되어도 정상으로 본다.

## 로컬 실행

```bash
cd frontend
npm run test:e2e
```

## Docker 기반 환경 실행

```bash
docker compose -f docker-compose.yml -f docker-compose.e2e.yml -p applymate_e2e --env-file .env.e2e.example up --build -d
docker compose -f docker-compose.yml -f docker-compose.e2e.yml -p applymate_e2e --env-file .env.e2e.example down
```

PowerShell helper:

```powershell
./scripts/e2e-up.ps1
./scripts/e2e-reset.ps1
./scripts/e2e-down.ps1
```

## v1.0.0 시나리오

- 로그인/회원가입 공개 화면 접근
- 비밀번호 재설정 요청 화면 접근
- 이메일 인증 화면 접근
- 인증 없는 보호 화면의 로그인 안내
- 대시보드 route smoke
- 채용공고 route smoke
- 이력서 route smoke
- 지원 문서 route smoke
- 지원 현황 route smoke
- 일정 route smoke
- 추천 route smoke
- 알림 route smoke
- 연동 설정 route smoke
- 계정 보안 route smoke
- 알림 설정 운영 화면 route smoke

## 최종 검증 결과

2026-07-20 v1.0.0 릴리스 검증에서 Playwright E2E는 `15 passed`로 통과했다.
