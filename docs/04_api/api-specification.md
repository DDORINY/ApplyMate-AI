# API Specification

## 기준

- Base URL: `/api/v1`
- 인증: Bearer Access Token
- 공통 성공 응답:

```json
{
  "success": true,
  "data": {},
  "message": "요청이 정상적으로 처리되었습니다."
}
```

- 공통 오류 응답:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "오류 메시지"
  }
}
```

## Health

| Method | Path | 인증 | 버전 | 설명 |
| --- | --- | --- | --- | --- |
| GET | `/health` | 불필요 | v0.1.0 | API, DB, Redis 상태 확인 |

## Auth

| Method | Path | 인증 | 버전 | 설명 |
| --- | --- | --- | --- | --- |
| POST | `/auth/signup` | 불필요 | v0.1.1 | 이메일 회원가입 |
| POST | `/auth/login` | 불필요 | v0.1.1 | 로그인 |
| POST | `/auth/refresh` | Refresh Cookie | v0.1.1 | access token 재발급 |
| POST | `/auth/logout` | Refresh Cookie | v0.1.1 | 로그아웃 |
| GET | `/auth/me` | Access Token | v0.1.1 | 현재 사용자 조회 |

## Account Security

| Method | Path | 인증 | 버전 | 설명 |
| --- | --- | --- | --- | --- |
| POST | `/auth/email-verification/send` | Access Token | v0.1.4 | 이메일 인증 발송 |
| POST | `/auth/email-verification/verify` | 불필요 | v0.1.4 | 이메일 인증 완료 |
| POST | `/auth/password/forgot` | 불필요 | v0.1.4 | 비밀번호 재설정 요청 |
| POST | `/auth/password/reset` | 불필요 | v0.1.4 | 비밀번호 재설정 |
| POST | `/auth/password/change` | Access Token | v0.1.4 | 비밀번호 변경 |
| POST | `/auth/password/set` | Access Token | v0.1.4 | 소셜 계정 비밀번호 설정 |
| GET | `/auth/sessions` | Access Token | v0.1.4 | 세션 목록 |
| DELETE | `/auth/sessions/others` | Access Token | v0.1.4 | 다른 세션 모두 해제 |
| DELETE | `/auth/sessions/{sessionId}` | Access Token | v0.1.4 | 특정 세션 해제 |
| GET | `/auth/security-events` | Access Token | v0.1.4 | 보안 이벤트 목록 |

## OAuth

| Method | Path | 인증 | 버전 | 설명 |
| --- | --- | --- | --- | --- |
| GET | `/auth/oauth/providers` | 불필요 | v0.1.3 | Google/GitHub 활성 상태 |
| GET | `/auth/oauth/{provider}/authorize` | 선택 | v0.1.3 | 로그인 OAuth URL 생성 |
| GET | `/auth/oauth/{provider}/link/authorize` | Access Token | v0.1.3 | 계정 연결 OAuth URL 생성 |
| GET | `/auth/oauth/{provider}/callback` | 불필요 | v0.1.3 | OAuth callback |
| POST | `/auth/oauth/exchange` | 불필요 | v0.1.3 | ticket을 token으로 교환 |
| GET | `/auth/oauth/accounts` | Access Token | v0.1.3 | 연결 계정 목록 |
| DELETE | `/auth/oauth/accounts/{provider}` | Access Token | v0.1.3 | 연결 계정 해제 |

## Career Profile

| Method | Path | 인증 | 버전 | 설명 |
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

| Method | Path | 인증 | 버전 | 설명 |
| --- | --- | --- | --- | --- |
| POST | `/jobs` | Access Token | v0.2.0 | 공고 직접 등록 |
| POST | `/jobs/import-url` | Access Token | v0.2.0 | URL 기반 공고 등록 |
| GET | `/jobs` | Access Token | v0.2.0 | 공고 목록 |
| GET | `/jobs/{jobId}` | Access Token | v0.2.0 | 공고 상세 |
| PATCH | `/jobs/{jobId}` | Access Token | v0.2.0 | 공고 수정 |
| DELETE | `/jobs/{jobId}` | Access Token | v0.2.0 | 공고 삭제 |

## AI Providers

| Method | Path | 인증 | 버전 | 설명 |
| --- | --- | --- | --- | --- |
| GET | `/ai/providers` | Access Token | v0.2.1 | 현재 AI Provider 상태 |

## Job Analysis

| Method | Path | 인증 | 버전 | 설명 |
| --- | --- | --- | --- | --- |
| POST | `/jobs/{jobId}/analysis` | Access Token | v0.2.1 | 공고 분석 실행 |
| GET | `/jobs/{jobId}/analysis` | Access Token | v0.2.1 | 현재 분석 조회 |
| PATCH | `/jobs/{jobId}/analysis` | Access Token | v0.2.1 | 사용자 검토 수정 |
| DELETE | `/jobs/{jobId}/analysis` | Access Token | v0.2.1 | 현재 분석 삭제 |
| GET | `/jobs/{jobId}/analysis/runs` | Access Token | v0.2.1 | 분석 실행 이력 |

## Job Matching

| Method | Path | 인증 | 버전 | 설명 |
| --- | --- | --- | --- | --- |
| POST | `/jobs/{jobId}/match` | Access Token | v0.2.2 | 적합도 분석 실행 |
| GET | `/jobs/{jobId}/match` | Access Token | v0.2.2 | 현재 적합도 조회 |
| DELETE | `/jobs/{jobId}/match` | Access Token | v0.2.2 | 현재 적합도 삭제 |
| GET | `/jobs/{jobId}/match/runs` | Access Token | v0.2.2 | 적합도 실행 이력 |
| POST | `/jobs/{jobId}/match/feedback` | Access Token | v0.2.2 | 피드백 등록 |
| GET | `/jobs/{jobId}/match/feedback` | Access Token | v0.2.2 | 피드백 목록 |
| PATCH | `/jobs/{jobId}/match/feedback/{feedbackId}` | Access Token | v0.2.2 | 피드백 수정 |
| DELETE | `/jobs/{jobId}/match/feedback/{feedbackId}` | Access Token | v0.2.2 | 피드백 삭제 |

## Resumes

| Method | Path | 인증 | 버전 | 설명 |
| --- | --- | --- | --- | --- |
| POST | `/resumes` | Access Token | v0.3.0 | 이력서 메타데이터 생성 |
| GET | `/resumes` | Access Token | v0.3.0 | 이력서 목록 조회 |
| GET | `/resumes/{resumeId}` | Access Token | v0.3.0 | 이력서 상세 조회 |
| PATCH | `/resumes/{resumeId}` | Access Token | v0.3.0 | 이력서 제목/설명/기본 여부 수정 |
| DELETE | `/resumes/{resumeId}` | Access Token | v0.3.0 | 이력서 및 연결 파일 삭제 |
| POST | `/resumes/{resumeId}/default` | Access Token | v0.3.0 | 기본 이력서 지정 |
| POST | `/resumes/{resumeId}/files` | Access Token | v0.3.0 | PDF/DOCX 파일 업로드 |
| GET | `/resumes/{resumeId}/files/{fileId}` | Access Token | v0.3.0 | 파일 메타데이터 조회 |
| GET | `/resumes/{resumeId}/files/{fileId}/download` | Access Token | v0.3.0 | 파일 다운로드 |
| DELETE | `/resumes/{resumeId}/files/{fileId}` | Access Token | v0.3.0 | 파일 삭제 |
| POST | `/resumes/{resumeId}/files/{fileId}/extraction` | Access Token | v0.3.1 | 이력서 파일 텍스트 추출 실행 |
| GET | `/resumes/{resumeId}/files/{fileId}/extraction` | Access Token | v0.3.1 | 이력서 파일 텍스트 추출 결과 조회 |

`POST /resumes/{resumeId}/files` 요청은 `multipart/form-data`이며 필드명은 `file`이다.

## v0.3.0 Resume Upload 보안 검증

- PDF는 확장자 `.pdf`, MIME `application/pdf`, magic bytes `%PDF-`를 모두 검증한다.
- DOCX는 확장자 `.docx`, MIME `application/vnd.openxmlformats-officedocument.wordprocessingml.document`, ZIP 구조, `[Content_Types].xml`, `word/document.xml`을 모두 검증한다.
- 파일 크기는 64KB chunk 단위로 읽으며 `RESUME_MAX_FILE_SIZE_BYTES` 초과 즉시 거부한다.
- 원본 파일명에 경로 구분자, NULL byte, 제어 문자가 있으면 거부한다.
- 내부 저장명은 UUID 기반이며 원본 파일명을 저장 경로에 사용하지 않는다.
- 다운로드는 storage base directory 내부 경로인지 재검증한다.
- 다운로드 응답은 `Content-Disposition: attachment`, `filename*`, `X-Content-Type-Options: nosniff`를 사용한다.

## v0.3.1 Resume Text Extraction

- `POST /resumes/{resumeId}/files/{fileId}/extraction`은 업로드된 PDF/DOCX 파일에서 텍스트를 추출하고 최신 결과를 저장한다.
- `GET /resumes/{resumeId}/files/{fileId}/extraction`은 저장된 최신 추출 결과를 반환한다.
- 추출 결과는 `COMPLETED` 또는 `FAILED` 상태를 가진다.
- 추출 결과에는 `extracted_text`, `text_length`, `parser_version`, `source_file_hash`, `error_code`, `error_message`, `extracted_at`을 포함한다.
- v0.3.1의 PDF 추출은 text literal 기반 best-effort이며, OCR과 이미지 PDF 분석은 포함하지 않는다.
