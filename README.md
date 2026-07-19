# ApplyMate AI

현재 버전: `v0.4.0`

ApplyMate AI는 개인용 AI 취업 매니저입니다. 사용자의 커리어 프로필, 이력서, 채용공고, AI 분석 결과를 기반으로 지원 문서를 만들고 실제 지원 현황까지 관리합니다.

## v0.4.0 주요 기능

- 회원가입, 로그인, JWT/Refresh Token 인증
- 커리어 프로필 관리
- 채용공고 등록/관리 및 AI 채용공고 분석
- 사용자-공고 적합도 분석
- 이력서 업로드, 텍스트 추출, AI 구조화 분석
- 근거 기반 지원 문서 생성, 버전 관리, 출처 조회
- 지원 현황 관리, 상태 변경 이력, 지원 메모
- 제출 문서 버전 고정

## 기술 스택

| 영역 | 기술 |
| --- | --- |
| Frontend | Next.js, TypeScript, Tailwind CSS, TanStack Query |
| Backend | Python, FastAPI, SQLAlchemy, Alembic, Pydantic, JWT |
| Database | PostgreSQL |
| Cache | Redis |
| Infra | Docker, Docker Compose |
| AI | disabled/mock/openai Provider abstraction |

## 실행

```bash
cp .env.example .env
docker compose up --build
```

기본 포트:

- Frontend: `3000`
- Backend: `8000`
- PostgreSQL: `5432`
- Redis: `6379`

## 주요 화면

- `/`
- `/signup`
- `/login`
- `/me`
- `/profile`
- `/jobs`
- `/jobs/new`
- `/jobs/{jobId}`
- `/resumes`
- `/resumes/new`
- `/resumes/{resumeId}`
- `/documents`
- `/documents/new`
- `/documents/{documentId}`
- `/applications`
- `/applications/new`
- `/applications/{applicationId}`
- `/settings/accounts`
- `/settings/security`

## 검증

Backend:

```bash
cd backend
python -m ruff check .
python -m pytest -p no:cacheprovider
```

Frontend:

```bash
cd frontend
npm run lint
npm run type-check
npm run build
```

## 문서

- [문서 인덱스](docs/README.md)
- [현재 상태](docs/00_status/current-project-status.md)
- [버전 로드맵](docs/05_development-plan/version-roadmap.md)
- [API 명세](docs/04_api/api-specification.md)
- [DB 설계](docs/06_database/database-design.md)
- [v0.4.0 릴리스 노트](docs/11_releases/v0.4.0-application-tracking.md)

## 현재 migration head

`20260719_1900`

## 미검증/주의

- 실제 OpenAI 호출은 별도 API key/model 환경에서 검증 필요
- 운영 SMTP/OAuth/HTTPS Cookie 검증 필요
- 브라우저 E2E 자동화는 별도 구축 대상
