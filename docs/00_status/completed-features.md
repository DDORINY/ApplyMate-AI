# 완료 기능 목록

## 기반 시스템

| 항목 | 내용 |
| --- | --- |
| 최초 구현 버전 | v0.1.0 |
| 관련 API | `GET /api/v1/health` |
| 관련 DB | 없음 |
| 관련 Frontend | `/` |
| 테스트 | Health API 테스트 |
| 제한사항 | 운영 배포 자동화는 아직 없음 |

## 인증

| 항목 | 내용 |
| --- | --- |
| 최초 구현 버전 | v0.1.1 |
| 관련 API | `/auth/signup`, `/auth/login`, `/auth/refresh`, `/auth/logout`, `/auth/me` |
| 관련 DB | `users`, `refresh_tokens` |
| 관련 Frontend | `/signup`, `/login`, `/me` |
| 테스트 | 인증/refresh/logout/reuse 테스트 |
| 제한사항 | 운영 HTTPS Cookie 설정 필요 |

## 소셜 인증

| 항목 | 내용 |
| --- | --- |
| 최초 구현 버전 | v0.1.3 |
| 관련 API | `/auth/oauth/*` |
| 관련 DB | `oauth_accounts`, `oauth_states`, `oauth_login_tickets` |
| 관련 Frontend | `/auth/callback`, `/settings/accounts` |
| 테스트 | OAuth state/ticket/link/unlink 테스트 |
| 제한사항 | 실제 provider credential 기반 운영 로그인 미검증 |

## 계정 보안

| 항목 | 내용 |
| --- | --- |
| 최초 구현 버전 | v0.1.4 |
| 관련 API | 이메일 인증, 비밀번호 복구, 세션, 보안 이벤트 API |
| 관련 DB | `email_verification_tokens`, `password_reset_tokens`, `security_events` |
| 관련 Frontend | `/verify-email`, `/forgot-password`, `/reset-password`, `/settings/security` |
| 테스트 | 계정 보안/세션/비밀번호 테스트 |
| 제한사항 | 운영 SMTP 발송 미검증 |

## 커리어 프로필

| 항목 | 내용 |
| --- | --- |
| 최초 구현 버전 | v0.1.2 |
| 관련 API | `/profiles/*` |
| 관련 DB | `career_profiles`, `skills`, `user_skills`, `experiences`, `projects`, `project_skills`, `job_preferences`, `excluded_conditions`, `portfolio_links` |
| 관련 Frontend | `/profile` |
| 테스트 | 프로필 CRUD/소유권/검증 테스트 |
| 제한사항 | 교육/자격증 별도 모델 없음 |

## 채용공고 관리

| 항목 | 내용 |
| --- | --- |
| 최초 구현 버전 | v0.2.0 |
| 관련 API | `/jobs`, `/jobs/import-url`, `/jobs/{jobId}` |
| 관련 DB | `companies`, `job_postings` |
| 관련 Frontend | `/jobs`, `/jobs/new`, `/jobs/{jobId}` |
| 테스트 | CRUD, 중복, SSRF 방어 테스트 |
| 제한사항 | 사이트별 crawler 없음 |

## AI 채용공고 분석

| 항목 | 내용 |
| --- | --- |
| 최초 구현 버전 | v0.2.1 |
| 관련 API | `/ai/providers`, `/jobs/{jobId}/analysis` |
| 관련 DB | `job_analyses`, `job_analysis_runs` |
| 관련 Frontend | `/jobs/{jobId}` AI 분석 패널 |
| 테스트 | mock/disabled/openai config, outdated, run history 테스트 |
| 제한사항 | 실제 OpenAI API 호출 미검증 |

## 사용자-공고 적합도 분석

| 항목 | 내용 |
| --- | --- |
| 최초 구현 버전 | v0.2.2 |
| 관련 API | `/jobs/{jobId}/match`, `/jobs/{jobId}/match/feedback` |
| 관련 DB | `job_matches`, `job_match_runs`, `job_match_feedback` |
| 관련 Frontend | `/jobs/{jobId}` 적합도 패널 |
| 테스트 | 점수 계산, outdated, feedback, exclusion 테스트 |
| 제한사항 | AI가 숫자 점수를 계산하지 않음, batch 계산 없음 |
