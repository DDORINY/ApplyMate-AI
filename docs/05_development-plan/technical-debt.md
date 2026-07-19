# 기술 부채

| ID | 영역 | 내용 | 근거 | 영향 | 우선순위 | 해결 목표 버전 |
| --- | --- | --- | --- | --- | --- | --- |
| TD-001 | Frontend Test | 컴포넌트/E2E 자동 테스트 부족 | 현재 검증은 lint/type-check/build 중심 | UI 회귀 발견 지연 | High | v0.3.x |
| TD-002 | CI/CD | GitHub Actions 미구성 | 로컬 검증에 의존 | PR 품질 자동 보장 부족 | High | v0.3.x |
| TD-003 | External Verification | OpenAI/OAuth/SMTP 실제 운영 검증 부족 | env secret 필요 | 운영 전 리스크 | High | v0.3.x~v0.4.x |
| TD-004 | Async Jobs | AI 분석이 동기 요청 중심 | v0.2.1/v0.2.2 서비스 흐름 | 장시간/대량 작업에 취약 | Medium | v0.5.x |
| TD-005 | Monitoring | 구조화 로그/metric/alert 부재 | 운영 infra 미구현 | 장애 추적 어려움 | Medium | v0.5.x |
| TD-006 | Backup | DB backup/restore 절차 문서 부족 | 운영 DB 없음 | 운영 안정성 부족 | Medium | v0.4.x |
| TD-007 | File Storage | 이력서 업로드 저장 구조 미정 | v0.3.x 예정 | 파일 기능 착수 전 설계 필요 | High | v0.3.0 |
| TD-008 | Encoding Hygiene | 일부 기존 문서/문자열 인코딩 깨짐 흔적 | 콘솔 출력과 기존 문서에 mojibake 존재 | 문서 가독성 저하 | Medium | v0.3.x |
