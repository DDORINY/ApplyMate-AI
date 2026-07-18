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
