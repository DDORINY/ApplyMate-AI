# 이메일 서비스 설정 가이드

v0.1.4에서는 이메일 인증과 비밀번호 복구 안내를 발송하기 위한 이메일 Adapter를 제공합니다.

## 개발 환경

기본값은 이메일 provider 비활성입니다.

```env
EMAIL_PROVIDER=disabled
```

테스트에서는 fake sender를 사용해 실제 SMTP 서버를 호출하지 않습니다.

## SMTP 환경변수

```env
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your-username
SMTP_PASSWORD=your-password
SMTP_USE_TLS=true
EMAIL_FROM_ADDRESS=no-reply@example.com
EMAIL_FROM_NAME=ApplyMate AI
FRONTEND_EMAIL_VERIFY_URL=http://localhost:3000/verify-email
FRONTEND_PASSWORD_RESET_URL=http://localhost:3000/reset-password
```

실제 SMTP 비밀번호와 secret은 저장소에 커밋하지 않습니다.

## 보안 주의사항

- 인증/재설정 token 원문은 일반 로그에 출력하지 않습니다.
- 운영 환경에서는 HTTPS와 `COOKIE_SECURE=true`가 필요합니다.
- SMTP provider 장애가 사용자 데이터 변경 실패로 이어지지 않도록 오류 처리를 분리합니다.
