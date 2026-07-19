# ApplyMate AI

현재 버전: `v0.4.1`

ApplyMate AI는 개인용 AI 취업 매니저입니다. 커리어 프로필, 이력서, 채용공고, AI 분석 결과, 지원 문서, 지원 현황, 일정을 연결해 취업 준비 흐름을 한곳에서 관리합니다.

## v0.4.1 주요 기능

- 회원가입, 로그인, JWT/Refresh Token 인증
- 이메일 인증, 비밀번호 복구, 세션 관리
- Google/GitHub OAuth 로그인 및 계정 연결
- 커리어 프로필, 경력, 프로젝트, 기술, 희망 조건 관리
- 채용공고 등록/관리, URL 기반 공고 등록
- AI 채용공고 분석과 사용자-공고 적합도 분석
- 이력서 PDF/DOCX 업로드, 텍스트 추출, AI 구조화 분석
- 근거 기반 맞춤 지원 문서 생성과 버전 관리
- 지원 현황 관리, 상태 변경 이력, 지원 메모
- 일정 관리: 마감, 코딩 테스트, 과제, 면접, 결과 발표, 알림, 충돌 표시, 변경 이력

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

## 주요 화면

- `/jobs`, `/resumes`, `/documents`, `/applications`, `/calendar`
- `/calendar/new`
- `/calendar/events/{eventId}`
- `/settings/accounts`
- `/settings/security`

## 검증

Backend:

```bash
cd backend
python -m ruff check app tests
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
- [Feature Status Matrix](docs/00_status/feature-status-matrix.md)
- [버전 로드맵](docs/05_development-plan/version-roadmap.md)
- [API 명세](docs/04_api/api-specification.md)
- [DB 설계](docs/06_database/database-design.md)
- [v0.4.1 릴리스 노트](docs/11_releases/v0.4.1-schedule-management.md)

## 현재 migration head

`20260719_2000`

## 미검증·주의

- 실제 OpenAI 호출은 운영 API key/model 환경에서 별도 검증이 필요합니다.
- 운영 Google/GitHub OAuth, SMTP, HTTPS Cookie는 운영 환경에서 별도 검증이 필요합니다.
- v0.4.1 일정 알림은 저장·표시 기능이며 이메일/푸시 실제 발송은 후속 버전 범위입니다.
- Google Calendar 실제 일정 생성은 v0.5.0 이후 범위입니다.
