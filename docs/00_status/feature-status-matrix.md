# Feature Status Matrix

문서 기준일: 2026-07-20
현재 릴리스: `v1.0.0`
현재 브랜치: `feature/v1.0.0-mvp-release`
최신 migration head: `20260720_0300`

## 상태 코드

| 상태 | 의미 |
| --- | --- |
| IMPLEMENTED | 코드 구현은 완료되었으나 별도 검증 결과가 아직 제한적 |
| VERIFIED_MOCK | mock provider 또는 mock 데이터 기준 검증 완료 |
| VERIFIED_LOCAL | 로컬 단위/API/lint/build 기준 검증 완료 |
| VERIFIED_E2E | Playwright 등 브라우저 기반 E2E 검증 완료 |
| NEEDS_VERIFICATION | 운영 credential, 외부 서비스, staging/production 환경에서 추가 검증 필요 |
| NOT_IMPLEMENTED | 아직 구현되지 않음 |
| EXCLUDED | MVP 범위에서 의도적으로 제외 |

## v1.0.0 MVP 기능 상태

| 영역 | 기능 | 상태 | 검증/비고 |
| --- | --- | --- | --- |
| 인증 | 회원가입, 로그인, JWT, refresh token, 이메일 인증, 비밀번호 복구 | VERIFIED_LOCAL | backend tests 포함 |
| 계정 보안 | 세션 관리, OAuth 계정 연결, 보안 이벤트 | VERIFIED_LOCAL | 소유권/토큰 노출 방지 테스트 포함 |
| 커리어 프로필 | 기본 프로필, 경력, 프로젝트, 기술, 희망 조건 | VERIFIED_LOCAL | backend/frontend 검증 |
| 채용공고 | 공고 CRUD, URL 기반 등록, 중복 검사 | VERIFIED_LOCAL | backend/frontend 검증 |
| AI 공고 분석 | 공고 핵심 정보/요구 기술/위험 요소 분석 | VERIFIED_MOCK | 실제 OpenAI 호출은 NEEDS_VERIFICATION |
| 적합도 분석 | 사용자-공고 적합도 점수와 근거 | VERIFIED_MOCK | mock AI/규칙 기반 검증 |
| 이력서 | 업로드, 다운로드, 삭제, 텍스트 추출, 사용자 보정 | VERIFIED_LOCAL | 파일 확장자/MIME/signature/size 검증 |
| AI 이력서 분석 | 이력서 구조화 분석과 프로필 반영 | VERIFIED_MOCK | 실제 OpenAI 호출은 NEEDS_VERIFICATION |
| 지원 문서 | 맞춤 문서 생성, 버전, 출처, 실행 이력 | VERIFIED_MOCK | 근거 없는 내용 생성 금지 정책 적용 |
| 문서 개선 루프 | 문장별 개선 제안, 승인/거절, 새 버전 생성 | VERIFIED_MOCK | backend tests, frontend build |
| 지원 현황 | 지원 목록, 상태 이력, 메모, 문서 버전 고정 | VERIFIED_LOCAL | backend/frontend 검증 |
| 일정 | 일정 CRUD, 신뢰도, 마감/면접 관리 | VERIFIED_LOCAL | backend/frontend 검증 |
| 대시보드 | 지원/일정/마감/AI/문서/연동 요약 | VERIFIED_LOCAL | backend tests, frontend type-check/build |
| Google Calendar | OAuth/캘린더 선택/동기화 기반 | VERIFIED_MOCK | 실제 Google API는 NEEDS_VERIFICATION |
| Gmail | 채용 메일 후보 분석/사용자 승인 반영 기반 | VERIFIED_MOCK | 실제 Gmail API는 NEEDS_VERIFICATION |
| 추천 | 저장 공고 기반 규칙 추천, 이력, 설정, 자동 실행 기반 | VERIFIED_LOCAL | RULE_BASED 추천 |
| 알림 | in-app 알림, 알림 설정, due reminder worker, mock email delivery | VERIFIED_LOCAL | worker 1회 실행 확인 |
| 운영 안정화 | request id, 보안 헤더, CORS, rate limit, health, audit logs | VERIFIED_LOCAL | backend tests 및 smoke 통과 |
| E2E | 주요 MVP 화면 10개 이상 route smoke | VERIFIED_E2E | Playwright 15 passed |
| 배포 준비 | Docker Compose, E2E compose, Nginx 예시, smoke/performance 스크립트 | VERIFIED_LOCAL | 실제 운영 배포는 NEEDS_VERIFICATION |
| 문서 | 사용자 가이드, 운영 가이드, release checklist, release notes, security review | VERIFIED_LOCAL | v1.0.0 문서 최신화 |

## MVP 제외 또는 운영 검증 필요 항목

| 항목 | 상태 | 이유 |
| --- | --- | --- |
| 외부 채용 사이트 자동 크롤링 | EXCLUDED | 약관/robots/법적 검토 전까지 MVP 제외 |
| 자동 지원서 제출 | EXCLUDED | 사용자 명시 승인과 외부 사이트 정책 검토 필요 |
| Push 알림 provider | NOT_IMPLEMENTED | v1.0.0은 in-app/mock email 중심 |
| 실제 SMTP 메일 발송 | NEEDS_VERIFICATION | 운영 SMTP 계정과 도메인 검증 필요 |
| 실제 OpenAI 호출 | NEEDS_VERIFICATION | 운영 API key/model/비용 한도 설정 필요 |
| 실제 Google Calendar/Gmail API | NEEDS_VERIFICATION | 운영 OAuth consent, redirect URI, scope 검증 필요 |
| 분산 worker lock/queue 운영 | NEEDS_VERIFICATION | 단일 worker 기준 검증 완료, 다중 인스턴스 검증 필요 |
| Redis 기반 분산 rate limit | NEEDS_VERIFICATION | 현재는 로컬/프로세스 기준 rate limit |
| 운영 자동 확장 | EXCLUDED | MVP 배포 이후 인프라 단계에서 검토 |
| 네이티브 모바일 앱 | EXCLUDED | 웹 MVP 범위 외 |
| 운영 DB restore 리허설 | NEEDS_VERIFICATION | 절차 문서화 완료, 실제 staging restore 필요 |
| 실제 운영 배포 | NEEDS_VERIFICATION | 로컬 Docker smoke 완료, production 배포는 별도 승인 필요 |

## 릴리스별 완료 요약

| 버전 | 핵심 내용 | 상태 |
| --- | --- | --- |
| v0.1.0 | 프로젝트 기반, Docker Compose, Health API | VERIFIED_LOCAL |
| v0.1.1 | 회원/인증 | VERIFIED_LOCAL |
| v0.1.2 | 커리어 프로필 | VERIFIED_LOCAL |
| v0.1.3 | Google/GitHub OAuth 로그인 기반 | VERIFIED_MOCK |
| v0.1.4 | 계정 보안·복구 | VERIFIED_LOCAL |
| v0.2.0 | 채용공고 관리 | VERIFIED_LOCAL |
| v0.2.1 | AI 채용공고 분석 | VERIFIED_MOCK |
| v0.2.2 | 사용자-공고 적합도 분석 | VERIFIED_MOCK |
| v0.3.0 | 이력서 업로드 | VERIFIED_LOCAL |
| v0.3.1 | 이력서 텍스트 추출 | VERIFIED_LOCAL |
| v0.3.2 | AI 이력서 구조화 분석 | VERIFIED_MOCK |
| v0.3.3 | 맞춤 지원 문서 생성 | VERIFIED_MOCK |
| v0.4.0 | 지원 현황 관리 | VERIFIED_LOCAL |
| v0.4.1 | 일정 관리 | VERIFIED_LOCAL |
| v0.4.2 | 대시보드 | VERIFIED_LOCAL |
| v0.5.0 | Google Calendar 연동 기반 | VERIFIED_MOCK |
| v0.5.1 | Gmail 채용 메일 분석 기반 | VERIFIED_MOCK |
| v0.6.0 | 규칙 기반 채용공고 추천 | VERIFIED_LOCAL |
| v0.6.1 | 추천 UX 및 자동 실행 기반 | VERIFIED_LOCAL |
| v0.7.0 | AI 지원 문서 개선 루프 | VERIFIED_MOCK |
| v0.8.0 | 알림·리마인더 운영화 | VERIFIED_LOCAL |
| v0.9.0 | E2E·성능·보안 안정화 | VERIFIED_E2E |
| v1.0.0 | MVP 릴리스 준비·검증·문서화 | VERIFIED_LOCAL |
