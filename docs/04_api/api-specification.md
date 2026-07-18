# API 명세

## 기본 정보

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
    "message": "입력값을 확인해 주세요."
  }
}
```

## Health API

| Method | Endpoint | 설명 |
| --- | --- | --- |
| GET | `/health` | Backend, PostgreSQL, Redis 상태 확인 |

## 인증 API

| Method | Endpoint | 설명 |
| --- | --- | --- |
| POST | `/auth/signup` | 회원가입 |
| POST | `/auth/login` | 로그인 |
| POST | `/auth/refresh` | Access Token 재발급 |
| POST | `/auth/logout` | 로그아웃 |
| GET | `/auth/me` | 현재 사용자 조회 |

## 커리어 프로필 API

모든 커리어 프로필 API는 인증이 필요하며, 현재 로그인한 사용자의 `user_id`로만 조회/수정한다.

### 기본 프로필

| Method | Endpoint | 설명 |
| --- | --- | --- |
| GET | `/profiles/me` | 내 커리어 프로필 조회 |
| POST | `/profiles` | 커리어 프로필 생성 |
| PATCH | `/profiles/me` | 커리어 프로필 수정 |

요청 예시:

```json
{
  "display_name": "도하",
  "headline": "AI 서비스를 만드는 백엔드 개발자",
  "career_level": "JUNIOR",
  "years_of_experience": 2,
  "desired_job_title": "Backend Engineer",
  "introduction": "FastAPI와 데이터 기반 제품 개발에 관심이 있습니다."
}
```

정책:

- 사용자당 프로필은 1개만 생성 가능하다.
- `career_level`은 `ENTRY`, `JUNIOR`, `MID`, `SENIOR`, `CAREER_CHANGE` 중 하나다.
- 비밀번호, 토큰, 인증 관련 정보는 응답하지 않는다.

### 기술 스택

| Method | Endpoint | 설명 |
| --- | --- | --- |
| GET | `/profiles/me/skills` | 내 기술 목록 조회 |
| POST | `/profiles/me/skills` | 기술 추가 |
| PATCH | `/profiles/me/skills/{userSkillId}` | 기술 숙련도/대표 여부 수정 |
| DELETE | `/profiles/me/skills/{userSkillId}` | 기술 삭제 |

요청 예시:

```json
{
  "name": "FastAPI",
  "category": "BACKEND",
  "proficiency_level": "ADVANCED",
  "years_of_experience": 2,
  "is_primary": true
}
```

정책:

- `skills.normalized_name`으로 기술 마스터 중복 생성을 방지한다.
- 동일 사용자가 동일 기술을 중복 등록할 수 없다.
- 타 사용자의 `userSkillId`는 404로 처리한다.

### 경력

| Method | Endpoint | 설명 |
| --- | --- | --- |
| GET | `/profiles/me/experiences` | 경력 목록 조회 |
| POST | `/profiles/me/experiences` | 경력 생성 |
| GET | `/profiles/me/experiences/{experienceId}` | 경력 상세 조회 |
| PATCH | `/profiles/me/experiences/{experienceId}` | 경력 수정 |
| DELETE | `/profiles/me/experiences/{experienceId}` | 경력 삭제 |

요청 예시:

```json
{
  "company_name": "ApplyMate Labs",
  "position": "Backend Engineer",
  "employment_type": "FULL_TIME",
  "start_date": "2024-01-01",
  "end_date": null,
  "is_current": true,
  "description": "FastAPI 기반 API 개발",
  "achievements": "인증 API와 프로필 API 구축"
}
```

정책:

- `is_current=true`이면 `end_date`는 null이어야 한다.
- `is_current=false`이면 `end_date`가 필요하다.
- 종료일은 시작일보다 빠를 수 없다.

### 프로젝트

| Method | Endpoint | 설명 |
| --- | --- | --- |
| GET | `/profiles/me/projects` | 프로젝트 목록 조회 |
| POST | `/profiles/me/projects` | 프로젝트 생성 |
| GET | `/profiles/me/projects/{projectId}` | 프로젝트 상세 조회 |
| PATCH | `/profiles/me/projects/{projectId}` | 프로젝트 수정 |
| DELETE | `/profiles/me/projects/{projectId}` | 프로젝트 삭제 |

요청 예시:

```json
{
  "name": "ApplyMate AI",
  "summary": "개인용 AI 취업 매니저",
  "role": "Full-stack Developer",
  "start_date": "2026-07-01",
  "end_date": null,
  "is_ongoing": true,
  "description": "회원, 인증, 커리어 프로필 구현",
  "responsibilities": "API와 화면 구현",
  "achievements": "v0.1.2 릴리즈",
  "repository_url": "https://github.com/DDORINY/ApplyMate-AI",
  "service_url": null,
  "skill_names": ["FastAPI", "Next.js", "PostgreSQL"]
}
```

정책:

- `repository_url`, `service_url`은 `http` 또는 `https`만 허용한다.
- `skill_names`는 기술 마스터 생성/재사용 후 `project_skills`로 연결한다.
- 진행 중 프로젝트는 종료일을 null로 둘 수 있다.

### 희망 조건

| Method | Endpoint | 설명 |
| --- | --- | --- |
| GET | `/profiles/me/preferences` | 희망 조건 조회 |
| PUT | `/profiles/me/preferences` | 희망 조건 저장/전체 갱신 |
| PATCH | `/profiles/me/preferences` | 희망 조건 부분 수정 |

요청 예시:

```json
{
  "preferred_employment_types": ["FULL_TIME"],
  "preferred_locations": ["서울", "원격"],
  "preferred_company_sizes": ["STARTUP", "MID_SIZED"],
  "remote_preference": "HYBRID",
  "minimum_salary": 40000000,
  "desired_roles": ["Backend Engineer"],
  "priority_keywords": ["AI", "FastAPI"]
}
```

### 지원 제외 조건

| Method | Endpoint | 설명 |
| --- | --- | --- |
| GET | `/profiles/me/exclusions` | 제외 조건 목록 조회 |
| POST | `/profiles/me/exclusions` | 제외 조건 생성 |
| PATCH | `/profiles/me/exclusions/{conditionId}` | 제외 조건 수정 |
| DELETE | `/profiles/me/exclusions/{conditionId}` | 제외 조건 삭제 |

요청 예시:

```json
{
  "condition_type": "LOCATION",
  "value": "해외 상주",
  "reason": "현재 국내 근무만 가능",
  "is_active": true
}
```

### 포트폴리오 링크

| Method | Endpoint | 설명 |
| --- | --- | --- |
| GET | `/profiles/me/portfolio-links` | 포트폴리오 링크 목록 조회 |
| POST | `/profiles/me/portfolio-links` | 포트폴리오 링크 생성 |
| PATCH | `/profiles/me/portfolio-links/{linkId}` | 포트폴리오 링크 수정 |
| DELETE | `/profiles/me/portfolio-links/{linkId}` | 포트폴리오 링크 삭제 |

요청 예시:

```json
{
  "link_type": "GITHUB",
  "title": "GitHub",
  "url": "https://github.com/DDORINY",
  "is_primary": true,
  "display_order": 0
}
```

정책:

- `http`, `https` URL만 허용한다.
- `javascript:`, `data:`, `file:` URL은 차단한다.
- 사용자별 동일 URL 중복 등록을 차단한다.
- 대표 링크는 사용자당 하나만 유지한다.

## v0.1.2 주요 오류 코드

```text
PROFILE_NOT_FOUND
PROFILE_ALREADY_EXISTS
SKILL_ALREADY_REGISTERED
SKILL_NOT_FOUND
USER_SKILL_NOT_FOUND
EXPERIENCE_NOT_FOUND
EXPERIENCE_INVALID_DATE_RANGE
PROJECT_NOT_FOUND
PROJECT_INVALID_DATE_RANGE
PREFERENCE_NOT_FOUND
EXCLUDED_CONDITION_NOT_FOUND
PORTFOLIO_LINK_NOT_FOUND
VALIDATION_ERROR
```
