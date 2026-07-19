# Error Codes

## 공통

| Code | HTTP Status | 설명 |
| --- | ---: | --- |
| `VALIDATION_ERROR` | 422 | 요청 값이 올바르지 않음 |
| `RESOURCE_NOT_FOUND` | 404 | 경로 또는 리소스를 찾을 수 없음 |
| `INTERNAL_SERVER_ERROR` | 500 | 서버 내부 오류 |

## 인증/계정

| Code | HTTP Status | 설명 |
| --- | ---: | --- |
| `AUTH_TOKEN_MISSING` | 401 | 인증 토큰 없음 |
| `AUTH_TOKEN_INVALID` | 401 | 인증 토큰 유효하지 않음 |
| `AUTH_UNAUTHORIZED` | 500 | 인증 설정 미완료 |
| `AUTH_EMAIL_ALREADY_EXISTS` | 409 | 이미 가입된 이메일 |
| `AUTH_INVALID_CREDENTIALS` | 401 | 잘못된 로그인 정보 |
| `AUTH_USER_INACTIVE` | 403 | 비활성 사용자 |

## 채용공고/분석

| Code | HTTP Status | 설명 |
| --- | ---: | --- |
| `JOB_POSTING_NOT_FOUND` | 404 | 채용공고 없음 |
| `JOB_POSTING_ALREADY_EXISTS` | 409 | 중복 채용공고 |
| `JOB_POSTING_URL_BLOCKED` | 422 | 차단된 URL |
| `JOB_POSTING_URL_FETCH_FAILED` | 502 | URL 요청 실패 |
| `JOB_POSTING_URL_UNSUPPORTED_CONTENT` | 415 | 지원하지 않는 URL 응답 |
| `JOB_POSTING_URL_CONTENT_TOO_LARGE` | 413 | URL 응답 크기 초과 |
| `JOB_INVALID_SALARY_RANGE` | 422 | 급여 범위 오류 |
| `JOB_INVALID_DEADLINE` | 422 | 마감일 오류 |
| `JOB_DEADLINE_REQUIRED` | 422 | 고정 마감일 누락 |
| `AI_PROVIDER_DISABLED` | 503 | AI Provider 비활성 |
| `AI_PROVIDER_CONFIG_INVALID` | 503 | AI Provider 설정 오류 |
| `JOB_ANALYSIS_NOT_FOUND` | 404 | 공고 분석 없음 |
| `JOB_MATCH_NOT_FOUND` | 404 | 적합도 분석 없음 |

## 이력서 업로드

| Code | HTTP Status | 설명 |
| --- | ---: | --- |
| `RESUME_NOT_FOUND` | 404 | 이력서를 찾을 수 없거나 현재 사용자의 이력서가 아님 |
| `RESUME_FILE_NOT_FOUND` | 404 | 이력서 파일을 찾을 수 없거나 현재 사용자의 파일이 아님 |
| `RESUME_FILE_NAME_REQUIRED` | 422 | 업로드 파일명 없음 |
| `RESUME_FILE_EXTENSION_NOT_ALLOWED` | 422 | 허용되지 않는 파일 확장자 |
| `RESUME_FILE_CONTENT_TYPE_NOT_ALLOWED` | 422 | 허용되지 않는 MIME 타입 |
| `RESUME_FILE_EMPTY` | 422 | 빈 파일 |
| `RESUME_FILE_TOO_LARGE` | 413 | 업로드 파일 크기 제한 초과 |
| `RESUME_FILE_ALREADY_EXISTS` | 409 | 동일 해시 파일 중복 |
| `RESUME_FILE_STORAGE_FAILED` | 500 | 파일 저장 실패 |
