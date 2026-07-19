# 데이터베이스 설계 개요

이 문서는 기술 설계 관점의 DB 원칙을 요약합니다. 실제 상세 스키마와 ERD는 다음 문서를 기준으로 합니다.

- `docs/06_database/database-design.md`
- `docs/06_database/erd.md`

## 현재 구현 스키마

v0.1.3 기준 구현 테이블:

- `users`
- `refresh_tokens`
- `oauth_accounts`
- `oauth_states`
- `oauth_login_tickets`
- `career_profiles`
- `skills`
- `user_skills`
- `experiences`
- `projects`
- `project_skills`
- `job_preferences`
- `excluded_conditions`
- `portfolio_links`

## 설계 원칙

- PostgreSQL을 기본 데이터베이스로 사용합니다.
- 모든 테이블은 명확한 Primary Key를 가집니다.
- 사용자 소유 데이터는 `user_id`로 소유자를 연결합니다.
- 보호 API는 인증된 사용자의 `user_id` 조건을 반드시 포함합니다.
- 상태 값은 Enum 또는 제한된 값으로 관리합니다.
- 스키마 변경은 Alembic migration으로 관리합니다.
- 운영 DB를 승인 없는 직접 변경으로 수정하지 않습니다.

## Migration

```text
backend/alembic/versions/20260718_1501_create_auth_tables.py
backend/alembic/versions/20260718_1900_create_career_profile_tables.py
backend/alembic/versions/20260718_2100_add_social_auth.py
```

검증:

```bash
cd backend
alembic upgrade head
alembic downgrade -1
alembic upgrade head
```

## 향후 스키마

| 버전 | 테이블 후보 | 목적 |
| --- | --- | --- |
| v0.2.x | `job_postings`, `companies`, `job_requirements` | 채용공고 관리 |
| v0.2.x | `job_matches`, `match_findings` | 적합도 분석 결과 |
| v0.3.x | `resumes`, `generated_documents`, `document_evidence` | 이력서/AI 문서 |
| v0.4.x | `applications`, `calendar_events` | 지원 현황과 일정 |
| v0.5.x | `external_accounts`, `calendar_sync_logs` | 외부 서비스 연동 |

pgvector는 v0.3.x 이후 의미 기반 검색과 분석이 필요할 때 도입합니다. v0.1.3에서는 확장 설치나 벡터 컬럼을 만들지 않습니다.
# v0.2.0 채용공고 DB 변경 요약

- `companies` 테이블을 추가한다.
- `job_postings` 테이블을 추가한다.
- `job_postings.user_id`로 사용자 소유권을 관리한다.
- `job_postings.company_id`로 기업 정보를 참조한다.
- enum으로 기업 규모, source type, 상태, 고용 형태, 근무 형태, 마감 유형을 제한한다.
- 동일 사용자 기준 `source_url`, `content_hash`, `company_id + title + deadline_at`으로 중복을 방지한다.
- migration 파일은 `backend/alembic/versions/20260719_1200_create_job_posting_tables.py`이다.
# v0.2.1 AI 채용공고 분석 DB 변경

- `job_analyses`: 채용공고별 현재 AI 분석 결과를 1개 저장합니다.
- `job_analysis_runs`: 분석 실행 이력, Provider, token 사용량, 실패 사유를 저장합니다.
- 분석 상태 enum은 `PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`를 사용합니다.
- 분석 결과의 구조화 필드는 PostgreSQL JSONB로 저장합니다.
- `job_analyses.job_posting_id`는 unique 제약으로 공고당 current 분석 1개를 보장합니다.
- `user_id`와 `job_posting_id` 기반 외래키와 index로 사용자 소유권 검사와 조회 성능을 확보합니다.
- migration: `backend/alembic/versions/20260719_1300_create_job_analysis_tables.py`
# v0.2.2 사용자-공고 적합도 분석 DB 변경

Migration:

```text
backend/alembic/versions/20260719_1400_create_job_match_tables.py
```

## job_matches

공고별 현재 적합도 분석 결과를 1개 저장합니다.

- `user_id`: 사용자 소유권 검사용 FK
- `job_posting_id`: 대상 채용공고 FK, 사용자별 unique
- `job_analysis_id`: 적합도 계산에 사용한 완료된 공고 분석 FK
- `status`: `PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`
- `total_score`: 0~100 종합 점수
- `grade`: `EXCELLENT`, `GOOD`, `MODERATE`, `LOW`, `VERY_LOW`
- `recommendation_status`: `STRONGLY_RECOMMENDED`, `RECOMMENDED`, `CONSIDER`, `NOT_RECOMMENDED`, `INSUFFICIENT_DATA`
- `role_score`, `skill_score`, `experience_score`, `project_score`, `preference_score`, `risk_score`
- `matched_skills`, `missing_skills`, `matched_projects`, `strengths`, `gaps`, `risks`: JSON 근거 데이터
- `profile_hash`, `job_analysis_hash`: 최신성 판단용 hash
- `calculation_version`, `explanation_provider`, `calculated_at`

## job_match_runs

적합도 분석 실행 이력을 저장합니다. 현재 결과가 삭제되어도 실행 이력은 `job_match_id = null`로 보존됩니다.

## job_match_feedback

사용자가 적합도 결과에 대한 피드백을 남기는 테이블입니다.

- `feedback_type`: `ACCURATE`, `TOO_HIGH`, `TOO_LOW`, `MISSING_STRENGTH`, `MISSING_RISK`, `OTHER`
- `rating`: 1~5 선택값
- `comment`: 선택 입력
