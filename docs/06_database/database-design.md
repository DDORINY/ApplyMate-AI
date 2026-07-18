# ApplyMate AI Database Design

## v0.1.1 인증 스키마

날짜와 시간은 UTC 기준으로 저장한다. Refresh Token 원문은 저장하지 않고 SHA-256 해시만 저장한다.

### users

| 컬럼 | 타입 | 제약조건 | 설명 |
| ---- | ---- | -------- | ---- |
| id | integer | primary key | 사용자 식별자 |
| email | varchar(255) | not null, unique index | 소문자와 공백 제거로 정규화된 이메일 |
| password_hash | varchar(512) | not null | PBKDF2-SHA256 비밀번호 해시 |
| name | varchar(100) | not null | 사용자 이름 |
| status | enum | not null, default ACTIVE | ACTIVE, INACTIVE, WITHDRAWN |
| last_login_at | timestamptz | nullable | 마지막 로그인 시각 |
| created_at | timestamptz | not null | 생성 시각 |
| updated_at | timestamptz | not null | 수정 시각 |

### refresh_tokens

| 컬럼 | 타입 | 제약조건 | 설명 |
| ---- | ---- | -------- | ---- |
| id | integer | primary key | Refresh Token 식별자 |
| user_id | integer | foreign key users.id, index | 토큰 소유 사용자 |
| token_hash | varchar(128) | not null, unique index | Refresh Token 원문 SHA-256 해시 |
| expires_at | timestamptz | not null | 만료 시각 |
| revoked_at | timestamptz | nullable | 폐기 시각 |
| created_at | timestamptz | not null | 생성 시각 |
| device_info | varchar(255) | nullable | 요청 User-Agent 기반 기기 정보 |

## 삭제 정책

`refresh_tokens.user_id`는 `users.id`를 참조하며 사용자 삭제 시 관련 Refresh Token은 cascade 삭제한다. v0.1.1에서는 회원 탈퇴 API를 구현하지 않으므로 운영 데이터 삭제 흐름은 포함하지 않는다.

## Migration

```text
backend/alembic/versions/20260718_1501_create_auth_tables.py
```

`upgrade`는 `users`, `refresh_tokens`, `user_status` enum, index, unique constraint, foreign key를 생성한다. `downgrade`는 역순으로 제거한다.
