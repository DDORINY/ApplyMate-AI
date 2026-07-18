# ApplyMate AI API 명세서

## 1. 기본 정보

### Base URL

```text
/api/v1
```

### 인증 방식

```text
Authorization: Bearer {access_token}
```

### 공통 응답 구조

```json
{
  "success": true,
  "data": {},
  "message": "요청이 정상적으로 처리되었습니다."
}
```

### 공통 오류 응답

```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "요청한 데이터를 찾을 수 없습니다."
  }
}
```

## 2. Health API

| Method | Endpoint  | 설명 |
| ------ | --------- | ---- |
| GET    | `/health` | Backend, PostgreSQL, Redis 상태 확인 |

응답 예시:

```json
{
  "success": true,
  "data": {
    "status": "UP",
    "database": "UP",
    "redis": "UP"
  },
  "message": "서비스가 정상적으로 실행 중입니다."
}
```

## 3. 인증 API

| Method | Endpoint        | 설명               |
| ------ | --------------- | ---------------- |
| POST   | `/auth/signup`  | 회원가입             |
| POST   | `/auth/login`   | 로그인              |
| POST   | `/auth/refresh` | Access Token 재발급 |
| POST   | `/auth/logout`  | 로그아웃             |
| GET    | `/auth/me`      | 로그인 사용자 조회       |

### 인증 정책

```text
Access Token: Authorization: Bearer {access_token}
Refresh Token: applymate_refresh_token HttpOnly Cookie
Access Token 만료: 30분
Refresh Token 만료: 14일
Refresh Token 저장: 원문 저장 금지, SHA-256 해시만 DB 저장
Refresh Token 재발급 정책: rotation 적용, 기존 토큰 폐기
```

### POST /auth/signup

요청:

```json
{
  "name": "도하",
  "email": "doha@example.com",
  "password": "password123"
}
```

응답:

```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "doha@example.com",
    "name": "도하",
    "status": "ACTIVE",
    "last_login_at": null,
    "created_at": "2026-07-18T06:00:00Z"
  },
  "message": "회원가입이 완료되었습니다."
}
```

### POST /auth/login

요청:

```json
{
  "email": "doha@example.com",
  "password": "password123"
}
```

응답 본문:

```json
{
  "success": true,
  "data": {
    "access_token": "jwt-access-token",
    "token_type": "Bearer",
    "expires_in": 1800,
    "user": {
      "id": 1,
      "email": "doha@example.com",
      "name": "도하",
      "status": "ACTIVE",
      "last_login_at": "2026-07-18T06:00:00Z",
      "created_at": "2026-07-18T06:00:00Z"
    }
  },
  "message": "로그인되었습니다."
}
```

Refresh Token은 `applymate_refresh_token` HttpOnly Cookie로 전달한다.

### POST /auth/refresh

요청 본문은 없고 `applymate_refresh_token` Cookie를 사용한다. 성공 시 새 Access Token을 응답하고 새 Refresh Token Cookie를 설정한다.

### POST /auth/logout

요청 본문은 없고 현재 Refresh Token Cookie가 있으면 폐기한다. 성공 시 Cookie를 제거한다.

### GET /auth/me

`Authorization: Bearer {access_token}` 헤더가 필요하다.

### 인증 오류 코드

```text
AUTH_EMAIL_ALREADY_EXISTS
AUTH_INVALID_CREDENTIALS
AUTH_TOKEN_MISSING
AUTH_TOKEN_INVALID
AUTH_TOKEN_EXPIRED
AUTH_REFRESH_TOKEN_INVALID
AUTH_REFRESH_TOKEN_EXPIRED
AUTH_REFRESH_TOKEN_REVOKED
AUTH_USER_INACTIVE
AUTH_UNAUTHORIZED
VALIDATION_ERROR
```

## 4. 커리어 프로필 API

| Method | Endpoint                        | 설명           |
| ------ | ------------------------------- | ------------ |
| GET    | `/profiles/me`                  | 내 커리어 프로필 조회 |
| POST   | `/profiles`                     | 커리어 프로필 생성   |
| PATCH  | `/profiles/me`                  | 커리어 프로필 수정   |
| GET    | `/profiles/me/skills`           | 기술 목록 조회     |
| POST   | `/profiles/me/skills`           | 기술 추가        |
| DELETE | `/profiles/me/skills/{skillId}` | 기술 삭제        |
| GET    | `/profiles/me/experiences`      | 경력 목록 조회     |
| POST   | `/profiles/me/experiences`      | 경력 추가        |
| GET    | `/profiles/me/projects`         | 프로젝트 목록 조회   |
| POST   | `/profiles/me/projects`         | 프로젝트 추가      |

## 5. 이력서 API

| Method | Endpoint                    | 설명        |
| ------ | --------------------------- | --------- |
| POST   | `/resumes/upload`           | 이력서 업로드   |
| GET    | `/resumes`                  | 이력서 목록 조회 |
| GET    | `/resumes/{resumeId}`       | 이력서 상세 조회 |
| POST   | `/resumes/{resumeId}/parse` | 이력서 내용 분석 |
| DELETE | `/resumes/{resumeId}`       | 이력서 삭제    |

## 6. 채용공고 API

| Method | Endpoint                | 설명           |
| ------ | ----------------------- | ------------ |
| POST   | `/jobs`                 | 채용공고 등록      |
| POST   | `/jobs/import-url`      | URL 기반 공고 등록 |
| GET    | `/jobs`                 | 채용공고 목록 조회   |
| GET    | `/jobs/{jobId}`         | 채용공고 상세 조회   |
| PATCH  | `/jobs/{jobId}`         | 채용공고 수정      |
| DELETE | `/jobs/{jobId}`         | 채용공고 삭제      |
| POST   | `/jobs/{jobId}/analyze` | 채용공고 분석      |

## 7. 적합도 분석 API

| Method | Endpoint                         | 설명           |
| ------ | -------------------------------- | ------------ |
| POST   | `/jobs/{jobId}/matches`          | 적합도 분석 실행    |
| GET    | `/jobs/{jobId}/matches/latest`   | 최신 적합도 결과 조회 |
| GET    | `/matches`                       | 전체 적합도 분석 목록 |
| POST   | `/matches/{matchId}/recalculate` | 적합도 재분석      |

## 8. 기업 분석 API

| Method | Endpoint                         | 설명          |
| ------ | -------------------------------- | ----------- |
| GET    | `/companies/{companyId}`         | 기업 정보 조회    |
| POST   | `/companies/{companyId}/analyze` | 기업 인재상 분석   |
| GET    | `/companies/{companyId}/values`  | 기업 핵심 가치 조회 |

## 9. AI 문서 생성 API

| Method | Endpoint                             | 설명          |
| ------ | ------------------------------------ | ----------- |
| POST   | `/documents/generate`                | 지원 문서 생성    |
| GET    | `/documents`                         | 생성 문서 목록    |
| GET    | `/documents/{documentId}`            | 생성 문서 상세 조회 |
| PATCH  | `/documents/{documentId}`            | 생성 문서 수정    |
| DELETE | `/documents/{documentId}`            | 생성 문서 삭제    |
| POST   | `/documents/{documentId}/regenerate` | 문서 재생성      |
| GET    | `/documents/{documentId}/evidence`   | 생성 근거 조회    |

### 지원 문서 생성 요청

```json
{
  "job_id": 1,
  "resume_id": 3,
  "document_type": "MOTIVATION",
  "question": "지원 동기와 입사 후 포부를 작성해 주세요.",
  "max_length": 1000
}
```

### 지원 문서 생성 응답

```json
{
  "success": true,
  "data": {
    "document_id": 15,
    "content": "지원 문서 내용",
    "evidence": [
      {
        "source_type": "PROJECT",
        "source_id": 2,
        "summary": "FastAPI 기반 AI 추론 API 구현 경험"
      }
    ]
  }
}
```

## 10. 지원 관리 API

| Method | Endpoint                               | 설명       |
| ------ | -------------------------------------- | -------- |
| POST   | `/applications`                        | 지원 공고 등록 |
| GET    | `/applications`                        | 지원 목록 조회 |
| GET    | `/applications/{applicationId}`        | 지원 상세 조회 |
| PATCH  | `/applications/{applicationId}`        | 지원 정보 수정 |
| PATCH  | `/applications/{applicationId}/status` | 지원 상태 변경 |
| DELETE | `/applications/{applicationId}`        | 지원 삭제    |

## 11. 일정 API

| Method | Endpoint                          | 설명                  |
| ------ | --------------------------------- | ------------------- |
| POST   | `/calendar/events`                | 일정 생성               |
| GET    | `/calendar/events`                | 일정 목록 조회            |
| GET    | `/calendar/events/{eventId}`      | 일정 상세 조회            |
| PATCH  | `/calendar/events/{eventId}`      | 일정 수정               |
| DELETE | `/calendar/events/{eventId}`      | 일정 삭제               |
| POST   | `/calendar/google/connect`        | Google Calendar 연결  |
| POST   | `/calendar/events/{eventId}/sync` | Google Calendar 동기화 |

## 12. 추천 API

| Method | Endpoint                                       | 설명           |
| ------ | ---------------------------------------------- | ------------ |
| GET    | `/recommendations/daily`                       | 오늘의 추천 공고 조회 |
| POST   | `/recommendations/refresh`                     | 추천 공고 재분석    |
| PATCH  | `/recommendations/{recommendationId}/hide`     | 추천 공고 숨김     |
| PATCH  | `/recommendations/{recommendationId}/favorite` | 추천 공고 관심 등록  |
