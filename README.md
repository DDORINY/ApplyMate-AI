# ApplyMate AI

현재 버전: `v0.5.0`

ApplyMate AI는 개인용 AI 취업 매니저입니다. 사용자의 커리어 프로필, 이력서, 채용공고, AI 분석 결과, 지원 문서, 지원 현황, 일정을 연결해 취업 준비 흐름을 한곳에서 관리합니다.

## v0.5.0 주요 기능

- 회원가입, 로그인, JWT/Refresh Token 인증
- 이메일 인증, 비밀번호 복구, 세션 관리
- Google/GitHub OAuth 로그인 및 계정 연결 구조
- 커리어 프로필, 경력, 프로젝트, 기술, 희망 조건 관리
- 채용공고 등록/관리, URL 기반 공고 등록
- AI 채용공고 분석 및 사용자-공고 적합도 분석
- 이력서 PDF/DOCX 업로드, 텍스트 추출, AI 구조화 분석
- 근거 기반 맞춤 지원 문서 생성 및 버전 관리
- 지원 현황 CRUD, 상태 변경 이력, 지원 메모, 제출 문서 버전 고정
- 일정 CRUD, 마감/면접/결과 일정, 알림 저장, 충돌 표시, 변경 이력
- `/dashboard` 읽기 전용 대시보드
  - 지원 상태 요약
  - 오늘/이번 주 일정
  - 다가오는 일정 마감과 마감 임박 공고
  - 준비 중인 지원 항목
  - 최근 AI 분석, 적합도 분석, 이력서 분석, 지원 문서, 활동
- Google Calendar 연동 기반
  - 로그인 OAuth와 Calendar OAuth 분리
  - Calendar token 암호화 저장
  - Calendar 목록 조회와 writable Calendar 선택
  - 내부 일정 → Google Calendar mock 동기화
  - sync mapping/run/error 기록
  - 연결 해제

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

- `/dashboard`
- `/jobs`
- `/resumes`
- `/documents`
- `/applications`
- `/calendar`
- `/settings/accounts`
- `/settings/integrations`
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
- [현재 프로젝트 상태](docs/00_status/current-project-status.md)
- [Feature Status Matrix](docs/00_status/feature-status-matrix.md)
- [버전 로드맵](docs/05_development-plan/version-roadmap.md)
- [API 명세](docs/04_api/api-specification.md)
- [DB 설계](docs/06_database/database-design.md)
- [v0.5.0 릴리스 노트](docs/11_releases/v0.5.0-google-calendar.md)

## 현재 migration head

`20260719_2100`

v0.5.0은 Google Calendar 연동 기반 테이블을 추가합니다.

## 미검증/운영 확인 필요

- 실제 OpenAI 호출은 운영 API key/model 설정 후 별도 검증이 필요합니다.
- 실제 Google Calendar API 호출은 운영 Google credentials 설정 후 별도 검증이 필요합니다.
- 운영 Google/GitHub OAuth, SMTP, HTTPS Cookie는 실제 도메인/시크릿 환경에서 별도 검증이 필요합니다.
- Google Calendar 실제 일정 생성은 v0.5.0 범위입니다.
