# Unverified Items

## 2026-07-20 현재 로컬 환경 메모

| 항목 | 상태 | 사유 |
| --- | --- | --- |
| 기본 Docker PostgreSQL 연결 | NOT_CONNECTED | 기존 기본 Docker volume의 DB 비밀번호가 현재 `.env` DB 자격 증명과 맞지 않는다. volume은 삭제하지 않았다. |
| 현재 `.env` 기준 Gmail 연동 | NOT_CONNECTED | `GMAIL_PROVIDER`가 비어 있고 Gmail OAuth client/secret 변수가 없어서 Compose에서 `disabled`로 해석된다. |
| 실제 OpenAI 호출 | NOT_CONNECTED | `AI_PROVIDER=mock`이며 `OPENAI_API_KEY`, `OPENAI_MODEL`이 비어 있다. v0.7.0 문서 개선은 mock provider로 검증했다. |
| 실제 SMTP 알림 발송 | NEEDS_VERIFICATION | v0.8.0은 mock email provider와 delivery 구조를 검증했고 실제 외부 SMTP 발송은 검증하지 않았다. |
| Push 알림 실발송 | EXCLUDED | v0.8.0은 push 설정 구조만 제공하며 provider 실발송은 구현하지 않는다. |
| Google Calendar live API | NEEDS_VERIFICATION | Calendar provider와 credential은 설정되어 있으나 실제 Google OAuth/API 동작은 별도 live 검증이 필요하다. |
| SMTP 실제 발송 | NEEDS_VERIFICATION | SMTP credential은 설정되어 있으나 실제 외부 메일 발송은 이번 확인 범위에서 검증하지 않았다. |
| 추천 자동 실행 스케줄러 | DEFERRED | v0.6.0은 수동 생성 API/화면까지 구현하고 일일 자동 실행은 후속 범위로 둔다. |
| 실제 Background Worker 추천 실행 | DEFERRED | v0.6.1은 설정, 실행 조건, 수동 API, Snapshot, 알림 후보까지만 구현한다. |
| `pip-audit` | NEEDS_VERIFICATION | 현재 로컬 Python 환경에 `pip_audit` 모듈이 설치되어 있지 않다. |
| npm audit moderate 2건 | NEEDS_REVIEW | Next 내부 PostCSS advisory이며 자동 fix가 Next major downgrade를 제안해 보류했다. |
| 실제 운영 부하 테스트 | NEEDS_VERIFICATION | v0.9.0은 성능 목표와 대상 endpoint를 문서화했으며 실측 부하 테스트는 수행하지 않았다. |
| 운영 DB 복구 리허설 | NEEDS_VERIFICATION | 백업/복구 문서는 작성했지만 실제 운영 복구 테스트는 수행하지 않았다. |

자세한 안전 요약은 [환경 연결 상태](environment-connection-status.md)를 기준으로 한다.

## 운영 환경 검증 필요

| 항목 | 상태 | 이유 |
| --- | --- | --- |
| 실제 OpenAI 호출 | NEEDS_VERIFICATION | 운영 API key/model 설정과 비용 확인 필요 |
| 운영 Google/GitHub OAuth | NEEDS_VERIFICATION | 운영 client/secret/redirect URI 필요 |
| 운영 SMTP | NEEDS_VERIFICATION | 실제 메일 발송 계정과 도메인 검증 필요 |
| HTTPS Cookie/SameSite | NEEDS_VERIFICATION | 운영 도메인과 HTTPS 환경에서 검증 필요 |
| 운영 배포 | NEEDS_VERIFICATION | 서버/도메인/DB/Redis 환경 필요 |
| 브라우저 E2E 자동화 | VERIFIED_LOCALLY | v0.9.0 Playwright smoke 3개 시나리오 통과 |

## v0.9.0 제외 또는 후속 범위

| 항목 | 상태 | 후속 버전 |
| --- | --- | --- |
| Redis 기반 분산 rate limit | DEFERRED | 다중 backend instance 운영 시 |
| 장기 scheduler/분산 worker lock | DEFERRED | v1.0.0 운영 설계 |
| 실제 운영 부하 테스트 | NEEDS_VERIFICATION | staging/production-like 환경 |
| 운영 DB restore 리허설 | NEEDS_VERIFICATION | staging DB |
| Critical/High dependency audit 자동화 | NEEDS_VERIFICATION | CI 구성 후 |

## v0.7.0 제외 또는 후속 범위

| 항목 | 상태 | 후속 버전 |
| --- | --- | --- |
| 실제 OpenAI 기반 지원 문서 개선 | NEEDS_VERIFICATION | API key/model 설정, 비용, 운영 프롬프트 검증 후 |
| 자동 전체 적용 | EXCLUDED | 사용자가 제안을 승인해야만 새 버전을 생성한다. |
| 근거 없는 성과/수치 자동 생성 | EXCLUDED | 사실성 정책상 금지 |
| 외부 웹 검색 기반 기업 인재상 추정 | EXCLUDED | 사용자/저장 공고/분석 근거 없이 추가하지 않는다. |

## v0.8.0 제외 또는 후속 범위

| 항목 | 상태 | 후속 버전 |
| --- | --- | --- |
| 실제 SMTP 알림 발송 | NEEDS_VERIFICATION | 운영 SMTP 계정과 도메인 검증 후 |
| Push provider 실발송 | EXCLUDED | provider 선정 후 별도 구현 |
| 장기 실행 production queue worker | DEFERRED | v0.9.0 worker 안정화 |

## v0.6.0 제외 또는 후속 범위

| 항목 | 상태 | 후속 버전 |
| --- | --- | --- |
| 외부 채용 사이트 자동 크롤링 | EXCLUDED | 정책상 기본 기능에서 제외 |
| AI/ML 기반 추천 모델 | EXCLUDED | v0.6.0은 `RULE_BASED`만 제공 |
| 일일 추천 자동 실행 스케줄러 | DEFERRED | v0.6.1 이후 |
| 추천 알림 발송 | DEFERRED | 알림/리마인더 운영화 단계 |
| 피드백 기반 자동 학습 | DEFERRED | 사용자 통제 정책 설계 후 |

## v0.6.1 제외 또는 후속 범위

| 항목 | 상태 | 후속 버전 |
| --- | --- | --- |
| 실제 Background Worker 운영 | DEFERRED | 운영 스케줄러 설계 후 |
| 실제 이메일/푸시 추천 알림 발송 | DEFERRED | v0.8.0 알림 운영화 |
| 외부 채용 사이트 자동 수집 | EXCLUDED | 정책상 기본 기능에서 제외 |
| 피드백 기반 가중치 자동 학습 | DEFERRED | 사용자 통제 정책 설계 후 |

## v0.4.2 제외 또는 후속 범위

| 항목 | 상태 | 후속 버전 |
| --- | --- | --- |
| 대시보드 위젯 사용자 커스터마이징 | DEFERRED | 미정 |
| 대시보드 차트 라이브러리 기반 고급 시각화 | DEFERRED | 미정 |
| 이메일/푸시 알림 실제 발송 | PLANNED | 미정 |
| 백그라운드 알림 워커 | PLANNED | 미정 |
| Google Calendar 실제 일정 생성/수정/삭제 | NEEDS_VERIFICATION | 운영 Google Cloud OAuth credentials와 consent 설정 필요 |
| Gmail 실제 OAuth token exchange/search/fetch | NEEDS_VERIFICATION | 운영 Google Cloud OAuth credentials와 consent 설정 필요 |
| 실제 OpenAI Gmail 메일 분석 | NEEDS_VERIFICATION | API key/model 및 비용 검증 필요 |
| 반복 일정 | DEFERRED | 미정 |
| 일정 생성에 따른 지원 상태 자동 변경 | DEFERRED | 사용자 승인 흐름 설계 후 |
