# Current Project Status

## 2026-07-20 환경 상태 업데이트

- 현재 완료 릴리스: `v0.6.1`
- 현재 작업 브랜치: `feature/v0.6.1-recommendation-automation`
- 현재 migration head: `20260720_0000`
- `v0.5.1`은 `main`에 병합되었고 `v0.5.1` 태그가 생성되었다.
- `v0.6.0`은 저장된 공고 기반 규칙 추천으로 완료되었다.
- `v0.6.1`은 추천 UX 개선과 추천 실행 자동화 기반을 구현 중이다.
- 현재 `.env` 기준 Gmail은 실제 연결되지 않는다. `GMAIL_PROVIDER`가 비어 있고 Gmail OAuth credential이 없다.
- 현재 `.env` 기준 AI는 `AI_PROVIDER=mock`이므로 실제 OpenAI 호출은 연결되지 않는다.
- 기본 Docker PostgreSQL 연결은 기존 로컬 volume 비밀번호 불일치로 막혀 있다. 깨끗한 별도 Compose project에서는 backend/PostgreSQL/Redis 연결이 정상 확인되었다.

상세 연결 메모: [환경 연결 상태](environment-connection-status.md)

## 현재 버전

- 버전: `v0.6.1`
- 현재 migration head: `20260720_0000`
- 최신 릴리스 범위: 추천 UX 개선 및 추천 실행 자동화 기반
- Calendar provider 검증 기준: `CALENDAR_PROVIDER=mock`
- AI provider 검증 기준: `AI_PROVIDER=mock`

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
- 지원 현황 관리, 상태 변경 이력, 지원 메모, 제출 문서 버전 고정
- 일정 관리, 알림 저장, 충돌 표시, 변경 이력
- 대시보드 집계 API와 `/dashboard` 화면
- Google Calendar 전용 OAuth state, token 암호화 저장, Calendar 선택, mock 동기화, mapping/run/error 기록, 연결 해제
- Gmail 전용 OAuth state, 읽기 전용 scope, mock 메일 조회, 채용 메일 후보 생성, 사용자 승인 기반 상태 변경/일정 생성
- 저장된 채용공고 기반 규칙 추천, 추천 점수/등급/이유/부족 조건, 추천 피드백, `/recommendations` 화면
- 추천 실행 설정, run-if-due, Snapshot, 추천 변화 판정, 추천 알림 후보, `/recommendations/history`, `/settings/recommendations`

## 주요 화면

- `/dashboard`
- `/applications`
- `/calendar`
- `/calendar/events/{eventId}`
- `/settings/accounts`
- `/settings/integrations`
- `/inbox-candidates`
- `/recommendations`
- `/recommendations/{recommendationId}`
- `/recommendations/history`
- `/settings/recommendations`
- `/settings/security`

## 현재 DB

최신 migration: `20260720_0000_create_recommendation_automation_tables.py`

v0.5.0 신규 테이블:

- `calendar_oauth_states`
- `external_accounts`
- `calendar_connections`
- `calendar_sync_mappings`
- `sync_runs`
- `sync_errors`

v0.5.1 신규 테이블:

- `gmail_oauth_states`
- `gmail_connections`
- `email_sync_runs`
- `email_messages`
- `email_analysis_runs`
- `email_candidates`
- `email_candidate_actions`

v0.6.0 신규 테이블:

- `job_recommendation_runs`
- `job_recommendations`
- `job_recommendation_reasons`
- `job_recommendation_feedback`

v0.6.1 신규 테이블:

- `job_recommendation_settings`
- `job_recommendation_snapshots`
- `job_recommendation_snapshot_items`
- `recommendation_notification_candidates`

## 최근 검증 기준

- Backend ruff: 통과
- Backend pytest: `157 passed`
- Frontend lint: 통과
- Frontend type-check: 통과
- Frontend build: 통과
- Docker compose config: 통과
- Alembic heads: `20260720_0000 (head)`
- 별도 Docker Compose project PostgreSQL migration upgrade/downgrade/upgrade: 통과

## 미검증

- 실제 Google OAuth consent
- 실제 Google Calendar API event create/update/delete
- 실제 OpenAI API 호출
- 운영 SMTP
- 운영 HTTPS Cookie
- 운영 배포
- Gmail 실제 API 조회/분석
