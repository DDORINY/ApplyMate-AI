# 기능 상태 매트릭스

상태 값:

- `COMPLETED`
- `PARTIAL`
- `PLANNED`
- `DEFERRED`
- `EXCLUDED`
- `NEEDS_VERIFICATION`

| 영역 | 기능 | 상태 | 구현 버전 | Backend | Frontend | DB | 테스트 | 실제 외부 검증 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 기반 | Health/API 기본 구조 | COMPLETED | v0.1.0 | Yes | Partial | No | Yes | Local only |
| 인증 | 이메일 회원가입/로그인 | COMPLETED | v0.1.1 | Yes | Yes | Yes | Yes | Local only |
| 인증 | Refresh Token rotation | COMPLETED | v0.1.1 | Yes | Yes | Yes | Yes | Local only |
| 인증 | Google OAuth | NEEDS_VERIFICATION | v0.1.3 | Yes | Yes | Yes | Yes | 실제 provider 미검증 |
| 인증 | GitHub OAuth | NEEDS_VERIFICATION | v0.1.3 | Yes | Yes | Yes | Yes | 실제 provider 미검증 |
| 계정 보안 | 이메일 인증 | NEEDS_VERIFICATION | v0.1.4 | Yes | Yes | Yes | Yes | 운영 SMTP 미검증 |
| 계정 보안 | 비밀번호 복구 | COMPLETED | v0.1.4 | Yes | Yes | Yes | Yes | 개발 outbox 검증 |
| 계정 보안 | 세션 관리 | COMPLETED | v0.1.4 | Yes | Yes | Yes | Yes | Local only |
| 프로필 | 커리어 프로필 | COMPLETED | v0.1.2 | Yes | Yes | Yes | Yes | Local only |
| 프로필 | 기술/경력/프로젝트 | COMPLETED | v0.1.2 | Yes | Yes | Yes | Yes | Local only |
| 프로필 | 희망/제외 조건 | COMPLETED | v0.1.2 | Yes | Yes | Yes | Yes | Local only |
| 채용공고 | 공고 CRUD | COMPLETED | v0.2.0 | Yes | Yes | Yes | Yes | Local DB |
| 채용공고 | URL 등록 | PARTIAL | v0.2.0 | Yes | Yes | Yes | Yes | 일반 HTML 제한 |
| 채용공고 | 대규모 crawling | EXCLUDED | - | No | No | No | No | 정책상 제외 |
| AI | 공고 구조화 분석 | NEEDS_VERIFICATION | v0.2.1 | Yes | Yes | Yes | Yes | 실제 OpenAI 미검증 |
| AI | Mock Provider | COMPLETED | v0.2.1 | Yes | No | No | Yes | Local only |
| 적합도 | 사용자-공고 적합도 | COMPLETED | v0.2.2 | Yes | Yes | Yes | Yes | Local only |
| 적합도 | 적합도 피드백 | COMPLETED | v0.2.2 | Yes | Yes | Yes | Yes | Local only |
| 이력서 | 파일 업로드 | PLANNED | v0.3.0 | No | No | No | No | - |
| 문서 | 자기소개서 생성 | PLANNED | v0.3.3 | No | No | No | No | - |
| 지원 | 지원 현황 관리 | PLANNED | v0.4.0 | No | No | No | No | - |
| 일정 | Google Calendar | DEFERRED | v0.5.0 | No | No | No | No | - |
