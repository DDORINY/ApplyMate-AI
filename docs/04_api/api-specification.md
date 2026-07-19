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
| POST | `/auth/email-verification/send` | Access Token | 이메일 인증 메일 발송/재발송 |
| POST | `/auth/email-verification/verify` | 공개 | 이메일 인증 token 검증 |
| POST | `/auth/password/forgot` | 공개 | 비밀번호 재설정 안내 요청 |
| POST | `/auth/password/reset` | 공개 | 비밀번호 재설정 |
| POST | `/auth/password/change` | Access Token | 현재 비밀번호 기반 비밀번호 변경 |
| POST | `/auth/password/set` | Access Token | 비밀번호 없는 소셜 계정의 비밀번호 설정 |
| GET | `/auth/sessions` | Access Token | 로그인 세션 목록 |
| DELETE | `/auth/sessions/{sessionId}` | Access Token | 개별 세션 로그아웃 |
| DELETE | `/auth/sessions/others` | Access Token | 현재 세션을 제외한 모든 세션 로그아웃 |
| DELETE | `/auth/sessions` | Access Token | 전체 세션 로그아웃 |
| GET | `/auth/security-events` | Access Token | 최근 계정 보안 이벤트 목록 조회 |

### 이메일 인증 요청

```json
{
  "success": true,
  "data": {
    "sent": true,
    "email": "user@example.com"
  },
  "message": "이메일 인증 안내를 발송했습니다."
}
```

### 비밀번호 찾기 요청

요청 이메일의 가입 여부와 관계없이 동일한 성공 응답을 반환합니다.

```json
{
  "email": "user@example.com"
}
```

### 세션 목록 응답

```json
{
  "success": true,
  "data": {
    "sessions": [
      {
        "session_id": "session-id",
        "device_name": "Chrome on Windows",
        "created_at": "2026-07-19T10:00:00Z",
        "last_used_at": "2026-07-19T10:10:00Z",
        "expires_at": "2026-08-02T10:00:00Z",
        "is_current": true
      }
    ]
  },
  "message": "세션 목록입니다."
}
```

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
# v0.2.0 채용공고 API

Base URL: `/api/v1`

모든 채용공고 API는 `Authorization: Bearer {accessToken}` 헤더가 필요하다.

## POST /jobs

채용공고를 직접 등록한다.

요청:

```json
{
  "company_name": "ApplyMate Labs",
  "company_website_url": "https://example.com",
  "company_size": "STARTUP",
  "title": "Backend Engineer",
  "position": "Backend",
  "employment_type": "FULL_TIME",
  "career_requirement": "3년 이상",
  "education_requirement": "학력 무관",
  "location": "Seoul",
  "work_type": "HYBRID",
  "salary_min": 50000000,
  "salary_max": 80000000,
  "description": "FastAPI 기반 서비스 개발",
  "requirements": "Python, SQLAlchemy",
  "preferred_qualifications": "Docker 운영 경험",
  "benefits": "자율 출퇴근",
  "recruitment_process": "서류-기술면접-최종면접",
  "deadline_at": "2026-08-31T14:59:00Z",
  "deadline_type": "FIXED",
  "status": "SAVED",
  "is_favorite": true,
  "source_type": "MANUAL",
  "source_url": null,
  "notes": "우선 검토"
}
```

응답: `201 Created`

```json
{
  "success": true,
  "data": {
    "id": 1,
    "company": {
      "id": 1,
      "name": "ApplyMate Labs",
      "normalized_name": "applymate labs",
      "website_url": "https://example.com",
      "industry": null,
      "company_size": "STARTUP",
      "description": null,
      "created_at": "2026-07-19T00:00:00Z",
      "updated_at": "2026-07-19T00:00:00Z"
    },
    "title": "Backend Engineer",
    "status": "SAVED",
    "is_favorite": true
  },
  "message": "채용공고가 등록되었습니다."
}
```

## POST /jobs/import-url

URL에서 제한적으로 HTML 정보를 추출해 채용공고를 등록한다.

요청:

```json
{
  "url": "https://example.com/jobs/123",
  "company_name": "ApplyMate Labs",
  "title": "Backend Engineer",
  "description": "사용자 확인 본문"
}
```

응답: `201 Created`

```json
{
  "success": true,
  "data": {
    "job": {
      "id": 1,
      "title": "Backend Engineer",
      "source_type": "URL",
      "source_url": "https://example.com/jobs/123"
    },
    "import_status": "PARTIAL",
    "extracted_fields": ["title", "description", "body"],
    "warnings": ["기업명은 URL 또는 사용자 입력으로 보완이 필요할 수 있습니다."]
  },
  "message": "URL 채용공고가 등록되었습니다."
}
```

## GET /jobs

채용공고 목록을 조회한다.

Query:

| 이름 | 설명 |
| --- | --- |
| `page` | 1부터 시작하는 페이지 번호 |
| `size` | 페이지 크기, 최대 100 |
| `query` | 제목, 기업명, 직무, 지역, 메모 검색 |
| `status` | `SAVED`, `REVIEWING`, `INTERESTED`, `EXCLUDED`, `CLOSED` |
| `employment_type` | 고용 형태 |
| `work_type` | 근무 형태 |
| `is_favorite` | 관심 공고 여부 |
| `source_type` | `MANUAL`, `URL` |
| `sort` | `created_at`, `updated_at`, `deadline_at`, `title` |
| `order` | `asc`, `desc` |

## GET /jobs/{jobId}

채용공고 상세를 조회한다. 본인 소유가 아니면 `JOB_POSTING_NOT_FOUND`를 반환한다.

## PATCH /jobs/{jobId}

채용공고를 수정한다. 요청 body는 `POST /jobs`의 일부 필드를 사용할 수 있다.

## DELETE /jobs/{jobId}

채용공고를 삭제한다.
