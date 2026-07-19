# OAuth Policy

## Purpose separation

OAuth 목적은 분리한다.

- `LOGIN`: 로그인과 계정 연결
- `CALENDAR`: Google Calendar 일정 동기화
- `GMAIL`: Gmail 채용 메일 분석

로그인 OAuth token을 Calendar 또는 Gmail API 호출에 재사용하지 않는다.

## State policy

- OAuth state 원문은 저장하지 않고 hash만 저장한다.
- state는 만료 시간을 가진다.
- state는 1회만 사용할 수 있다.
- redirect path는 내부 path만 허용한다.

## Gmail OAuth

- Gmail 연결은 사용자의 명시적 동의가 있어야 한다.
- v0.5.1은 읽기 전용 `gmail.readonly` scope만 사용한다.
- 로그인 또는 Calendar 연결이 Gmail 연결을 자동으로 활성화하면 안 된다.
- Gmail 연결 해제 시 provider token은 비활성화하지만 내부 후보 데이터는 자동 삭제하지 않는다.

## User approval

외부 OAuth 연결만으로 다음 작업을 자동 수행하지 않는다.

- 외부 Calendar 일정 생성/수정/삭제
- Gmail 메일 수정/삭제/발송
- 내부 지원 상태 변경
- 내부 일정 생성
