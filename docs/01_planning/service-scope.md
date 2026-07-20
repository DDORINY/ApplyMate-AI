# ApplyMate AI 서비스 범위

문서 기준 버전: `v1.0.0`

## 1. 서비스 정의

ApplyMate AI는 개인 사용자가 취업 준비 과정을 한곳에서 관리할 수 있도록 돕는 AI 기반 취업 매니저다. 커리어 프로필, 채용공고, 이력서, 지원 문서, 지원 현황, 일정, 추천, 알림을 연결해 “공고 발견 → 분석 → 지원 준비 → 일정 관리 → 후속 관리” 흐름을 지원한다.

## 2. v1.0.0 MVP 포함 범위

| 영역 | 포함 기능 | 상태 |
| --- | --- | --- |
| 회원/인증 | 회원가입, 로그인, JWT, refresh token, 로그아웃, 현재 사용자 조회 | VERIFIED_LOCAL |
| 계정 보안 | 이메일 인증, 비밀번호 복구, 세션 관리, 보안 이벤트 | VERIFIED_LOCAL |
| OAuth | Google/GitHub 로그인 기반, 계정 연결 | VERIFIED_MOCK |
| 커리어 프로필 | 기본 프로필, 경력, 프로젝트, 기술, 희망 조건 | VERIFIED_LOCAL |
| 채용공고 | 공고 CRUD, URL 등록, 중복 검사, 검색/필터 | VERIFIED_LOCAL |
| AI 공고 분석 | 공고 요약, 요구사항, 기술, 위험 요소 분석 | VERIFIED_MOCK |
| 적합도 분석 | 사용자-공고 점수, 등급, 근거, 부족 조건 | VERIFIED_MOCK |
| 이력서 | PDF/DOCX 업로드, 다운로드, 삭제, 텍스트 추출, 사용자 보정 | VERIFIED_LOCAL |
| AI 이력서 분석 | 구조화 분석, 프로필 반영 후보 | VERIFIED_MOCK |
| 지원 문서 | 근거 기반 문서 생성, 버전, 출처, 실행 이력 | VERIFIED_MOCK |
| 문서 개선 | 문장별 개선 제안, 승인/거절, 새 버전 생성 | VERIFIED_MOCK |
| 지원 현황 | 지원 목록, 상태 이력, 메모, 제출 문서 버전 고정 | VERIFIED_LOCAL |
| 일정 | 일정 CRUD, reminder, 신뢰도, 변경 이력 | VERIFIED_LOCAL |
| 대시보드 | 지원/일정/마감/AI/문서/활동 요약 | VERIFIED_LOCAL |
| Google Calendar | OAuth, calendar 선택, sync mapping/run/error 기반 | VERIFIED_MOCK |
| Gmail | read-only OAuth, 채용 메일 후보 분석, 승인 기반 반영 | VERIFIED_MOCK |
| 추천 | 저장 공고 기반 규칙 추천, 추천 이력, 설정, 피드백 | VERIFIED_LOCAL |
| 알림 | in-app 알림, 알림 설정, delivery 이력, due reminder worker | VERIFIED_LOCAL |
| 운영 안정화 | request id, 보안 헤더, CORS, rate limit, health, audit logs | VERIFIED_LOCAL |
| 릴리스 문서 | 사용자 가이드, 운영 가이드, 체크리스트, 보안 리뷰, 릴리스 노트 | VERIFIED_LOCAL |

## 3. v1.0.0 제외 범위

- 외부 채용 사이트 자동 크롤링
- 외부 채용 사이트 자동 지원서 제출
- Push 알림 provider 실제 발송
- 운영 자동 확장
- 네이티브 모바일 앱
- 사용자가 제공하지 않은 경력/성과/수치의 AI 임의 생성
- 사용자 승인 없는 Gmail 기반 지원 상태 변경 또는 일정 생성

## 4. 운영 검증 필요 범위

| 항목 | 상태 | 이유 |
| --- | --- | --- |
| 실제 OpenAI 호출 | NEEDS_VERIFICATION | 운영 API key/model/비용 한도 설정 필요 |
| 실제 Google Calendar API | NEEDS_VERIFICATION | 운영 OAuth consent, redirect URI, scope 확인 필요 |
| 실제 Gmail API | NEEDS_VERIFICATION | 운영 OAuth scope와 mailbox 접근 검증 필요 |
| 실제 SMTP 발송 | NEEDS_VERIFICATION | 운영 SMTP 계정, 도메인 인증, 발송 제한 검증 필요 |
| 운영 배포 | NEEDS_VERIFICATION | 실제 서버/도메인/HTTPS/secret 주입 확인 필요 |
| 운영 DB restore | NEEDS_VERIFICATION | staging 또는 production-like 환경 리허설 필요 |

## 5. 외부 연동 원칙

- OpenAI 실제 호출은 mock/local 검증과 분리해 관리한다.
- Google Calendar 실제 일정 생성은 사용자 연결 상태와 권한을 확인한 뒤 수행한다.
- Gmail은 read-only 최소 권한을 원칙으로 하며, 상태 변경/일정 생성은 사용자 승인 후 반영한다.
- OAuth token과 provider secret은 API 응답이나 로그에 노출하지 않는다.
- 외부 provider 장애가 내부 데이터 저장 실패로 직접 이어지지 않도록 분리한다.

## 6. v1.0.0 완료 판단

v1.0.0은 MVP 로컬 릴리스 기준으로 완료 상태다. 실제 운영 배포와 외부 provider live 검증은 릴리스 이후 별도 운영 단계에서 진행한다.
