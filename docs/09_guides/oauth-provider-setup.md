# OAuth Provider 설정 가이드

이 문서는 로컬 개발 환경에서 Google/GitHub OAuth 로그인을 테스트하기 위한 설정 가이드입니다. 실제 Client Secret은 저장소에 커밋하지 않습니다.

## 공통 로컬 URL

Frontend:

```text
http://localhost:3000
```

Backend:

```text
http://localhost:8000
```

Frontend callback:

```text
http://localhost:3000/auth/callback
```

## Google OAuth

Google Cloud Console에서 OAuth Client를 만들고 다음 redirect URI를 등록합니다.

```text
http://localhost:8000/api/v1/auth/oauth/google/callback
```

`.env` 설정:

```env
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/oauth/google/callback
```

요청 scope:

```text
openid email profile
```

## GitHub OAuth

GitHub Developer settings에서 OAuth App을 만들고 다음 callback URL을 등록합니다.

```text
http://localhost:8000/api/v1/auth/oauth/github/callback
```

`.env` 설정:

```env
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
GITHUB_REDIRECT_URI=http://localhost:8000/api/v1/auth/oauth/github/callback
```

요청 scope:

```text
read:user user:email
```

## 서비스 설정

```env
OAUTH_FRONTEND_CALLBACK_URL=http://localhost:3000/auth/callback
OAUTH_ALLOWED_REDIRECT_PATHS=/me,/profile,/settings/accounts
OAUTH_STATE_EXPIRE_SECONDS=300
OAUTH_TICKET_EXPIRE_SECONDS=60
```

## 확인 순서

1. `.env`에 provider client 값을 입력합니다.
2. `docker compose up --build`를 실행합니다.
3. `http://localhost:3000/login` 또는 `/signup`으로 이동합니다.
4. Google/GitHub 버튼을 클릭합니다.
5. provider 인증 완료 후 `/auth/callback`을 거쳐 `/me`로 이동하는지 확인합니다.
6. `/settings/accounts`에서 연결된 provider를 확인합니다.
