# 시스템 아키텍처

## 개요

ApplyMate AI는 Frontend, Backend, Database, Cache, 외부 API 연동 계층으로 구성한다. 현재 v0.1.1에서는 인증과 기본 실행 환경에 집중하며, AI 분석과 외부 연동은 이후 버전에서 확장한다.

## 구성 요소

| 영역 | 기술 | 책임 |
| ---- | ---- | ---- |
| Frontend | Next.js, TypeScript, Tailwind CSS | 사용자 화면, 폼 검증, API 호출 |
| Backend | FastAPI, SQLAlchemy, Alembic | REST API, 인증, DB 접근, 비즈니스 로직 |
| Database | PostgreSQL | 사용자, Refresh Token, 향후 서비스 데이터 저장 |
| Cache | Redis | Health 확인, 향후 캐시와 비동기 작업 보조 |
| Container | Docker Compose | 로컬 개발 실행 환경 |

## v0.1.1 인증 아키텍처

```text
Browser
  -> Next.js Frontend
  -> FastAPI Backend
  -> PostgreSQL
```

인증 흐름:

1. 사용자가 로그인한다.
2. Backend가 Access Token과 Refresh Token을 발급한다.
3. Access Token은 응답 본문으로 전달된다.
4. Refresh Token은 HttpOnly Cookie로 전달된다.
5. Backend는 Refresh Token 원문이 아닌 해시만 PostgreSQL에 저장한다.
6. 보호 API는 Bearer Access Token을 검증한다.
7. Access Token 만료 시 Refresh Token으로 재발급한다.

## Backend 계층 구조

```text
app/
  api/          Router 및 dependency
  core/         설정, 보안, 예외 처리
  db/           DB engine, session, Base
  models/       SQLAlchemy 모델
  repositories/ DB 접근
  schemas/      Pydantic 요청/응답 스키마
  services/     비즈니스 로직
```

원칙:

* Router는 요청/응답과 dependency 연결에 집중한다.
* Service는 인증 정책과 트랜잭션 흐름을 담당한다.
* Repository는 SQLAlchemy 쿼리를 담당한다.
* Schema는 API 외부 계약을 정의한다.
* Model은 DB 구조를 정의한다.

## Frontend 구조

```text
src/
  app/          App Router 페이지
  components/   UI 컴포넌트
  lib/api/      API client
  lib/auth/     token helper
  lib/env/      환경변수 접근
  providers/    React Query Provider
  types/        API 타입
```

원칙:

* API Base URL은 환경변수에서 읽는다.
* 서버 상태는 TanStack Query로 관리한다.
* 폼 검증은 React Hook Form과 Zod를 사용한다.
* Refresh Token은 JavaScript에서 읽지 않는다.

## 데이터 흐름

```text
Frontend Form
  -> API Client
  -> FastAPI Router
  -> Service
  -> Repository
  -> PostgreSQL
```

오류는 Backend 공통 오류 구조로 반환하고 Frontend는 메시지를 화면에 표시한다.

## 확장 방향

* v0.1.2: 사용자별 커리어 프로필 모델과 보호 API 추가
* v0.2.x: 채용공고 모델과 분석 API 추가
* v0.3.x: AI 분석 서비스와 프롬프트 템플릿 분리
* v0.5.x: Google Calendar와 Gmail 외부 연동 추가
* v0.6.x: 추천 스케줄러와 비동기 처리 확장
