# External Token Policy

## Storage

- 외부 access token과 refresh token은 평문 저장하지 않는다.
- token 컬럼은 `*_encrypted` 이름을 사용한다.
- API 응답, 로그, 테스트 출력에 token 값을 노출하지 않는다.
- provider raw response를 그대로 저장하지 않는다.

## Encryption

- `EXTERNAL_TOKEN_ENCRYPTION_KEY`를 사용한다.
- `EXTERNAL_TOKEN_ENCRYPTION_KEY_VERSION`으로 key version을 기록한다.
- key가 없으면 실제 provider token 저장을 차단한다.

## Gmail v0.5.1

Gmail access token, refresh token, future history id는 평문 저장하지 않는다.

## Disconnect

연결 해제 시 provider revoke를 시도한다. revoke 실패가 발생해도 로컬 connection과 external account는 비활성화한다.

## Operations checklist

- 운영 key entropy
- key rotation 절차
- backup/restore 후 token 복호화 가능성
- log redaction
- incident 대응 절차
