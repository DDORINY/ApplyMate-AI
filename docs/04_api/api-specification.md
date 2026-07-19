# API 명세

Base URL: `/api/v1`

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
    "code": "ERROR_CODE",
    "message": "오류 메시지"
  }
}
```

보호 API는 `Authorization: Bearer {access_token}` 헤더가 필요하다.

## Health

| Method | Path | 인증 | 구현 버전 | 설명 |
| --- | --- | --- | --- | --- |
| GET | `/health` | 불필요 | v0.1.0 | Backend, PostgreSQL, Redis 상태 |

## Auth

| Method | Path | 인증 | 구현 버전 | 설명 |
| --- | --- | --- | --- | --- |
| POST | `/auth/signup` | 불필요 | v0.1.1 | 이메일 회원가입 |
| POST | `/auth/login` | 불필요 | v0.1.1 | 이메일 로그인 |
| POST | `/auth/refresh` | Refresh Cookie | v0.1.1 | Access Token 재발급 |
| POST | `/auth/logout` | Refresh Cookie | v0.1.1 | 로그아웃 |
| GET | `/auth/me` | Access Token | v0.1.1 | 현재 사용자 조회 |

## Account Security

| Method | Path | 인증 | 구현 버전 | 설명 |
| --- | --- | --- | --- | --- |
| POST | `/auth/email-verification/send` | Access Token | v0.1.4 | 이메일 인증 발송/재발송 |
| POST | `/auth/email-verification/verify` | 불필요 | v0.1.4 | 이메일 인증 token 검증 |
| POST | `/auth/password/forgot` | 불필요 | v0.1.4 | 비밀번호 재설정 요청 |
| POST | `/auth/password/reset` | 불필요 | v0.1.4 | 비밀번호 재설정 |
| POST | `/auth/password/change` | Access Token | v0.1.4 | 현재 비밀번호 기반 변경 |
| POST | `/auth/password/set` | Access Token | v0.1.4 | 비밀번호 없는 계정의 비밀번호 설정 |
| GET | `/auth/sessions` | Access Token | v0.1.4 | 로그인 세션 목록 |
| DELETE | `/auth/sessions/{sessionId}` | Access Token | v0.1.4 | 개별 세션 폐기 |
| DELETE | `/auth/sessions/others` | Access Token | v0.1.4 | 다른 모든 세션 폐기 |
| DELETE | `/auth/sessions` | Access Token | v0.1.4 | 전체 세션 폐기 |
| GET | `/auth/security-events` | Access Token | v0.1.4 | 보안 이벤트 목록 |

## OAuth

| Method | Path | 인증 | 구현 버전 | 설명 |
| --- | --- | --- | --- | --- |
| GET | `/auth/oauth/providers` | 불필요 | v0.1.3 | OAuth provider 상태 |
| GET | `/auth/oauth/{provider}/authorize` | 불필요 | v0.1.3 | 로그인 authorize URL |
| GET | `/auth/oauth/{provider}/link/authorize` | Access Token | v0.1.3 | 계정 연결 authorize URL |
| GET | `/auth/oauth/{provider}/callback` | Provider redirect | v0.1.3 | OAuth callback |
| POST | `/auth/oauth/exchange` | 불필요 | v0.1.3 | one-time ticket 교환 |
| GET | `/auth/oauth/accounts` | Access Token | v0.1.3 | 연결 계정 목록 |
| DELETE | `/auth/oauth/accounts/{provider}` | Access Token | v0.1.3 | 연결 계정 해제 |

지원 provider path 값: `google`, `github`.

## Career Profile

| Method | Path | 인증 | 구현 버전 | 설명 |
| --- | --- | --- | --- | --- |
| GET | `/profiles/me` | Access Token | v0.1.2 | 내 프로필 조회 |
| POST | `/profiles` | Access Token | v0.1.2 | 프로필 생성 |
| PATCH | `/profiles/me` | Access Token | v0.1.2 | 프로필 수정 |
| GET | `/profiles/me/skills` | Access Token | v0.1.2 | 기술 목록 |
| POST | `/profiles/me/skills` | Access Token | v0.1.2 | 기술 추가 |
| PATCH | `/profiles/me/skills/{userSkillId}` | Access Token | v0.1.2 | 기술 수정 |
| DELETE | `/profiles/me/skills/{userSkillId}` | Access Token | v0.1.2 | 기술 삭제 |
| GET | `/profiles/me/experiences` | Access Token | v0.1.2 | 경력 목록 |
| POST | `/profiles/me/experiences` | Access Token | v0.1.2 | 경력 추가 |
| GET | `/profiles/me/experiences/{experienceId}` | Access Token | v0.1.2 | 경력 상세 |
| PATCH | `/profiles/me/experiences/{experienceId}` | Access Token | v0.1.2 | 경력 수정 |
| DELETE | `/profiles/me/experiences/{experienceId}` | Access Token | v0.1.2 | 경력 삭제 |
| GET | `/profiles/me/projects` | Access Token | v0.1.2 | 프로젝트 목록 |
| POST | `/profiles/me/projects` | Access Token | v0.1.2 | 프로젝트 추가 |
| GET | `/profiles/me/projects/{projectId}` | Access Token | v0.1.2 | 프로젝트 상세 |
| PATCH | `/profiles/me/projects/{projectId}` | Access Token | v0.1.2 | 프로젝트 수정 |
| DELETE | `/profiles/me/projects/{projectId}` | Access Token | v0.1.2 | 프로젝트 삭제 |
| GET | `/profiles/me/preferences` | Access Token | v0.1.2 | 희망 조건 조회 |
| PUT | `/profiles/me/preferences` | Access Token | v0.1.2 | 희망 조건 저장 |
| PATCH | `/profiles/me/preferences` | Access Token | v0.1.2 | 희망 조건 수정 |
| GET | `/profiles/me/exclusions` | Access Token | v0.1.2 | 제외 조건 목록 |
| POST | `/profiles/me/exclusions` | Access Token | v0.1.2 | 제외 조건 추가 |
| PATCH | `/profiles/me/exclusions/{conditionId}` | Access Token | v0.1.2 | 제외 조건 수정 |
| DELETE | `/profiles/me/exclusions/{conditionId}` | Access Token | v0.1.2 | 제외 조건 삭제 |
| GET | `/profiles/me/portfolio-links` | Access Token | v0.1.2 | 포트폴리오 링크 목록 |
| POST | `/profiles/me/portfolio-links` | Access Token | v0.1.2 | 포트폴리오 링크 추가 |
| PATCH | `/profiles/me/portfolio-links/{linkId}` | Access Token | v0.1.2 | 포트폴리오 링크 수정 |
| DELETE | `/profiles/me/portfolio-links/{linkId}` | Access Token | v0.1.2 | 포트폴리오 링크 삭제 |

## Jobs

| Method | Path | 인증 | 구현 버전 | 설명 |
| --- | --- | --- | --- | --- |
| POST | `/jobs` | Access Token | v0.2.0 | 공고 직접 등록 |
| POST | `/jobs/import-url` | Access Token | v0.2.0 | URL 기반 공고 등록 |
| GET | `/jobs` | Access Token | v0.2.0 | 공고 목록 |
| GET | `/jobs/{jobId}` | Access Token | v0.2.0 | 공고 상세 |
| PATCH | `/jobs/{jobId}` | Access Token | v0.2.0 | 공고 수정 |
| DELETE | `/jobs/{jobId}` | Access Token | v0.2.0 | 공고 삭제 |

목록 query:

- `page`, `size`
- `query`
- `status`
- `employment_type`
- `work_type`
- `company_id`
- `deadline_from`, `deadline_to`
- `deadline_type`
- `is_favorite`
- `source_type`
- `sort`, `order`

## AI Providers

| Method | Path | 인증 | 구현 버전 | 설명 |
| --- | --- | --- | --- | --- |
| GET | `/ai/providers` | Access Token | v0.2.1 | 현재 AI Provider 상태 |

## Job Analysis

| Method | Path | 인증 | 구현 버전 | 설명 |
| --- | --- | --- | --- | --- |
| POST | `/jobs/{jobId}/analysis` | Access Token | v0.2.1 | 공고 분석 실행 |
| GET | `/jobs/{jobId}/analysis` | Access Token | v0.2.1 | 현재 분석 조회 |
| PATCH | `/jobs/{jobId}/analysis` | Access Token | v0.2.1 | 사용자 검토 수정 |
| DELETE | `/jobs/{jobId}/analysis` | Access Token | v0.2.1 | 현재 분석 삭제 |
| GET | `/jobs/{jobId}/analysis/runs` | Access Token | v0.2.1 | 분석 실행 이력 |

`POST /jobs/{jobId}/analysis` 요청:

```json
{
  "force": false
}
```

## Job Matching

| Method | Path | 인증 | 구현 버전 | 설명 |
| --- | --- | --- | --- | --- |
| POST | `/jobs/{jobId}/match` | Access Token | v0.2.2 | 적합도 분석 실행 |
| GET | `/jobs/{jobId}/match` | Access Token | v0.2.2 | 현재 적합도 조회 |
| DELETE | `/jobs/{jobId}/match` | Access Token | v0.2.2 | 현재 적합도 삭제 |
| GET | `/jobs/{jobId}/match/runs` | Access Token | v0.2.2 | 적합도 실행 이력 |
| POST | `/jobs/{jobId}/match/feedback` | Access Token | v0.2.2 | 피드백 등록 |
| GET | `/jobs/{jobId}/match/feedback` | Access Token | v0.2.2 | 피드백 목록 |
| PATCH | `/jobs/{jobId}/match/feedback/{feedbackId}` | Access Token | v0.2.2 | 피드백 수정 |
| DELETE | `/jobs/{jobId}/match/feedback/{feedbackId}` | Access Token | v0.2.2 | 피드백 삭제 |

`POST /jobs/{jobId}/match` 요청:

```json
{
  "force": false,
  "generate_explanation": true
}
```

## 주요 오류 코드

상세 목록은 [error-codes.md](error-codes.md)를 참고한다.

- `AUTH_TOKEN_MISSING`
- `AUTH_TOKEN_INVALID`
- `PROFILE_NOT_FOUND`
- `JOB_POSTING_NOT_FOUND`
- `JOB_ANALYSIS_REQUIRED`
- `JOB_ANALYSIS_OUTDATED`
- `JOB_MATCH_PROFILE_REQUIRED`
- `JOB_MATCH_PROFILE_INCOMPLETE`
