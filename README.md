# ApplyMate AI

현재 버전: `v0.3.3`

ApplyMate AI는 개인용 AI 취업 매니저입니다. 회원/인증, 커리어 프로필, 채용공고 관리, AI 채용공고 분석, 사용자-공고 적합도 분석, 이력서 업로드/텍스트 추출/AI 구조화 분석, 맞춤 지원 문서 생성을 제공합니다.

## v0.3.3 주요 기능

- 근거 기반 맞춤 지원 문서 생성
- 지원동기, 직무 역량, 자기소개, 프로젝트/경력 경험, 입사 후 포부, 자유 문항, 사용자 문항 지원
- 문단별 source reference 저장
- 사용자 편집, AI 재생성, 버전 복원
- 생성 실행 이력과 provider 상태 조회
- `/documents`, `/documents/new`, `/documents/{documentId}` 프론트 화면

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
- `/resumes`
- `/documents`
- `/documents/new`
- `/documents/{documentId}`
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
- [v0.3.3 릴리스 노트](docs/11_releases/v0.3.3-application-documents.md)

## 현재 migration head

`20260719_1800`

## 미검증/주의

- 실제 OpenAI 호출은 별도 API key/model 환경에서 검증 필요
- 운영 SMTP/OAuth/HTTPS Cookie 검증 필요
- 브라우저 E2E 자동화는 아직 별도 구축 전
