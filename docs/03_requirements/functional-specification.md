# Functional Specification

문서 기준 버전: `v1.0.0`

ApplyMate AI v1.0.0은 개인용 AI 취업 매니저 MVP다. 사용자의 커리어 정보, 채용공고, 이력서, 지원 문서, 지원 현황, 일정, 추천, 알림을 하나의 흐름으로 연결한다.

## MVP 기능 범위

| 영역 | 요구사항 |
| --- | --- |
| 인증/회원 | 이메일 회원가입, 로그인, JWT access/refresh token, 로그아웃, 현재 사용자 조회, 이메일 인증, 비밀번호 복구, 세션 관리 |
| OAuth | Google/GitHub 로그인 기반, 계정 연결/해제, OAuth state 검증 |
| 커리어 프로필 | 기본 프로필, 경력, 프로젝트, 기술, 희망 직무/지역/근무 조건 관리 |
| 채용공고 | 공고 등록, 목록, 상세, 수정, 삭제, URL 기반 등록, 중복 검사 |
| AI 공고 분석 | 공고 요약, 주요 요구사항, 기술, 위험 요소, 분석 실행 이력 저장 |
| 적합도 분석 | 사용자 프로필과 공고의 점수, 등급, 근거, 부족 조건 산출 |
| 이력서 | PDF/DOCX 업로드, 검증, 다운로드, 삭제, 텍스트 추출, 사용자 보정 |
| AI 이력서 분석 | 이력서 내용을 구조화하고 커리어 프로필에 반영 가능한 후보 생성 |
| 지원 문서 | 공고/프로필/이력서 근거 기반 자기소개서·지원 문서 생성, 버전 관리, 출처 저장 |
| 문서 개선 | 문장별 개선 제안, 승인/거절, 승인된 제안만 새 문서 버전으로 반영 |
| 지원 현황 | 지원 목록, 상태 변경 이력, 메모, 제출 문서 버전 고정 |
| 일정 | 일정 CRUD, 마감/면접/과제 등 event type, 신뢰도, reminder, 변경 이력 |
| 대시보드 | 지원 상태, 일정, 마감, 최근 AI 분석, 최근 문서, 최근 활동 요약 |
| Google Calendar | Calendar OAuth, calendar 선택, 동기화 mapping/run/error 저장 기반 |
| Gmail | Gmail read-only OAuth, 채용 메일 후보 분석, 사용자 승인 기반 반영 |
| 추천 | 저장된 공고 기반 RULE_BASED 추천, 추천 이유, 부족 조건, 피드백, 이력, 설정 |
| 알림 | in-app 알림, 알림 설정, 알림 delivery 이력, due reminder worker |
| 운영 안정화 | request id, 보안 헤더, CORS, rate limit, live/ready health, audit logs |
| 문서/릴리스 | 사용자 가이드, 운영 가이드, release checklist, known limitations, security review, release notes |

## 공통 요구사항

- 모든 API는 `/api/v1` 하위 경로를 사용한다.
- 인증이 필요한 API는 bearer access token을 요구한다.
- 사용자 소유 데이터는 반드시 `user_id` 기준 소유권 검사를 수행한다.
- 성공/오류 응답 구조는 기존 공통 구조를 유지한다.
- 오류 응답에는 가능한 경우 request id를 포함한다.
- 비밀번호, refresh token, OAuth token, provider secret, API key는 로그/응답에 노출하지 않는다.
- AI 결과는 구조화된 형식으로 검증하고, 근거 없는 사실·수치·성과를 생성하지 않는다.
- 외부 provider 실패가 내부 데이터 저장 실패로 직접 이어지지 않도록 분리한다.
- 파일 업로드는 확장자, MIME, signature, 크기, 경로 조작 가능성을 검증한다.
- 일정 신뢰도는 `CONFIRMED`, `ESTIMATED`, `USER_INPUT`으로 구분한다.

## v1.0.0 인수 기준

- Backend test가 통과해야 한다.
- Frontend lint, type-check, build가 통과해야 한다.
- Playwright E2E는 MVP 주요 화면 10개 이상을 확인해야 한다.
- Alembic head가 `20260720_0300`이어야 한다.
- Docker Compose config, migration upgrade/downgrade/upgrade, smoke test가 통과해야 한다.
- dependency audit에서 Critical/High 차단 이슈가 없어야 한다.
- 실제 OpenAI/Gmail/Calendar/SMTP 호출은 mock/local 검증과 분리해 `NEEDS_VERIFICATION`으로 표시한다.

## MVP 제외 항목

- 외부 채용 사이트 자동 크롤링
- 자동 지원서 제출
- Push provider 실제 발송
- 운영 자동 확장
- 네이티브 모바일 앱
- 사용자가 제공하지 않은 경력/성과/수치의 AI 임의 생성
- 사용자 승인 없는 Gmail 기반 상태 변경 또는 일정 생성
