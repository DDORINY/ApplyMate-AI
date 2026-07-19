# Master Completion Plan

## 현재 위치

- 완료: `v0.4.1` 일정 관리
- 다음: `v0.4.2` 대시보드
- 최신 DB head: `20260719_2000`

## 완료된 큰 흐름

1. 계정과 인증 기반 구축
2. 커리어 프로필과 이력서 데이터 기반 구축
3. 채용공고 저장과 AI 분석
4. 사용자-공고 적합도 분석
5. 이력서 텍스트 추출과 AI 구조화 분석
6. 근거 기반 지원 문서 생성
7. 지원 현황 관리
8. 지원 일정 관리

## 남은 큰 흐름

1. 대시보드에서 지원/일정/AI 작업을 요약한다.
2. Google Calendar와 Gmail 같은 외부 서비스 연동을 사용자 명시 승인 기반으로 추가한다.
3. 일일 맞춤 채용공고 추천을 구현한다.
4. 브라우저 E2E, 운영 배포 문서, 보안 검증을 강화한다.
5. v1.0.0 MVP 릴리스를 완료한다.

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
