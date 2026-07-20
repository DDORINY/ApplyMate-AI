# Known Limitations

## v1.0.0 기준

| 항목 | 상태 | 설명 |
| --- | --- | --- |
| 실제 OpenAI 호출 | NEEDS_VERIFICATION | `AI_PROVIDER=mock/disabled` 기준으로 검증됨. 운영 key/model과 비용 검증 필요 |
| 실제 Gmail API | NEEDS_VERIFICATION | mock 기반 검증. 운영 OAuth consent와 Gmail API 검증 필요 |
| 실제 Google Calendar API | NEEDS_VERIFICATION | mock 기반 검증. 운영 OAuth consent와 Calendar API 검증 필요 |
| 실제 SMTP 발송 | NEEDS_VERIFICATION | mock/development provider 검증. 실제 발송은 별도 도메인/계정 검증 필요 |
| Push 알림 | NOT_IMPLEMENTED | 설정 구조만 존재하며 실발송 provider 없음 |
| 분산 Worker | NOT_IMPLEMENTED | one-shot worker 구조. 분산 lock과 scheduler는 후속 |
| 분산 Rate Limit | NOT_IMPLEMENTED | 현재 in-memory rate limit. 다중 backend instance에서는 Redis 기반 필요 |
| 운영 배포 | NEEDS_VERIFICATION | Docker/문서/스모크 도구는 준비됐지만 실제 운영 배포는 별도 |
| 운영 DB 복구 리허설 | NEEDS_VERIFICATION | 절차 문서화 완료, 실제 리허설은 별도 |
| npm moderate advisories | ACCEPTED_RISK | Next 내부 PostCSS advisory. 자동 fix가 major downgrade 제안 |
