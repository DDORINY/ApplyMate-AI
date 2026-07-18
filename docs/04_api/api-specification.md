# API 명세

Base URL:

```text
/api/v1
```

보호 API 인증:

```text
Authorization: Bearer {access_token}
```

공통 성공 응답:

```json
{
  "success": true,
  "data": {},
  "message": "요청이 정상적으로 처리되었습니다."
}
```

공통 오류 응답:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "요청 값을 확인해 주세요."
  }
}
```

## Health API

| Method | Endpoint | 설명 |
| --- | --- | --- |
| GET | `/health` | Backend, PostgreSQL, Redis 상태 확인 |

## 인증 API

| Method | Endpoint | 인증 | 설명 |
| --- | --- | --- | --- |
| POST | `/auth/signup` | 공개 | 이메일 회원가입 |
| POST | `/auth/login` | 공개 | 이메일 로그인 |
| POST | `/auth/refresh` | Refresh Cookie | Access Token 재발급 |
| POST | `/auth/logout` | Refresh Cookie | 로그아웃 |
| GET | `/auth/me` | Access Token | 현재 사용자 조회 |

## 소셜 로그인 API

지원 provider path 값은 `google`, `github`입니다.

| Method | Endpoint | 인증 | 설명 |
| --- | --- | --- | --- |
| GET | `/auth/oauth/providers` | 공개 | provider 활성화 상태 조회 |
| GET | `/auth/oauth/{provider}/authorize?redirect_path=/me` | 공개 | 로그인용 OAuth authorize URL 생성 |
| GET | `/auth/oauth/{provider}/callback` | provider redirect | provider callback 처리 후 프론트 callback으로 redirect |
| POST | `/auth/oauth/exchange` | 공개 | 1회용 OAuth login ticket을 서비스 access/refresh token으로 교환 |
| GET | `/auth/oauth/accounts` | Access Token | 연결된 소셜 계정 목록 조회 |
| GET | `/auth/oauth/{provider}/link/authorize?redirect_path=/settings/accounts` | Access Token | 계정 연결용 OAuth authorize URL 생성 |
| DELETE | `/auth/oauth/accounts/{provider}` | Access Token | 연결된 소셜 계정 해제 |

### Provider 목록 응답

```json
{
  "success": true,
  "data": {
    "providers": [
      { "provider": "GOOGLE", "enabled": true },
      { "provider": "GITHUB", "enabled": true }
    ]
  },
  "message": "OAuth provider list returned."
}
```

### OAuth 로그인 흐름

1. Frontend가 `GET /auth/oauth/google/authorize?redirect_path=/me`를 호출합니다.
2. Backend가 `oauth_states`에 state hash를 저장하고 provider authorize URL을 반환합니다.
3. Browser가 provider authorize URL로 이동합니다.
4. Provider가 `GET /auth/oauth/google/callback?code=...&state=...`로 redirect합니다.
5. Backend가 state를 검증하고 provider 사용자 정보를 조회합니다.
6. Backend가 서비스 사용자를 확인/생성하고 `oauth_login_tickets`에 1회용 ticket hash를 저장합니다.
7. Backend가 `/auth/callback?ticket=...&redirect_path=/me`로 redirect합니다.
8. Frontend가 `POST /auth/oauth/exchange`로 ticket을 교환합니다.
9. Backend가 access token을 본문에, refresh token을 HttpOnly Cookie에 발급합니다.

### Ticket 교환 요청

```json
{
  "ticket": "one-time-ticket"
}
```

### Ticket 교환 응답

```json
{
  "success": true,
  "data": {
    "access_token": "jwt",
    "token_type": "Bearer",
    "expires_in": 1800,
    "redirect_path": "/me",
    "provider": "GOOGLE",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "name": "User",
      "status": "ACTIVE",
      "email_verified": true,
      "last_login_at": "2026-07-18T12:00:00Z",
      "created_at": "2026-07-18T12:00:00Z"
    }
  },
  "message": "OAuth login completed."
}
```

## 커리어 프로필 API

모든 커리어 프로필 API는 인증이 필요하며, 현재 로그인한 사용자의 `user_id`로만 조회/수정합니다.

| Method | Endpoint | 설명 |
| --- | --- | --- |
| GET | `/profiles/me` | 내 커리어 프로필 조회 |
| POST | `/profiles` | 커리어 프로필 생성 |
| PATCH | `/profiles/me` | 커리어 프로필 수정 |
| GET | `/profiles/me/skills` | 내 기술 목록 조회 |
| POST | `/profiles/me/skills` | 기술 추가 |
| PATCH | `/profiles/me/skills/{userSkillId}` | 기술 숙련도 수정 |
| DELETE | `/profiles/me/skills/{userSkillId}` | 기술 삭제 |
| GET | `/profiles/me/experiences` | 경력 목록 조회 |
| POST | `/profiles/me/experiences` | 경력 생성 |
| GET | `/profiles/me/experiences/{experienceId}` | 경력 상세 조회 |
| PATCH | `/profiles/me/experiences/{experienceId}` | 경력 수정 |
| DELETE | `/profiles/me/experiences/{experienceId}` | 경력 삭제 |
| GET | `/profiles/me/projects` | 프로젝트 목록 조회 |
| POST | `/profiles/me/projects` | 프로젝트 생성 |
| GET | `/profiles/me/projects/{projectId}` | 프로젝트 상세 조회 |
| PATCH | `/profiles/me/projects/{projectId}` | 프로젝트 수정 |
| DELETE | `/profiles/me/projects/{projectId}` | 프로젝트 삭제 |
| GET | `/profiles/me/preferences` | 희망 조건 조회 |
| PUT | `/profiles/me/preferences` | 희망 조건 저장/전체 갱신 |
| PATCH | `/profiles/me/preferences` | 희망 조건 일부 수정 |
| GET | `/profiles/me/exclusions` | 지원 제외 조건 목록 조회 |
| POST | `/profiles/me/exclusions` | 지원 제외 조건 생성 |
| PATCH | `/profiles/me/exclusions/{conditionId}` | 지원 제외 조건 수정 |
| DELETE | `/profiles/me/exclusions/{conditionId}` | 지원 제외 조건 삭제 |
| GET | `/profiles/me/portfolio-links` | 포트폴리오 링크 목록 조회 |
| POST | `/profiles/me/portfolio-links` | 포트폴리오 링크 생성 |
| PATCH | `/profiles/me/portfolio-links/{linkId}` | 포트폴리오 링크 수정 |
| DELETE | `/profiles/me/portfolio-links/{linkId}` | 포트폴리오 링크 삭제 |
