# ApplyMate AI v1.0.0 완성 마스터 플랜

## 1. 현재 상태

- 현재 기준 버전: `v0.2.2`
- 현재 main 기준 기능: 프로젝트 기반, 회원/인증, 커리어 프로필, 소셜 로그인, 계정 보안, 채용공고 관리, AI 채용공고 분석, 사용자-공고 적합도 분석
- 현재 migration head: `20260719_1400`
- 실제 OpenAI, Google Calendar, Gmail, 운영 SMTP, 운영 배포는 아직 검증 대상이다.

## 2. 최종 서비스 목표

ApplyMate AI는 개인 사용자가 채용공고 탐색부터 지원 문서 작성, 지원 현황과 일정 관리, 추천 확인까지 한 흐름으로 관리하는 개인용 AI 취업 매니저를 목표로 한다.

## 3. MVP 정의

v1.0.0 MVP는 다음 사용자 흐름이 한 계정 안에서 끊기지 않고 동작하는 상태로 정의한다.

1. 회원가입 및 로그인
2. 커리어 프로필 작성
3. 이력서 업로드
4. 이력서 텍스트 추출
5. AI 이력서 구조화 분석
6. 채용공고 등록
7. AI 채용공고 분석
8. 사용자-공고 적합도 분석
9. 지원 문서 초안 생성
10. 지원 현황 등록 및 상태 관리
11. 일정 관리
12. 대시보드 확인
13. 저장된 공고 기반 추천 확인

## 4. 버전별 개발 순서

| 버전 | 목적 | 완료 산출물 |
| --- | --- | --- |
| v0.3.0 | 이력서 파일 업로드 | 파일 저장, 메타데이터, 다운로드, 삭제 |
| v0.3.1 | 이력서 텍스트 추출 | PDF/DOCX 텍스트 추출, 재추출, 수정 |
| v0.3.2 | AI 이력서 분석 | 구조화 분석, 근거, 실행 이력 | 완료 |
| v0.3.3 | 지원 문서 생성 | 근거 기반 초안, 버전, 출처 |
| v0.4.0 | 지원 현황 관리 | 지원 상태, 이력, 메모 |
| v0.4.1 | 일정 관리 | 일정, 리마인더, 신뢰도 |
| v0.4.2 | 대시보드 | 지원/일정/분석 요약 |
| v0.5.0 | Google Calendar 연동 기반 | OAuth scope 분리, mock 연동, NEEDS_VERIFICATION |
| v0.5.1 | Gmail 채용 메일 분석 기반 | 명시 승인 기반 메일 후보 분석, NEEDS_VERIFICATION |
| v0.6.0 | 추천 시스템 기반 | 규칙 기반 추천, 피드백 |
| v0.6.1 | 정기 추천 | 스케줄 실행, 실행 이력 |
| v0.9.0 | 통합 안정화 | 보안, 성능, E2E, migration chain |
| v1.0.0 | 공식 MVP 릴리스 | 최종 문서, 릴리스 노트, 태그 |

## 5. DB 확장 계획

- v0.3.x: `resumes`, `resume_files`, `resume_extractions`, `resume_extraction_runs`, `resume_analyses`, `resume_analysis_runs`
- v0.3.3: `application_documents`, `application_document_versions`, `application_document_sources`, `generation_runs`
- v0.4.x: `applications`, `application_status_history`, `application_notes`, `schedule_events`, `schedule_reminders`, `schedule_event_history`
- v0.5.x: `calendar_connections`, `calendar_sync_mappings`, `sync_runs`, `sync_errors`, `gmail_connections`, `email_sync_runs`, `email_candidates`, `email_candidate_actions`
- v0.6.x: `job_recommendations`, `recommendation_runs`, `recommendation_feedback`

## 6. API 확장 계획

모든 API는 `/api/v1` 하위에 추가하고 공통 응답 구조를 유지한다.

- `/resumes`
- `/resumes/{resume_id}/files`
- `/resumes/{resume_id}/extractions`
- `/resumes/{resume_id}/analyses`
- `/documents`
- `/applications`
- `/calendar/events`
- `/dashboard`
- `/integrations/calendar`
- `/integrations/gmail`
- `/recommendations`

## 7. Frontend 화면 확장 계획

- `/resumes`
- `/resumes/new`
- `/resumes/[resumeId]`
- `/documents`
- `/documents/new`
- `/documents/[documentId]`
- `/applications`
- `/applications/[applicationId]`
- `/calendar`
- `/calendar/events/[eventId]`
- `/dashboard`
- `/recommendations`

## 8. 외부 연동 계획

- OpenAI: `AI_PROVIDER=mock` 상태에서는 mock provider와 구조 검증까지 완료하고 실제 호출은 `NEEDS_VERIFICATION`으로 남긴다.
- Google Calendar: 인증 정보가 없으면 adapter, DB, API, Frontend, 테스트까지만 완료한다.
- Gmail: 사용자 명시 승인 기반 후보 분석 구조까지만 구현하고 실제 메일 변경은 금지한다.
- SMTP: 운영 SMTP 미검증 상태는 문서에 분리 기록한다.

## 9. 보안 계획

- 사용자 소유권 검사
- 파일 업로드 확장자/MIME/크기 검증
- path traversal 방어
- 실행 파일 업로드 차단
- 원본 파일명과 내부 저장명을 분리
- OAuth token 로그 출력 금지
- AI prompt injection 방어
- 운영 secret 저장소 커밋 금지

## 10. 테스트 전략

각 버전마다 다음을 기본 검증으로 수행한다.

- backend ruff
- backend pytest
- frontend lint
- frontend type-check
- frontend build
- docker compose config
- migration upgrade 검증

v0.9.0부터는 브라우저 E2E와 실제 PostgreSQL migration chain 검증을 강화한다.

## 11. 배포 전략

로컬 Docker Compose를 기준으로 개발 검증을 완료한 뒤, v1.0.0에서 운영 배포 가이드를 최신화한다. 운영 배포, 운영 DB migration, 운영 secret 변경은 별도 명시 승인 없이는 수행하지 않는다.

## 12. 백업·복구 전략

v1.0.0 전까지 다음 문서를 완성한다.

- DB 백업 가이드
- 파일 스토리지 백업 가이드
- migration rollback 가이드
- 장애 복구 절차

## 13. 모니터링 전략

- API 오류율
- 인증 실패
- AI provider 실패
- 파일 업로드 실패
- 외부 연동 실패
- background job 실패

## 14. 버전별 완료 조건

각 버전은 다음 조건을 만족해야 완료한다.

- 기능 구현
- DB migration 작성
- API 문서 최신화
- Frontend 화면 연결
- 테스트 통과
- PR squash merge
- main 재검증
- annotated tag 생성 및 push

## 15. v1.0.0 완료 조건

- 필수 MVP 흐름 전체 동작
- 문서와 코드 일치
- Critical/High 보안 이슈 없음
- 미검증 외부 연동은 `NEEDS_VERIFICATION`으로 명확히 표시
- main clean
- `v1.0.0` annotated tag push 완료
