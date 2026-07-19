# 미검증 항목

| 항목 | 코드 상태 | 미검증 사유 | 필요한 설정 | 검증 방법 | 완료 기준 |
| --- | --- | --- | --- | --- | --- |
| 실제 OpenAI API 호출 | Provider 구현 있음 | API key/model이 필요하고 비용 발생 가능 | `AI_PROVIDER=openai`, `OPENAI_API_KEY`, `OPENAI_MODEL` | 실제 공고 분석 API 호출 | 구조화 응답 저장과 오류 처리 확인 |
| 실제 Google OAuth 로그인 | 코드 구현 있음 | provider app credential 필요 | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, redirect URI | 브라우저 OAuth 로그인 | callback→ticket exchange→로그인 완료 |
| 실제 GitHub OAuth 로그인 | 코드 구현 있음 | provider app credential 필요 | `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, redirect URI | 브라우저 OAuth 로그인 | callback→ticket exchange→로그인 완료 |
| 운영 SMTP 발송 | SMTP adapter 있음 | 실제 SMTP 계정/도메인 필요 | SMTP 환경변수 | 인증/비밀번호 메일 발송 | 수신함 도착과 링크 검증 |
| 운영 HTTPS Cookie | 설정 항목 있음 | HTTPS 도메인 필요 | `COOKIE_SECURE=true`, HTTPS proxy | refresh/login/logout | secure cookie 정상 동작 |
| 운영 배포 | Docker 기반 있음 | 서버/도메인/Nginx/GitHub Actions 필요 | 운영 infra | staging 배포 | health/API/frontend 정상 |
| 부하 테스트 | 없음 | 부하 도구/시나리오 미정 | 테스트 환경 | API load test | 병목/오류율 기준 충족 |
| 장기 실행 테스트 | 없음 | 장시간 세션/토큰/DB 검증 필요 | 테스트 계정 | 장기 soak test | 메모리/DB connection 안정 |
| 브라우저 E2E 테스트 | 없음 | Playwright/Cypress 미도입 | 테스트 러너 | signup→profile→job→analysis→match | 주요 흐름 자동 통과 |
| 다양한 실제 채용사이트 URL 추출 | 제한 구현 있음 | 사이트별 HTML 구조 다양 | 테스트 URL 목록 | URL import smoke | 주요 사이트별 성공/경고 기준 정리 |
