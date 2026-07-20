# Current Project Status

## 2026-07-20 v0.7.0 상태 업데이트

- 현재 완료 릴리스: `v0.7.0`
- 현재 작업 브랜치: `feature/v0.7.0-document-improvement`
- 현재 migration head: `20260720_0100`
- 직전 완료 릴리스: `v0.6.1` 추천 UX 개선 및 추천 실행 자동화
- 신규 완료 범위: AI 지원 문서 개선 루프
- AI provider 검증 기준: `AI_PROVIDER=mock`
- 실제 OpenAI 문서 개선 호출은 `OPENAI_API_KEY`, `OPENAI_MODEL`, 비용 및 운영 프롬프트 검증이 필요하므로 `NEEDS_VERIFICATION` 상태이다.

상세 연결 메모: [환경 연결 상태](environment-connection-status.md)

## 현재 버전

- 버전: `v0.7.0`
- 최신 migration: `20260720_0100_create_document_improvement_tables.py`
- 최신 릴리스 범위: 기존 지원 문서 버전 기반 AI 개선, 문장별 제안, 사용자 승인, 새 버전 적용, 개선 실행 이력

## 구현 완료 기능

- 프로젝트 기반, Docker Compose, Health API
- 회원가입, 로그인, JWT/Refresh Token 인증
- 이메일 인증, 비밀번호 복구, 세션 관리
- Google/GitHub OAuth 로그인 및 계정 연결 구조
- 커리어 프로필, 경력, 프로젝트, 기술, 희망 조건 관리
- 채용공고 등록/관리, URL 기반 등록
- AI 채용공고 분석
- 사용자-공고 적합도 분석
- 이력서 PDF/DOCX 업로드, 텍스트 추출, AI 구조화 분석
- 근거 기반 지원 문서 생성, 편집, 버전 관리
- AI 지원 문서 개선 루프, 문장별 제안, 승인 기반 새 버전 생성
- 지원 현황 관리, 상태 변경 이력, 지원 메모, 제출 문서 버전 고정
- 일정 관리, 알림 저장, 충돌 표시, 변경 이력
- 대시보드 집계 API와 `/dashboard` 화면
- Google Calendar 연동 기반
- Gmail 채용 메일 분석 기반
- 저장된 채용공고 기반 규칙 추천
- 추천 실행 설정, Snapshot, 변화 판정, 추천 알림 후보

## 주요 화면

- `/dashboard`
- `/documents`
- `/documents/{documentId}`
- `/documents/{documentId}/improve`
- `/documents/{documentId}/improvements/{runId}`
- `/applications`
- `/calendar`
- `/settings/accounts`
- `/settings/integrations`
- `/inbox-candidates`
- `/recommendations`
- `/recommendations/{recommendationId}`
- `/recommendations/history`
- `/settings/recommendations`
- `/settings/security`

## 현재 DB

최신 migration: `20260720_0100_create_document_improvement_tables.py`

v0.7.0 신규 테이블:

- `document_improvement_runs`
- `document_improvement_suggestions`
- `document_improvement_sources`
- `document_improvement_actions`

## 최근 검증 기준

- Backend ruff: 통과
- Backend pytest: `163 passed`
- Frontend lint: 통과
- Frontend type-check: 통과
- Frontend build: 통과
- Docker compose config: 통과
- Alembic heads: `20260720_0100 (head)`
- 별도 Docker Compose project PostgreSQL migration upgrade/downgrade/upgrade: 통과

## 미검증

- 실제 OpenAI API 기반 지원 문서 개선
- 실제 Google OAuth consent
- 실제 Google Calendar API event create/update/delete
- 실제 Gmail API 조회/분석
- 운영 SMTP
- 운영 HTTPS Cookie
- 운영 배포
