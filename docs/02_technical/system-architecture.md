# 시스템 아키텍처

## 개요

ApplyMate AI는 Frontend, Backend, Database, Cache, 향후 외부 API 연동 계층으로 구성합니다. 현재 v0.1.3에서는 회원/인증, Google/GitHub 소셜 로그인, 커리어 프로필 관리까지 구현되어 있으며, AI 분석과 캘린더/메일 연동은 이후 버전에서 확장합니다.

## 구성 요소

| 영역 | 기술 | 책임 |
| --- | --- | --- |
| Frontend | Next.js, TypeScript, Tailwind CSS | 사용자 화면, 입력 검증, API 호출 |
| Backend | FastAPI, SQLAlchemy, Alembic | REST API, 인증, 권한, 비즈니스 로직 |
| Database | PostgreSQL | 사용자, 인증, OAuth, 커리어 프로필 데이터 저장 |
| Cache | Redis | Health 확인, 향후 캐시/비동기 작업 보조 |
| Container | Docker Compose | 로컬 개발 실행 환경 |

## 기본 요청 흐름

```text
Browser
  -> Next.js App Router
  -> Frontend API Client
  -> FastAPI /api/v1
  -> Router
  -> Service
  -> Repository
  -> PostgreSQL
```

## 인증 구조

- 로그인 성공 시 Access Token은 응답 본문으로 반환합니다.
- Refresh Token은 `applymate_refresh_token` HttpOnly Cookie로 전달합니다.
- Refresh Token 원문은 저장하지 않고 hash만 DB에 저장합니다.
- 보호 API는 `Authorization: Bearer {access_token}` 헤더를 확인합니다.
- 만료된 Access Token은 Refresh Token으로 재발급할 수 있습니다.

## OAuth 구조

```text
Browser
  -> GET /auth/oauth/{provider}/authorize
  -> Provider authorize page
  -> GET /auth/oauth/{provider}/callback
  -> Backend validates state and provider user
  -> Frontend /auth/callback?ticket=...
  -> POST /auth/oauth/exchange
  -> Service access token + refresh cookie issued
```

정책:

- OAuth provider token은 저장하지 않습니다.
- State와 login ticket은 원문 대신 hash만 저장합니다.
- Provider callback에서 바로 서비스 token을 URL에 싣지 않고 1회용 ticket으로 교환합니다.
- 동일 이메일 기존 계정은 자동 병합하지 않고 명시적 연결을 요구합니다.

## 커리어 프로필 구조

Backend 계층:

```text
app/api/v1/endpoints/profiles.py
app/schemas/profile.py
app/services/profile.py
app/repositories/profile.py
app/models/career.py
```

Frontend 계층:

```text
src/app/profile/page.tsx
src/components/profile/profile-manager.tsx
src/lib/api/profile.ts
src/types/profile.ts
```

DB 계층:

```text
career_profiles
skills
user_skills
experiences
projects
project_skills
job_preferences
excluded_conditions
portfolio_links
```

## 권한 원칙

- 모든 커리어 프로필 API는 인증이 필요합니다.
- 사용자 소유 리소스는 현재 사용자의 `user_id`로만 조회합니다.
- 다른 사용자의 리소스 ID 접근은 존재 여부 노출을 줄이기 위해 404로 처리합니다.
- 비밀번호, 토큰, secret은 API 응답에 포함하지 않습니다.

## 향후 확장

- v0.2.x: 채용공고 관리와 분석 계층 추가
- v0.3.x: 이력서 파싱과 AI 문서 생성 계층 추가
- v0.4.x: 지원 현황과 일정 관리 추가
- v0.5.x: Google Calendar/Gmail 등 외부 연동 추가
