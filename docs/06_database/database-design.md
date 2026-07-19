# Database Design

## 기준

- DB: PostgreSQL
- ORM: SQLAlchemy
- Migration: Alembic
- 현재 migration head: `20260719_1500`

## 현재 테이블 목록

```text
users
refresh_tokens
oauth_accounts
oauth_states
oauth_login_tickets
career_profiles
skills
user_skills
experiences
projects
project_skills
job_preferences
excluded_conditions
portfolio_links
email_verification_tokens
password_reset_tokens
security_events
companies
job_postings
job_analyses
job_analysis_runs
job_matches
job_match_runs
job_match_feedback
resumes
resume_files
```

## 인증/계정

- `users`: 사용자 기본 정보, 이메일, 비밀번호 해시, 상태
- `refresh_tokens`: refresh token hash와 세션 정보
- `email_verification_tokens`: 이메일 인증 토큰
- `password_reset_tokens`: 비밀번호 재설정 토큰
- `security_events`: 로그인/비밀번호/세션/소셜 연결 이벤트

## OAuth

- `oauth_accounts`: 사용자와 provider 계정 연결
- `oauth_states`: OAuth state 검증
- `oauth_login_tickets`: frontend callback 교환용 임시 ticket

## 커리어 프로필

- `career_profiles`
- `skills`
- `user_skills`
- `experiences`
- `projects`
- `project_skills`
- `job_preferences`
- `excluded_conditions`
- `portfolio_links`

모든 사용자 소유 데이터는 `user_id`를 기준으로 소유권을 검사한다.

## 채용공고

- `companies`: 정규화된 회사 정보
- `job_postings`: 사용자별 채용공고

주요 제약:

- `(user_id, source_url)` unique
- `(user_id, content_hash)` unique
- 회사명은 `normalized_name`으로 중복 방지

## AI 채용공고 분석

- `job_analyses`: 현재 공고 분석 결과
- `job_analysis_runs`: provider, model, token, latency, 오류 이력

## 사용자-공고 적합도 분석

- `job_matches`: 현재 적합도 결과
- `job_match_runs`: 적합도 계산 실행 이력
- `job_match_feedback`: 사용자 피드백

주요 제약:

- `(user_id, job_posting_id)` unique
- 점수 컬럼은 0~100 범위

## 이력서 업로드

### resumes

사용자 이력서 메타데이터.

| 컬럼 | 설명 |
| --- | --- |
| `id` | PK |
| `user_id` | 사용자 FK |
| `title` | 이력서 제목 |
| `description` | 설명 |
| `source_type` | `USER_UPLOAD`, `MANUAL` |
| `is_default` | 기본 이력서 여부 |
| `created_at` | 생성 시각 |
| `updated_at` | 수정 시각 |

### resume_files

업로드 파일 메타데이터와 로컬 저장 경로.

| 컬럼 | 설명 |
| --- | --- |
| `id` | PK |
| `resume_id` | 이력서 FK |
| `user_id` | 사용자 FK |
| `original_filename` | 표시용 원본 파일명 |
| `stored_filename` | UUID 기반 내부 저장명 |
| `storage_path` | 로컬 저장 경로 |
| `content_type` | MIME |
| `file_extension` | 확장자 |
| `file_size` | 파일 크기 |
| `file_hash` | SHA-256 |
| `uploaded_at` | 업로드 시각 |
| `created_at` | 생성 시각 |

제약:

- `(user_id, file_hash)` unique
- `stored_filename` unique
- `resume_id`와 `user_id`는 cascade 삭제

## Migration 목록

| Revision | 설명 |
| --- | --- |
| `20260718_1501` | auth tables |
| `20260718_1900` | career profile tables |
| `20260718_2100` | social auth |
| `20260719_1000` | account security |
| `20260719_1200` | job posting |
| `20260719_1300` | job analysis |
| `20260719_1400` | job matching |
| `20260719_1500` | resume upload |
| `20260719_1600` | resume text extraction |

## v0.3.0 보완 DB 제약

사용자당 기본 이력서는 PostgreSQL partial unique index로 최대 하나만 허용한다.

```sql
CREATE UNIQUE INDEX uq_resumes_one_default_per_user
ON resumes (user_id)
WHERE is_default = true;
```

`resume_files`는 사용자별 파일 hash 중복을 방지한다.

```text
uq_resume_files_user_file_hash = (user_id, file_hash)
```

원본 파일명은 표시용이며 저장 경로에는 사용하지 않는다. 실제 저장 파일명은 UUID 기반이다.

## v0.3.1 Resume Extraction

### `resume_file_extractions`

업로드된 이력서 파일의 최신 텍스트 추출 결과와 사용자 수정본을 저장한다.

| 컬럼 | 설명 |
| --- | --- |
| `id` | Primary Key |
| `resume_file_id` | 대상 이력서 파일 ID, 파일 삭제 시 cascade |
| `user_id` | 소유 사용자 ID |
| `extraction_status` | `PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`, `TEXT_NOT_FOUND`, `OCR_REQUIRED` |
| `raw_text` | 시스템이 원본 파일에서 추출한 텍스트 |
| `edited_text` | 사용자가 수정한 텍스트 |
| `page_texts` | 페이지별 텍스트 JSON. DOCX는 단일 logical page |
| `section_candidates` | 규칙 기반 섹션 후보 JSON |
| `page_count` | 페이지 수 또는 logical page 수 |
| `character_count` | 현재 추출/수정 텍스트 길이 |
| `input_hash` | 추출 당시 원본 파일 hash |
| `is_outdated` | 현재 파일 hash와 `input_hash`가 다른지 여부 |
| `is_user_edited` | 사용자 수정본 존재 여부 |
| `current_run_id` | 최신 실행 이력 ID |
| `error_code`, `error_message` | 실패 시 오류 정보 |
| `extracted_at` | 추출 실행 시각 |

제약:

- `resume_file_id`는 unique로 관리하여 파일당 최신 추출 결과 1개만 유지한다.
- 모든 조회는 `user_id` 소유권 조건을 함께 사용한다.

### `resume_extraction_runs`

이력서 텍스트 추출 실행 이력을 보존한다. 재추출 시 기존 이력을 덮어쓰지 않고 새 run을 추가한다.

| 컬럼 | 설명 |
| --- | --- |
| `id` | Primary Key |
| `extraction_id` | 연결된 최신 추출 결과 ID |
| `resume_file_id` | 대상 파일 ID |
| `user_id` | 소유 사용자 ID |
| `status` | 실행 최종 상태 |
| `input_hash` | 실행 당시 파일 hash |
| `extractor`, `extractor_version` | 추출기 식별자와 버전 |
| `started_at`, `completed_at` | 실행 시작/종료 시각 |
| `error_code`, `error_message` | 실패 또는 특수 상태 사유 |
| `page_count`, `character_count` | 실행 결과 메타데이터 |
| `metadata_json` | page_texts, section_candidates 등 실행 메타데이터 |

설계 정책:

- `raw_text`는 재추출 결과로 갱신될 수 있지만 `edited_text`는 사용자가 수정한 값으로 별도 보존한다.
- 재추출은 실행 이력을 보존하며 최신 결과만 `resume_file_extractions`에 반영한다.
- OCR은 v0.3.1에서 실행하지 않으며 텍스트 레이어가 없는 PDF는 `OCR_REQUIRED`로 기록한다.
