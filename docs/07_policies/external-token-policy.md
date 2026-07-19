# External Token Policy

## 저장 원칙

- 외부 access token과 refresh token은 평문 저장하지 않는다.
- token 원문은 API 응답, 로그, 문서, 테스트 출력에 노출하지 않는다.
- provider raw response는 저장하지 않는다.
- token 저장 컬럼은 `*_encrypted` 이름을 사용한다.

## v0.5.0 구현

- `EXTERNAL_TOKEN_ENCRYPTION_KEY`를 사용해 application-level encryption을 수행한다.
- `EXTERNAL_TOKEN_ENCRYPTION_KEY_VERSION`으로 key version을 기록한다.
- key가 없으면 실제 provider token 저장을 차단한다.
- mock provider 검증에서도 token 평문이 API 응답에 나오지 않아야 한다.

## 연결 해제

- 연결 해제 시 provider revoke를 시도한다.
- revoke 실패가 발생해도 로컬 connection은 비활성화할 수 있다.
- 내부 일정은 삭제하지 않는다.
- 외부 Calendar 일정도 자동 hard delete하지 않는다.

## 운영 전 확인

- 운영 key entropy
- key rotation 절차
- backup/restore 시 token 복호화 가능성
- log redaction
- incident 대응 절차
