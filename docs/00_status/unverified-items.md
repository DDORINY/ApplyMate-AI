# Unverified Items

## 운영 환경 검증 필요

| 항목 | 상태 | 이유 |
| --- | --- | --- |
| 실제 OpenAI 호출 | NEEDS_VERIFICATION | 운영 API key/model 설정과 비용 확인 필요 |
| 운영 Google/GitHub OAuth | NEEDS_VERIFICATION | 운영 client/secret/redirect URI 필요 |
| 운영 SMTP | NEEDS_VERIFICATION | 실제 메일 발송 계정과 도메인 검증 필요 |
| HTTPS Cookie/SameSite | NEEDS_VERIFICATION | 운영 도메인과 HTTPS 환경에서 검증 필요 |
| 운영 배포 | NEEDS_VERIFICATION | 서버/도메인/DB/Redis 환경 필요 |
| 브라우저 E2E 자동화 | PLANNED | v0.9.0 안정화 단계에서 강화 예정 |

## v0.4.2 제외 또는 후속 범위

| 항목 | 상태 | 후속 버전 |
| --- | --- | --- |
| 대시보드 위젯 사용자 커스터마이징 | DEFERRED | 미정 |
| 대시보드 차트 라이브러리 기반 고급 시각화 | DEFERRED | 미정 |
| 이메일/푸시 알림 실제 발송 | PLANNED | 미정 |
| 백그라운드 알림 워커 | PLANNED | 미정 |
| Google Calendar 실제 일정 생성/동기화 | PLANNED | v0.5.0 |
| Gmail 일정 자동 추출 | PLANNED | v0.5.1 |
| 반복 일정 | DEFERRED | 미정 |
| 일정 생성에 따른 지원 상태 자동 변경 | DEFERRED | 사용자 승인 흐름 설계 후 |
