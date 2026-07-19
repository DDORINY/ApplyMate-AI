# Completed Features

## 완료 버전

| 버전 | 완료 기능 |
| --- | --- |
| v0.1.0 | 프로젝트 기반, Docker Compose, Health API |
| v0.1.1 | 회원가입, 로그인, JWT/Refresh Token 인증 |
| v0.1.2 | 커리어 프로필, 경력, 프로젝트, 기술, 희망 조건 |
| v0.1.3 | Google/GitHub OAuth 로그인과 계정 연결 |
| v0.1.4 | 이메일 인증, 비밀번호 복구, 비밀번호 변경, 세션 관리, 보안 이벤트 |
| v0.2.0 | 채용공고 등록/목록/상세/수정/삭제, URL 기반 등록 |
| v0.2.1 | AI 채용공고 분석과 분석 이력 |
| v0.2.2 | 사용자-공고 적합도 분석과 피드백 |
| v0.3.0 | 이력서 메타데이터, PDF/DOCX 업로드, 다운로드, 삭제 |
| v0.3.1 | 이력서 텍스트 추출, 사용자 편집, 재추출 이력 |
| v0.3.2 | AI 이력서 구조화 분석, 후보 데이터, 실행 이력 |
| v0.3.3 | 맞춤 지원 문서 생성, 버전 관리, 출처 조회, 실행 이력 |
| v0.4.0 | 지원 현황 CRUD, 상태 변경 이력, 지원 메모, 제출 문서 버전 고정 |
| v0.4.1 | 일정 CRUD, 상태/신뢰도, 알림 저장, 충돌 표시, 임박 일정, 변경 이력 |

## v0.4.1 완료 상세

- `/api/v1/calendar/events` 일정 생성/목록/상세/수정/보관
- `/api/v1/calendar/events/{eventId}/status` 상태 변경
- `/api/v1/calendar/events/{eventId}/history` 변경 이력 조회
- `/api/v1/calendar/events/{eventId}/reminders` 알림 생성/조회/수정/삭제
- `/api/v1/calendar/conflicts` 시간 충돌 조회
- `/api/v1/calendar/upcoming` 임박 일정 조회
- `/api/v1/calendar/options` 일정 생성 선택 옵션 조회
- `/calendar`, `/calendar/new`, `/calendar/events/{eventId}` 프론트 화면
- 지원 상세와 채용공고 상세의 일정 연결 진입점
