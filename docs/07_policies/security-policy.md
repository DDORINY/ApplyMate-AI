# Security Policy

## 공통 원칙

- Secret, token, password, OAuth code는 응답과 로그에 노출하지 않는다.
- 사용자 소유 resource는 `user_id`로 소유권을 검증한다.
- 운영 CORS는 wildcard를 사용하지 않는다.
- 운영 환경에서는 HTTPS와 secure cookie를 사용한다.

## v0.9.0 보안 헤더

- `Content-Security-Policy`
- `X-Content-Type-Options`
- `Referrer-Policy`
- `Permissions-Policy`
- `X-Frame-Options`
- HTTPS 운영 환경의 `Strict-Transport-Security`

## Rate Limit

다음 API는 우선 rate limit 대상이다.

- 회원가입
- 로그인
- refresh
- 비밀번호 재설정/이메일 재발송 후보
- 추천 생성
- 알림 worker 수동 실행

분산 환경에서는 Redis 기반 rate limit으로 확장한다.

## 파일 업로드

PDF/DOCX만 허용한다. 확장자, MIME, signature, DOCX 구조, 파일명, 크기 제한, 중복 hash를 검증한다.

## OAuth

OAuth state는 만료와 1회 사용을 적용한다. redirect path는 allowlist로 제한한다. Provider token은 암호화 저장하고 응답에 포함하지 않는다.
