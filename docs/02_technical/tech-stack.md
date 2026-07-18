# ApplyMate AI 기술 스택

## 구성 개요

ApplyMate AI는 웹 기반 개인 취업 관리 서비스입니다.

- Frontend: 사용자 화면과 상태 관리
- Backend: 회원, 인증, 프로필, 향후 공고/지원 API
- Database: 사용자와 지원 데이터 저장
- Cache: 세션성/비동기 작업 보조
- External API: OAuth, AI, 캘린더/메일 연동

## Frontend

| 구분 | 기술 | 사용 목적 |
| --- | --- | --- |
| Framework | Next.js App Router | 웹 화면 구현 |
| Language | TypeScript | 타입 안정성 |
| UI | Tailwind CSS | 빠른 UI 개발 |
| Server State | TanStack Query | API 데이터 조회/캐싱 |
| Form | React Hook Form | 입력 폼 관리 |
| Validation | Zod | 프론트 입력 검증 |

v0.1.3 기준 구현 화면은 홈, 회원가입, 로그인, OAuth callback, 내 계정, 커리어 프로필, 소셜 계정 연결입니다.

## Backend

| 구분 | 기술 | 사용 목적 |
| --- | --- | --- |
| Framework | FastAPI | REST API 개발 |
| Language | Python 3.12 | 백엔드 구현 |
| ORM | SQLAlchemy | DB 모델링 |
| Migration | Alembic | DB 변경 이력 관리 |
| Validation | Pydantic | API 요청/응답 검증 |
| Authentication | JWT | 서비스 사용자 인증 |
| HTTP Client | httpx | OAuth provider API 호출 |
| API Docs | Swagger UI | API 문서 자동 생성 |

인증은 JWT Access Token과 HttpOnly Refresh Token Cookie를 사용합니다. 비밀번호는 PBKDF2-SHA256 hash로 저장합니다. OAuth provider token은 저장하지 않습니다.

## Database

| 구분 | 기술 | 사용 목적 |
| --- | --- | --- |
| Main DB | PostgreSQL | 서비스 데이터 저장 |
| Cache | Redis | 캐시 및 비동기 작업 기반 |

v0.1.3부터 OAuth 연결을 위해 `oauth_accounts`, `oauth_states`, `oauth_login_tickets` 테이블을 사용합니다.

## External API

| 서비스 | 사용 목적 | 상태 |
| --- | --- | --- |
| Google OAuth | Google 로그인/계정 연결 | v0.1.3 구현 |
| GitHub OAuth | GitHub 로그인/계정 연결 | v0.1.3 구현 |
| OpenAI API | 채용공고 분석, 문서 생성 | 향후 |
| Google Calendar API | 지원 일정 동기화 | 향후 |
| Gmail API | 채용 메일 분석 | 향후 |

## Infrastructure

| 구분 | 기술 | 사용 목적 |
| --- | --- | --- |
| Container | Docker | 실행 환경 통일 |
| Orchestration | Docker Compose | 로컬 개발 환경 구성 |
| CI/CD | GitHub Actions | 향후 테스트/배포 자동화 |

## 개발 도구

| 구분 | 기술 |
| --- | --- |
| Version Control | Git, GitHub |
| Code Quality | Ruff, ESLint, TypeScript |
| Test | Pytest |
| API Test | Swagger UI, Postman/Bruno 후보 |
