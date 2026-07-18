# ApplyMate AI 기술 스택

## 1. 기술 구성 개요

ApplyMate AI는 웹 기반 취업 관리 서비스로 구성한다.

* Frontend: 사용자 화면 및 일정 관리
* Backend: 회원, 공고, 지원, 일정 API
* AI Service: 공고 분석 및 지원 문서 생성
* Database: 사용자 및 지원 데이터 저장
* Scheduler: 채용공고 분석 및 알림 처리
* External API: Google Calendar, Gmail, LLM 연동

## 2. Frontend

| 구분           | 기술              | 사용 목적             |
| ------------ | --------------- | ----------------- |
| Framework    | Next.js         | 웹 서비스 화면 구현       |
| Language     | TypeScript      | 타입 안정성 확보         |
| UI           | Tailwind CSS    | 빠른 UI 개발          |
| State        | Zustand         | 사용자 상태 및 화면 상태 관리 |
| Server State | TanStack Query  | API 데이터 조회 및 캐싱   |
| Form         | React Hook Form | 입력 폼 관리           |
| Validation   | Zod             | 입력값 검증            |
| Calendar     | FullCalendar    | 일정 및 지원 일정 표시     |

v0.1.0에서는 서비스 기반 구축 범위에 맞춰 Next.js, TypeScript, Tailwind CSS만 우선 적용한다. v0.1.1에서는 인증 화면과 서버 상태 관리를 위해 TanStack Query, React Hook Form, Zod를 적용한다. Zustand와 FullCalendar는 실제 기능이 도입되는 버전에서 적용한다.

## 3. Backend

| 구분             | 기술         | 사용 목적           |
| -------------- | ---------- | --------------- |
| Framework      | FastAPI    | REST API 개발     |
| Language       | Python     | 백엔드 및 AI 서비스 구현 |
| ORM            | SQLAlchemy | 데이터베이스 연동       |
| Migration      | Alembic    | 데이터베이스 변경 이력 관리 |
| Validation     | Pydantic   | API 요청 및 응답 검증  |
| Authentication | JWT        | 사용자 인증          |
| API Document   | Swagger UI | API 문서 자동 생성    |

v0.1.1 JWT는 HS256 서명 구조를 사용하며 Access Token과 Refresh Token Secret을 분리한다. 비밀번호는 PBKDF2-SHA256 해시로 저장한다.

## 4. AI Service

| 구분                | 기술                     | 사용 목적             |
| ----------------- | ---------------------- | ----------------- |
| LLM               | 호환 모델                | 공고 분석 및 문서 생성     |
| Embedding         | Embedding API          | 사용자 경험과 공고 유사도 분석 |
| Vector Search     | pgvector               | 경험 및 공고 의미 기반 검색  |
| Prompt Management | 자체 Prompt Template     | 기능별 프롬프트 관리       |
| Document Parser   | PyMuPDF 또는 python-docx | 이력서 문서 분석         |

## 5. Database

| 구분               | 기술         | 사용 목적          |
| ---------------- | ---------- | -------------- |
| Main DB          | PostgreSQL | 서비스 데이터 저장     |
| Vector Extension | pgvector   | 임베딩 벡터 저장      |
| Cache            | Redis      | 캐시 및 비동기 작업 관리 |

PostgreSQL을 기본 데이터베이스로 사용한다.

## 6. Scheduler 및 비동기 처리

| 구분             | 기술          | 사용 목적         |
| -------------- | ----------- | ------------- |
| MVP Scheduler  | APScheduler | 정기 공고 분석 및 알림 |
| 확장 Queue       | Celery      | 비동기 분석 작업     |
| Message Broker | Redis       | 작업 큐 처리       |

MVP에서는 APScheduler를 사용하고, 처리량이 증가하면 Celery 구조로 확장한다.

## 7. 외부 API

| 외부 서비스              | 사용 목적            |
| ------------------- | ---------------- |
| Google Calendar API | 지원 일정 등록 및 동기화   |
| Gmail API           | 채용 관련 이메일 분석     |
| OpenAI API          | 채용공고 및 자기소개서 분석  |
| GitHub API          | 사용자 프로젝트 및 활동 분석 |
| 채용공고 API            | 공개 채용공고 수집       |

## 8. Infrastructure

| 구분            | 기술                  | 사용 목적                 |
| ------------- | ------------------- | --------------------- |
| Container     | Docker              | 서비스 실행 환경 통일          |
| Orchestration | Docker Compose      | 로컬 및 서버 환경 구성         |
| Web Server    | Nginx               | Reverse Proxy 및 HTTPS |
| CI/CD         | GitHub Actions      | 테스트 및 배포 자동화          |
| Server        | Ubuntu 24.04 LTS    | 운영 서버                 |
| Monitoring    | Prometheus, Grafana | 확장 단계 모니터링            |

## 9. 개발 도구

| 구분              | 기술                            |
| --------------- | ----------------------------- |
| Version Control | Git, GitHub                   |
| API Test        | Postman 또는 Bruno              |
| DB Tool         | DBeaver                       |
| Code Quality    | Ruff, Black, ESLint, Prettier |
| Test            | Pytest, Vitest, Playwright    |

v0.1.1의 필수 검증은 Backend Pytest, Ruff, Frontend lint, TypeScript 검사, production build, Docker Compose 설정 검증, Alembic migration upgrade/downgrade, 인증 API 흐름 검증이다.
