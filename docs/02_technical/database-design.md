# 데이터베이스 설계 개요

이 문서는 기술 설계 관점의 DB 설계 원칙을 정리한다. 실제 v0.1.1 스키마 상세와 ERD는 `docs/06_database/database-design.md`, `docs/06_database/erd.md`를 따른다.

## 기본 원칙

* PostgreSQL을 기본 데이터베이스로 사용한다.
* 모든 테이블은 명확한 Primary Key를 가진다.
* 사용자 소유 데이터는 `user_id`를 통해 소유자를 식별한다.
* 날짜와 시간은 UTC 기준으로 저장한다.
* 상태값은 자유 문자열이 아니라 Enum 또는 제한된 값으로 관리한다.
* 스키마 변경은 Alembic migration으로 관리한다.
* 운영 DB는 migration 없이 직접 변경하지 않는다.

## 현재 구현 스키마

v0.1.1 기준 구현된 테이블:

* `users`
* `refresh_tokens`

## 예정 스키마

향후 버전에서 추가할 주요 도메인 테이블은 다음과 같다.

| 버전 | 테이블 후보 | 목적 |
| ---- | ----------- | ---- |
| v0.1.2 | `career_profiles`, `skills`, `experiences`, `projects` | 사용자 커리어 프로필 |
| v0.2.x | `job_postings`, `companies`, `job_requirements` | 채용공고 관리 |
| v0.2.x | `job_matches`, `match_findings` | 적합도 분석 결과 |
| v0.3.x | `resumes`, `generated_documents`, `document_evidence` | 이력서와 AI 문서 |
| v0.4.x | `applications`, `calendar_events` | 지원 현황과 일정 |
| v0.5.x | `external_accounts`, `calendar_sync_logs` | 외부 서비스 연동 |

## 사용자 데이터 분리

사용자별 데이터는 기본적으로 `user_id`를 가진다. API에서는 인증된 사용자의 `user_id`를 기준으로 조회 범위를 제한한다. 관리자 기능은 현재 범위가 아니므로 사용자 간 데이터 접근 기능을 만들지 않는다.

## 삭제 정책

* 인증 토큰은 사용자 삭제 시 cascade 삭제할 수 있다.
* 지원 기록, 문서, 일정 등 중요한 사용자 데이터 삭제는 향후 회원 탈퇴 정책에서 별도로 정의한다.
* 운영 데이터 삭제가 필요한 migration은 별도 승인 없이 진행하지 않는다.

## 인덱스 기준

* 로그인 식별자처럼 고유 조회가 잦은 컬럼에는 unique index를 둔다.
* 외래키 조회가 잦은 `user_id`에는 index를 둔다.
* 목록 검색, 필터, 정렬이 실제 API로 구현될 때 필요한 복합 index를 추가한다.

## pgvector 사용 계획

pgvector는 v0.3.x 이후 사용자 경험과 채용공고의 의미 기반 검색에 사용한다. v0.1.1에서는 확장을 설치하거나 벡터 컬럼을 만들지 않는다.
