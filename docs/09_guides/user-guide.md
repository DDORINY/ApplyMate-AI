# ApplyMate AI 사용자 가이드

## 1. 회원가입과 로그인

- `/signup`에서 계정을 만든다.
- `/login`에서 로그인한다.
- 이메일 인증과 비밀번호 재설정은 계정 보안 화면과 이메일 링크를 기준으로 진행한다.

## 2. 프로필 작성

- `/profile`에서 희망 직무, 기술, 경력, 프로젝트, 포트폴리오를 입력한다.
- 추천과 적합도 분석은 프로필 정보가 많을수록 설명력이 높아진다.

## 3. 채용공고

- `/jobs`에서 저장한 공고를 확인한다.
- `/jobs/new`에서 URL 또는 직접 입력으로 공고를 등록한다.
- 공고 상세에서 AI 분석과 사용자-공고 적합도 분석을 실행한다.

## 4. 이력서

- `/resumes`에서 이력서를 관리한다.
- PDF/DOCX만 업로드할 수 있다.
- 업로드 후 텍스트 추출과 구조화 분석을 실행한다.

## 5. 지원 문서

- `/documents`에서 지원 문서를 생성하고 관리한다.
- `/documents/{documentId}/improve`에서 개선 요청을 실행한다.
- `/documents/{documentId}/improvements/{runId}`에서 제안을 확인하고 승인하면 새 버전이 생성된다.

## 6. 지원 현황

- `/applications`에서 지원 항목을 만들고 상태를 관리한다.
- 제출 문서 버전을 고정해 나중에 어떤 문서로 지원했는지 추적한다.

## 7. 일정

- `/calendar`에서 마감일, 면접, 과제, 개인 일정을 관리한다.
- 일정 리마인더는 worker 실행 시 in-app 알림으로 생성된다.

## 8. 추천

- `/recommendations`에서 저장된 공고 기반 규칙 추천을 확인한다.
- `/recommendations/history`에서 추천 실행 이력을 확인한다.
- `/settings/recommendations`에서 추천 설정을 변경한다.

## 9. 알림

- `/notifications`에서 in-app 알림을 확인한다.
- `/settings/notifications`에서 이벤트별 알림 설정을 변경한다.

## 10. 외부 연동

- `/settings/integrations`에서 Calendar/Gmail 연결 상태를 확인한다.
- 실제 provider가 연결되지 않은 환경에서는 mock/disabled/verification 필요 상태를 구분한다.

## 11. 계정 보안

- `/settings/security`에서 비밀번호, 세션, 보안 이벤트를 관리한다.
