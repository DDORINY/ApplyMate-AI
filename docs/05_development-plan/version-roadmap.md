# 버전 로드맵

## 기준

- 현재 버전: v0.2.2
- 기준 commit: `8d003c3`
- 기준 tag: `v0.2.2`

## 완료 버전

| 버전 | 상태 | 핵심 범위 | 상세 문서 |
| --- | --- | --- | --- |
| v0.1.0 | 완료 | 프로젝트 기반, Health API, Docker Compose | [v0.1.0](../11_releases/v0.1.0-foundation.md) |
| v0.1.1 | 완료 | 이메일 회원가입/로그인, JWT, refresh token | [v0.1.1](../11_releases/v0.1.1-authentication.md) |
| v0.1.2 | 완료 | 커리어 프로필, 기술, 경력, 프로젝트, 희망/제외 조건 | [v0.1.2](../11_releases/v0.1.2-career-profile.md) |
| v0.1.3 | 완료 | Google/GitHub OAuth, 계정 연결 | [v0.1.3](../11_releases/v0.1.3-social-authentication.md) |
| v0.1.4 | 완료 | 이메일 인증, 비밀번호 복구, 세션, 보안 이벤트 | [v0.1.4](../11_releases/v0.1.4-account-security.md) |
| v0.2.0 | 완료 | 채용공고 등록/관리, URL 등록, SSRF 방어 | [v0.2.0](../11_releases/v0.2.0-job-posting-management.md) |
| v0.2.1 | 완료 | AI 채용공고 분석, provider abstraction, 분석 이력 | [v0.2.1](../11_releases/v0.2.1-ai-job-analysis.md) |
| v0.2.2 | 완료 | 사용자-공고 적합도 분석, 점수, 피드백 | [v0.2.2](../11_releases/v0.2.2-job-matching.md) |

## 예정 버전

| 버전 | 상태 | 목적 |
| --- | --- | --- |
| v0.3.0 | 예정 | 이력서 파일 업로드 |
| v0.3.1 | 예정 | 이력서 텍스트 추출 |
| v0.3.2 | 예정 | AI 이력서 구조화 분석 |
| v0.3.3 | 예정 | 맞춤 지원 문서 생성 |
| v0.4.0 | 예정 | 지원 현황 관리 |
| v0.4.1 | 예정 | 일정 관리 |
| v0.4.2 | 예정 | 대시보드 |
| v0.5.0 | 예정 | Google Calendar 연동 |
| v0.5.1 | 예정 | Gmail 채용 메일 분석 |
| v0.6.0 | 예정 | 추천 시스템 기반 |
| v0.6.1 | 예정 | 정기 추천 |
| v1.0.0 | 예정 | MVP 통합 안정화 |

자세한 향후 계획은 [future-detailed-plan.md](future-detailed-plan.md)를 기준으로 한다.

## 로드맵 원칙

- 완료 상태는 실제 main 코드, migration, 테스트, tag 기준으로만 표시한다.
- 예정 기능은 현재 API 명세에 완료 기능처럼 포함하지 않는다.
- 제외 기능은 [excluded-features.md](excluded-features.md)에 분리한다.
- 보류 기능은 [deferred-features.md](deferred-features.md)에 분리한다.
