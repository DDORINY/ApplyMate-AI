# Navigation Structure

## Main navigation

- `/`
- `/dashboard`
- `/profile`
- `/jobs`
- `/recommendations`
- `/recommendations/history`
- `/resumes`
- `/documents`
- `/applications`
- `/calendar`
- `/inbox-candidates`

## Account navigation

- `/login`
- `/signup`
- `/me`
- `/settings/accounts`
- `/settings/integrations`
- `/settings/recommendations`
- `/settings/security`

## v0.5.1 Gmail screens

- `/settings/integrations`: Gmail connection, search settings, sync, recent runs
- `/inbox-candidates`: email candidate list, evidence, approve/reject

## v0.6.0 Recommendation screens

- `/recommendations`: 저장된 채용공고 기반 규칙 추천 목록, 등급/키워드 필터, 추천 생성, 피드백
- `/recommendations/{recommendationId}`: 추천 점수 상세, 추천 이유, 부족 조건, 입력 snapshot, 재계산
- `/dashboard`: 상위 추천 공고 카드와 추천 목록 진입 CTA
- `/jobs/{jobId}`: 추천 점수 확인 화면으로 이동하는 CTA

## v0.6.1 Recommendation automation screens

- `/recommendations`: 신규/점수 변화/피드백/최소 점수 필터, 추천 변화 배지, 알림 후보 카드
- `/recommendations/history`: 추천 실행 Snapshot과 신규/변경 추천 이력
- `/settings/recommendations`: 추천 실행 설정, 빈도, 기준 시간, 제외 정책, 알림 후보 설정
- `/dashboard`: 최신 Snapshot의 마지막 실행, 신규 추천, 변경 추천 요약

## v0.7.0 Document improvement screens

- `/documents/{documentId}`: 지원 문서 상세, AI 문서 개선 CTA, 개선 이력 카드
- `/documents/{documentId}/improve`: 개선 유형, 추가 요청, 목표 톤/길이 입력 후 AI 개선 실행 생성
- `/documents/{documentId}/improvements/{runId}`: before/after 비교, 문장별 승인/제외, 새 버전 적용, 재시도/거절

## Rule

로그인, 회원가입, 내 계정, 계정 연결, 외부 연동, 보안 메뉴는 계정 네비게이션 영역에 배치한다.
공고 추천은 주요 서비스 기능이므로 왼쪽/메인 네비게이션에 배치한다.
추천 실행 설정은 계정/환경 설정 성격이므로 계정 관리 영역에 배치한다.
지원 문서 개선은 문서 상세의 하위 작업이므로 별도 메인 네비게이션 항목을 만들지 않고 `/documents` 흐름 안에 둔다.
