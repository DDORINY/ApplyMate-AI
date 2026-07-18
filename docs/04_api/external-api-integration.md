# 외부 API 연동

## 개요

외부 API 연동은 버전별로 단계적으로 도입합니다. v0.1.3에서는 Google/GitHub OAuth 로그인만 실제 호출 대상으로 구현했습니다. AI, Calendar, Gmail, 채용공고 공개 API는 향후 범위입니다.

## 현재 구현

| 서비스 | 목적 | 상태 |
| --- | --- | --- |
| Google OAuth | 로그인, 계정 연결, 검증 이메일 조회 | v0.1.3 구현 |
| GitHub OAuth | 로그인, 계정 연결, 검증 이메일 조회 | v0.1.3 구현 |

## 향후 연동 후보

| 서비스 | 목적 | 예정 버전 |
| --- | --- | --- |
| OpenAI API | 채용공고 분석, 지원 문서 생성, 면접 질문 생성 | v0.2.x 이후 |
| Google Calendar API | 지원 일정 캘린더 등록 및 동기화 | v0.5.x |
| Gmail API | 채용 관련 메일 분석 및 일정 추출 | v0.5.x |
| 채용공고 공개 API | 공고 수집 | v0.6.x |
| GitHub API | 사용자 프로젝트 참고 자료 수집 | v1.0 이후 검토 |

## OAuth v0.1.3 원칙

- Provider access token은 서비스 DB에 저장하지 않습니다.
- Provider 사용자 식별자, 이메일, username, display name 등 최소 정보만 저장합니다.
- 검증된 이메일이 없는 provider 계정은 로그인/연결을 허용하지 않습니다.
- OAuth state와 login ticket 원문은 저장하지 않고 hash만 저장합니다.
- Provider 장애는 서비스 내부 데이터 저장 실패로 전파되지 않도록 명확한 오류 코드로 처리합니다.

## 공통 연동 원칙

- 사용자의 명시적 승인 없이 외부 계정을 연결하지 않습니다.
- API key와 OAuth secret은 저장소에 커밋하지 않습니다.
- 외부 API 응답은 필요한 필드만 저장합니다.
- 기능별 rate limit, 재시도, 로그 정책을 별도로 정의합니다.
