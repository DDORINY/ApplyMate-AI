# 현재 프로젝트 상태

## 기준

| 항목 | 값 |
| --- | --- |
| 현재 버전 | v0.2.2 |
| 기준 브랜치 | `main` |
| 기준 main SHA | `8d003c3e6dbcc6090de994e50af30a95fafd4f01` |
| 기준 tag | `v0.2.2` |
| 문서 기준일 | 2026-07-19 |

## 현재 구현 요약

ApplyMate AI는 v0.2.2 기준으로 사용자 계정, 커리어 프로필, 채용공고 관리, AI 채용공고 분석, 사용자-공고 적합도 분석까지 구현되어 있다.

## 기술 스택

| 영역 | 현재 사용 |
| --- | --- |
| Frontend | Next.js, TypeScript, Tailwind CSS, TanStack Query |
| Backend | Python, FastAPI, SQLAlchemy, Alembic, Pydantic, JWT |
| Database | PostgreSQL |
| Cache | Redis |
| Infra | Docker, Docker Compose |
| AI | Provider abstraction: disabled, mock, openai |

## 현재 Architecture

```text
Frontend(Next.js)
  -> Backend(FastAPI /api/v1)
    -> PostgreSQL(SQLAlchemy + Alembic)
    -> Redis
    -> AI Provider(disabled/mock/openai)
```

## 현재 사용자 흐름

1. 회원가입
2. 이메일 인증
3. 로그인 또는 OAuth 로그인
4. 커리어 프로필 작성
5. 기술/경력/프로젝트/희망 조건/제외 조건 입력
6. 채용공고 등록
7. AI 채용공고 분석
8. 사용자-공고 적합도 분석
9. 결과 확인과 피드백 입력

## Backend API 그룹

- Health
- Auth
- OAuth
- Account Security
- Career Profile
- Jobs
- AI Providers
- Job Analysis
- Job Matching
- Job Match Feedback

## 현재 DB 테이블

```text
users
refresh_tokens
oauth_accounts
oauth_states
oauth_login_tickets
career_profiles
skills
user_skills
experiences
projects
project_skills
job_preferences
excluded_conditions
portfolio_links
email_verification_tokens
password_reset_tokens
security_events
companies
job_postings
job_analyses
job_analysis_runs
job_matches
job_match_runs
job_match_feedback
```

## 현재 Frontend 경로

```text
/
/signup
/login
/auth/callback
/me
/profile
/jobs
/jobs/new
/jobs/{jobId}
/settings/accounts
/settings/security
/verify-email
/forgot-password
/reset-password
```

## 현재 테스트 상태

v0.2.2 PR #6 기준:

- Backend ruff: passed
- Backend tests: 84 passed
- Frontend lint: passed
- Frontend type-check: passed
- Frontend build: passed
- Docker Compose config/build/up/down: passed
- Alembic upgrade/downgrade/re-upgrade: passed

## 현재 미검증 항목

- 실제 OpenAI API 호출
- 실제 Google/GitHub OAuth 운영 로그인
- 운영 SMTP 발송
- 운영 HTTPS Cookie
- 운영 배포
- 브라우저 E2E 자동화
- 부하 테스트

## 현재 제한사항

- 이력서 업로드/분석 없음
- 지원 문서 생성 없음
- 지원 현황/일정 관리 없음
- Google Calendar/Gmail 연동 없음
- 대량 crawling 없음
- batch/queue 기반 AI 작업 없음

## 다음 예정 버전

v0.3.x: 이력서 업로드, 이력서 분석, AI 지원 문서 생성.
