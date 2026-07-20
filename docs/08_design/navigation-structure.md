# Navigation Structure

## Main navigation

- `/`
- `/dashboard`
- `/profile`
- `/jobs`
- `/recommendations`
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
- `/settings/security`

## v0.5.1 Gmail screens

- `/settings/integrations`: Gmail connection, search settings, sync, recent runs
- `/inbox-candidates`: email candidate list, evidence, approve/reject

## v0.6.0 Recommendation screens

- `/recommendations`: 저장된 채용공고 기반 규칙 추천 목록, 등급/키워드 필터, 추천 생성, 피드백
- `/recommendations/{recommendationId}`: 추천 점수 상세, 추천 이유, 부족 조건, 입력 snapshot, 재계산
- `/dashboard`: 상위 추천 공고 카드와 추천 목록 진입 CTA
- `/jobs/{jobId}`: 추천 점수 확인 화면으로 이동하는 CTA

## Rule

로그인, 회원가입, 내 계정, 계정 연결, 외부 연동, 보안 메뉴는 계정 네비게이션 영역에 배치한다.
공고 추천은 주요 서비스 기능이므로 왼쪽/메인 네비게이션에 배치한다.
