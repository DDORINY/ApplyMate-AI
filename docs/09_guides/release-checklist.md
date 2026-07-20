# v1.0.0 Release Checklist

문서 기준일: 2026-07-20  
대상 브랜치: `feature/v1.0.0-mvp-release`  
대상 태그: `v1.0.0`

## 최종 체크리스트

| 항목 | 상태 | 결과 |
| --- | --- | --- |
| Version | DONE | backend/frontend `1.0.0` |
| Branch | DONE | `feature/v1.0.0-mvp-release` |
| Backend lint | PASS | `python -m ruff check app tests scripts` |
| Backend tests | PASS | `171 passed` |
| Frontend lint | PASS | `npm run lint` |
| Frontend type-check | PASS | `npm run type-check` |
| Frontend build | PASS | `npm run build` |
| E2E | PASS | Playwright `15 passed` |
| Migration head | PASS | `20260720_0300 (head)` |
| Migration rollback | PASS | `20260720_0300 -> 20260720_0200 -> 20260720_0300` |
| Docker Compose config | PASS | `docker compose ... config --quiet` |
| Docker smoke | PASS | live/ready/openapi 200 |
| Worker | PASS | `docker compose ... run --rm worker` 정상 종료 |
| Demo seed payload | PASS | `backend/scripts/seed_demo_data.py` JSON payload 생성 |
| npm audit | PASS | vulnerabilities 0 |
| pip-audit | PASS | 프로젝트 전용 임시 venv 기준 known vulnerabilities 0 |
| Secret scan | PASS | tracked source/env 제외 기준 매칭 없음 |
| Security review | DONE | `docs/12_audits/v1.0.0-security-review.md` |
| Performance smoke | PASS | 15 requests, concurrency 3, errors 0 |
| Backup/restore | NEEDS_VERIFICATION | 절차 문서화 완료, staging/production restore 리허설 필요 |
| Deployment | NEEDS_VERIFICATION | 로컬 Docker 검증 완료, 실제 운영 배포는 별도 승인 필요 |
| Release notes | DONE | `docs/11_releases/v1.0.0-mvp-release.md` |
| Tag | PENDING | PR merge 후 annotated tag `v1.0.0` 생성 예정 |

## 릴리스 전 운영 확인 필요

- 운영 `.env`에는 실제 secret 값을 저장소 밖에서 주입한다.
- `AI_PROVIDER=openai` 전환 전 OpenAI key/model/비용 한도를 확인한다.
- Google Calendar/Gmail은 운영 OAuth consent, redirect URI, scope 검증 후 연결한다.
- SMTP 발송은 운영 도메인 인증과 발송 제한 정책 확인 후 활성화한다.
- 실제 배포 전 DB backup을 수행하고 restore 절차를 staging에서 리허설한다.
