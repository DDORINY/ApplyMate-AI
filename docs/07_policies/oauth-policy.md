# OAuth Policy

## 분리 원칙

- 로그인 OAuth와 외부 서비스 연동 OAuth는 목적과 저장소를 분리한다.
- 로그인 OAuth는 인증과 기본 프로필 식별에만 사용한다.
- Calendar OAuth는 Calendar 목록 조회와 일정 동기화 권한에만 사용한다.
- 기존 로그인 OAuth access token을 Calendar API 용도로 재사용하지 않는다.

## State 정책

- OAuth state 원문은 저장하지 않고 hash만 저장한다.
- state는 만료 시간을 가진다.
- state는 1회만 사용할 수 있다.
- provider, user, redirect path를 state에 연결해 CSRF와 open redirect를 방어한다.

## Redirect 정책

- 내부 path만 허용한다.
- 외부 URL, protocol-relative URL, backslash 포함 path는 허용하지 않는다.

## 사용자 승인

사용자의 명시적 승인 없이 다음 작업을 수행하지 않는다.

- 외부 Calendar 일정 생성
- 외부 Calendar 일정 수정
- 외부 Calendar 일정 삭제
- 내부 일정 자동 생성
- 내부 지원 상태 자동 변경
