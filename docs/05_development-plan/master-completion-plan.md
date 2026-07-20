# Master Completion Plan

## 현재 위치

- 완료: `v0.7.0` AI 지원 문서 개선 루프
- 다음: `v0.8.0` 알림/리마인더 운영화
- 최신 DB head: `20260720_0100`

## 완료된 큰 흐름

1. 계정과 인증 기반 구축
2. 커리어 프로필과 이력서 데이터 기반 구축
3. 채용공고 저장과 AI 분석
4. 사용자-공고 적합도 분석
5. 이력서 텍스트 추출과 AI 구조화 분석
6. 근거 기반 지원 문서 생성
7. 지원 현황 관리
8. 지원 일정 관리
9. 대시보드
10. Google Calendar 연동 기반
11. Gmail 채용 메일 분석 기반
12. 규칙 기반 채용공고 추천
13. 추천 실행 설정, Snapshot, 변화 판정, 알림 후보 기반
14. AI 지원 문서 개선 루프

## 남은 큰 흐름

1. 알림/리마인더 운영화를 구현한다.
2. 브라우저 E2E, 운영 배포 문서, 보안 검증을 강화한다.
3. v1.0.0 MVP 릴리스를 완료한다.

## v0.4.2 방향

- 지원 현황 통계
- 오늘/이번 주 일정
- 임박 마감 채용공고
- 준비 중인 지원 항목
- 최근 AI 분석, 적합도 분석, 지원 문서
- 최근 활동 로그
# v0.4.2 Completion Update

- 대시보드 API와 `/dashboard` 화면을 v0.4.2 범위로 완료한다.
- v0.4.2는 신규 DB migration 없이 기존 지원/일정/공고/AI/문서 데이터를 읽기 전용으로 집계한다.
- v0.4.2 완료 후 다음 개발 브랜치는 `feature/v0.5.0-google-calendar`이다.
- v0.5.0은 Google Calendar OAuth 계정 연결과 내부 일정 동기화 기반을 목표로 한다.

# v0.5.0 Completion Update

- Google Calendar 전용 OAuth state와 token 저장 구조를 추가한다.
- 로그인 OAuth와 Calendar OAuth를 분리한다.
- mock provider 기준 Calendar 목록, Calendar 선택, 내부 일정 동기화, mapping/run/error 기록, 연결 해제를 완료한다.
- 실제 Google Calendar API 호출은 운영 credentials 준비 후 `NEEDS_VERIFICATION`으로 남긴다.
- v0.5.0 완료 후 다음 개발 브랜치는 `feature/v0.5.1-gmail-analysis`이다.

# v0.5.1 Completion Update

- Gmail OAuth, 읽기 전용 scope, mock Gmail Provider, 메일 후보 생성, 사용자 승인 기반 지원 상태/일정 반영을 구현한다.
- 실제 Gmail API token exchange/search/fetch와 실제 OpenAI 메일 분석은 `NEEDS_VERIFICATION`으로 남긴다.
- v0.5.1 완료 후 다음 개발 브랜치는 `feature/v0.6.0-job-recommendations`이다.

# v0.6.0 Completion Update

- 저장된 채용공고만 후보로 사용하는 `RULE_BASED` 추천 생성/조회/상세/피드백 API를 구현한다.
- 추천 점수, 등급, 추천 이유, 부족 조건, 필수 조건 불일치, 정책 버전, 입력 snapshot/hash를 저장한다.
- `/recommendations`, `/recommendations/{recommendationId}`, 대시보드 추천 카드, 공고 상세 추천 CTA를 구현한다.
- AI/ML 호출, 외부 크롤링, 자동 지원 제출은 제외한다.
- v0.6.0 완료 후 다음 개발 브랜치는 `feature/v0.6.1-recommendation-automation`이다.

# v0.6.1 Completion Update

- 추천 실행 설정, `run-if-due`, Snapshot, 추천 변화 판정, 추천 알림 후보 저장 기반을 구현한다.
- `/recommendations` UX를 새 추천/점수 변화/피드백 필터 중심으로 개선한다.
- `/recommendations/history`와 `/settings/recommendations` 화면을 추가한다.
- 실제 Background Worker 운영, 외부 공고 수집, 이메일·푸시 발송, 자동 지원은 제외한다.
- v0.6.1 완료 후 다음 개발 브랜치는 `feature/v0.7.0-document-improvement`이다.

# v0.7.0 Completion Update

- 기존 지원 문서 버전을 기준으로 AI 개선 실행을 생성한다.
- 문장별 원문/개선안/근거/위험도/선택 상태를 저장한다.
- 승인 전에는 기존 문서를 변경하지 않고, 적용 시 새 버전을 생성한다.
- 기준 문서보다 최신 버전이 있으면 적용을 차단한다.
- `/documents/{documentId}/improve`와 `/documents/{documentId}/improvements/{runId}` 화면을 추가한다.
- 실제 OpenAI 개선 호출은 `NEEDS_VERIFICATION`으로 남긴다.
- v0.7.0 완료 후 다음 개발 브랜치는 `feature/v0.8.0-notification-operations`이다.
