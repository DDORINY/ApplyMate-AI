# Gmail Integration Guide

## 환경변수

```text
GMAIL_PROVIDER=mock
GOOGLE_GMAIL_CLIENT_ID=
GOOGLE_GMAIL_CLIENT_SECRET=
GOOGLE_GMAIL_REDIRECT_URI=http://localhost:8000/api/v1/integrations/gmail/callback
GOOGLE_GMAIL_SCOPES=openid,email,profile,https://www.googleapis.com/auth/gmail.readonly
GMAIL_DEFAULT_LOOKBACK_DAYS=30
GMAIL_MAX_MESSAGES_PER_SYNC=50
EXTERNAL_TOKEN_ENCRYPTION_KEY=
```

## 로컬 검증

Mock Provider 기준:

1. 회원가입/로그인
2. `/settings/integrations`에서 Gmail 연결
3. Gmail 동기화 실행
4. `/inbox-candidates`에서 후보 확인
5. 후보 승인 또는 거절

## 운영 전 확인

- Google Cloud OAuth consent screen
- redirect URI 등록
- scope 승인
- 실제 Gmail API token exchange
- 실제 message search/fetch

실제 Gmail API는 v0.5.1에서 `NEEDS_VERIFICATION`이다.
