# ApplyMate AI Codex 작업 규칙

## 1. 프로젝트 개요

ApplyMate AI는 사용자의 경력, 기술, 프로젝트 경험 및 희망 조건을 기반으로 적합한 채용공고를 추천하고, 채용공고와 기업 인재상을 분석하여 맞춤형 이력서 및 자기소개서 작성을 지원하는 AI 기반 취업 관리 서비스이다.

주요 기능은 다음과 같다.

* 사용자 커리어 프로필 관리
* 이력서 및 포트폴리오 관리
* 채용공고 등록 및 분석
* 사용자와 채용공고 적합도 분석
* 기업 인재상 분석
* 근거 기반 자기소개서 생성
* 지원 현황 관리
* 일정 및 Google Calendar 연동
* 일일 맞춤 채용공고 추천

## 2. 기본 기술 스택

### Frontend

* Next.js
* TypeScript
* Tailwind CSS
* TanStack Query
* Zustand
* React Hook Form
* Zod

### Backend

* Python
* FastAPI
* SQLAlchemy
* Alembic
* Pydantic
* JWT

### Database

* PostgreSQL
* pgvector
* Redis

### Infrastructure

* Docker
* Docker Compose
* Nginx
* GitHub Actions

기존 기술 스택을 임의로 변경하지 않는다.

새로운 라이브러리가 필요한 경우 기존 라이브러리로 해결할 수 있는지 먼저 검토하고, 반드시 변경 이유를 작업 결과에 기록한다.

## 3. 문서 우선 원칙

기능 구현 전 다음 문서를 확인한다.

1. `docs/01_planning/project-plan.md`
2. `docs/02_technical/tech-stack.md`
3. `docs/03_requirements/functional-specification.md`
4. `docs/04_api/api-specification.md`
5. `docs/05_development-plan/version-roadmap.md`

문서와 코드가 충돌할 경우 임의로 코드를 작성하지 않는다.

다음 기준으로 처리한다.

* 명확한 문서가 존재하면 문서를 기준으로 구현한다.
* 문서가 서로 충돌하면 충돌 내용을 보고한다.
* 문서에 없는 기능은 임의로 추가하지 않는다.
* 기능 변경이 필요한 경우 관련 문서도 함께 수정한다.
* API 변경 시 API 명세서를 함께 수정한다.
* 데이터베이스 변경 시 DB 설계와 Alembic migration을 함께 수정한다.

## 4. 작업 범위 원칙

요청받은 범위만 작업한다.

다음 행위를 금지한다.

* 요청하지 않은 대규모 리팩터링
* 폴더 구조 임의 변경
* 기술 스택 교체
* 기존 API 경로 임의 변경
* 기존 데이터베이스 컬럼 삭제
* 사용하지 않는 기능 선행 구현
* 테스트를 통과시키기 위한 기능 제거
* 임시 mock 데이터를 운영 코드에 남기는 행위
* 관련 없는 파일 수정
* 전체 코드 포맷팅으로 불필요한 diff 생성

추가 개선이 필요하면 직접 반영하지 말고 작업 결과의 권고사항에 기록한다.

## 5. 작업 시작 전 확인

작업 시작 전 반드시 다음을 확인한다.

* 현재 브랜치
* Git 작업 트리 상태
* 관련 문서
* 관련 기존 코드
* 기존 API와 데이터 모델
* 테스트 구조
* 환경변수 사용 위치
* 기존 구현과의 중복 여부

작업 트리가 깨끗하지 않은 경우 기존 변경 내용을 삭제하거나 덮어쓰지 않는다.

사용자의 기존 변경사항은 보존한다.

## 6. 브랜치 규칙

기능별 브랜치를 생성한다.

브랜치 이름 형식:

```text
feature/v{version}-{feature-name}
fix/v{version}-{issue-name}
refactor/v{version}-{target-name}
docs/v{version}-{document-name}
```

예시:

```text
feature/v0.1.1-auth
feature/v0.1.2-career-profile
feature/v0.2.0-job-posting
fix/v0.2.1-job-parser-date
docs/v0.2.0-api-spec
```

다음은 금지한다.

* 사용자의 요청 없이 `main`에서 직접 작업
* 기존 원격 브랜치 강제 덮어쓰기
* `git push --force`
* 기존 태그 삭제
* 기존 커밋 기록 변경
* 사용자 승인 없는 main 병합

## 7. 커밋 규칙

커밋 메시지는 Conventional Commits 형식을 사용한다.

```text
feat: 새로운 기능
fix: 버그 수정
docs: 문서 수정
refactor: 기능 변경 없는 구조 개선
test: 테스트 추가 또는 수정
chore: 설정 및 빌드 작업
style: 코드 동작에 영향 없는 형식 수정
```

예시:

```text
feat: add user career profile API
fix: prevent duplicate job posting registration
docs: update job analysis API specification
test: add application status transition tests
```

한 커밋에는 하나의 논리적인 변경만 포함한다.

다음 내용을 하나의 커밋에 섞지 않는다.

* 기능 구현과 대규모 리팩터링
* 문서 수정과 무관한 코드 수정
* 여러 버전 기능 동시 구현
* 버그 수정과 신규 기능

## 8. 코드 작성 원칙

### 공통

* 읽기 쉬운 코드를 우선한다.
* 중복 코드를 최소화한다.
* 불필요한 추상화를 만들지 않는다.
* 기능 하나를 지나치게 많은 계층으로 나누지 않는다.
* 함수와 클래스 이름은 역할이 명확해야 한다.
* 주석은 코드 설명보다 이유와 제약을 기록한다.
* 사용하지 않는 코드는 제거한다.
* 임시 코드는 `TODO`와 이유를 남긴다.

### Frontend

* TypeScript의 `any` 사용을 최소화한다.
* API 요청 및 응답 타입을 정의한다.
* 서버 상태는 TanStack Query로 관리한다.
* 전역 상태가 아닌 값은 Zustand에 넣지 않는다.
* 입력값은 React Hook Form과 Zod로 검증한다.
* 페이지 컴포넌트에 비즈니스 로직을 집중시키지 않는다.
* 로딩, 빈 상태, 오류 상태를 모두 구현한다.
* 모바일 화면을 고려한다.
* API URL을 하드코딩하지 않는다.

### Backend

* Router, Service, Repository 책임을 구분한다.
* Router에 비즈니스 로직을 직접 작성하지 않는다.
* Pydantic Schema와 SQLAlchemy Model을 구분한다.
* 모든 사용자 데이터 조회에 사용자 소유권 검사를 적용한다.
* 요청과 응답 타입을 명확하게 정의한다.
* 트랜잭션 실패 시 rollback을 보장한다.
* API 오류는 공통 예외 구조를 사용한다.
* 비밀번호, 토큰, API Key를 로그에 출력하지 않는다.
* 비동기 함수 안에서 동기식 고비용 작업을 직접 실행하지 않는다.

## 9. 데이터베이스 규칙

* 모든 테이블은 명확한 Primary Key를 가진다.
* 사용자 소유 데이터는 `user_id`를 가진다.
* 외래키와 삭제 정책을 명시한다.
* 날짜와 시간은 UTC 기준으로 저장한다.
* 화면에서 사용자 타임존으로 변환한다.
* 생성일과 수정일을 관리한다.
* 상태값은 문자열을 자유 입력하지 않고 Enum 또는 제한된 값으로 관리한다.
* 개인정보와 인증정보를 일반 로그에 남기지 않는다.
* 스키마 변경은 Alembic migration으로 관리한다.
* migration 없이 운영 테이블을 직접 변경하지 않는다.

데이터베이스 변경 시 다음을 확인한다.

* 기존 데이터 호환성
* nullable 여부
* default 값
* index 필요 여부
* unique 제약조건
* foreign key
* cascade 정책
* rollback 가능 여부

## 10. API 규칙

Base URL:

```text
/api/v1
```

REST 원칙을 따른다.

공통 응답 구조:

```json
{
  "success": true,
  "data": {},
  "message": "요청이 정상적으로 처리되었습니다."
}
```

공통 오류 구조:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "오류 메시지"
  }
}
```

API 작성 시 다음을 준수한다.

* API 명세서와 경로를 일치시킨다.
* 적절한 HTTP Method를 사용한다.
* 적절한 HTTP Status Code를 반환한다.
* 목록 API는 페이지네이션을 고려한다.
* 검색, 필터, 정렬 파라미터를 명확히 정의한다.
* 사용자 권한 검사를 수행한다.
* 내부 예외 메시지를 그대로 사용자에게 노출하지 않는다.
* 기존 API의 응답 구조를 임의로 변경하지 않는다.

## 11. 인증 및 보안 규칙

* 비밀번호는 안전한 해시 알고리즘으로 저장한다.
* JWT Secret을 코드에 하드코딩하지 않는다.
* Access Token과 Refresh Token을 구분한다.
* 사용자 입력값을 검증한다.
* 파일 업로드 시 확장자만 신뢰하지 않는다.
* 파일 크기를 제한한다.
* 업로드 파일명을 그대로 저장 경로로 사용하지 않는다.
* SQL Injection, XSS, CSRF 가능성을 검토한다.
* 외부 URL 요청 시 SSRF 가능성을 검토한다.
* OAuth Token을 로그에 남기지 않는다.
* OpenAI API Key와 Google OAuth Secret을 저장소에 포함하지 않는다.
* `.env` 파일을 커밋하지 않는다.
* 예제 환경변수는 `.env.example`로 관리한다.

## 12. AI 기능 규칙

AI가 사용자의 실제 경험에 없는 내용을 생성하지 않도록 한다.

지원 문서 생성 시 다음 데이터를 근거로 사용한다.

* 사용자 커리어 프로필
* 등록된 경력
* 등록된 프로젝트
* 등록된 기술
* 업로드한 이력서
* 사용자가 확인한 사실 정보

AI 생성 결과에는 가능한 경우 근거 정보를 함께 저장한다.

근거가 부족한 경우 다음과 같이 처리한다.

* 내용을 만들어내지 않는다.
* 사용자 확인이 필요함을 표시한다.
* 구체적인 수치나 성과를 임의로 생성하지 않는다.
* 합격 가능성을 확정적으로 표현하지 않는다.
* 기업 인재상을 사실처럼 추정하지 않는다.

프롬프트는 코드 내부에 중복 작성하지 않고 별도 템플릿으로 관리한다.

AI 응답은 반드시 구조화된 형식으로 검증한다.

## 13. 채용공고 수집 규칙

* 사이트 이용약관과 robots 정책을 고려한다.
* 무단 대규모 크롤링을 기본 기능으로 구현하지 않는다.
* 공식 API, RSS, 사용자 입력, 이메일 연동을 우선한다.
* 동일 공고 중복 여부를 검사한다.
* 공고 원문 URL과 수집 시점을 저장한다.
* 공고의 마감일이 명확하지 않으면 확정값으로 저장하지 않는다.
* 예상 일정과 확정 일정을 구분한다.

## 14. 일정 관리 규칙

일정 신뢰도는 다음 값으로 구분한다.

```text
CONFIRMED
ESTIMATED
USER_INPUT
```

* 공고에 명시된 일정은 `CONFIRMED`
* 시스템이 추정한 일정은 `ESTIMATED`
* 사용자가 직접 입력한 일정은 `USER_INPUT`

예상 일정을 확정 일정처럼 표시하지 않는다.

Google Calendar 등록 전 사용자의 연결 상태와 권한을 확인한다.

외부 캘린더 동기화 실패가 내부 일정 저장 실패로 이어지지 않도록 처리한다.

## 15. 테스트 규칙

기능 구현 후 관련 테스트를 작성하거나 수정한다.

### Backend

* 단위 테스트
* Service 테스트
* API 테스트
* 인증 및 권한 테스트
* 잘못된 입력값 테스트
* 존재하지 않는 리소스 테스트
* 사용자 소유권 테스트

### Frontend

* 컴포넌트 테스트
* 폼 검증 테스트
* 로딩 및 오류 상태 테스트
* 주요 사용자 흐름 테스트

### 필수 검증

* Backend test
* Frontend lint
* Frontend type check
* Frontend build
* Docker Compose 설정 검증
* migration 적용 검증

테스트를 통과시키기 위해 테스트를 삭제하거나 검증 수준을 낮추지 않는다.

실행할 수 없는 검증 항목은 실행하지 못한 이유를 최종 보고에 기록한다.

## 16. 환경변수 규칙

환경변수 예시:

```text
DATABASE_URL
REDIS_URL
JWT_SECRET_KEY
JWT_REFRESH_SECRET_KEY
OPENAI_API_KEY
GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI
FRONTEND_URL
BACKEND_URL
```

* 운영 값은 저장소에 커밋하지 않는다.
* `.env.example`에는 변수명과 예시 형식만 기록한다.
* 환경변수가 없을 때 명확한 오류를 발생시킨다.
* 비밀값에 임의 기본값을 사용하지 않는다.

## 17. 완료 기준

작업은 다음 조건을 충족해야 완료된 것으로 본다.

* 요청 기능 구현
* 관련 테스트 작성 또는 수정
* 관련 테스트 통과
* lint 및 build 통과
* API 변경 시 API 문서 수정
* DB 변경 시 migration 작성
* 환경변수 변경 시 `.env.example` 수정
* 불필요한 파일 변경 없음
* 임시 코드와 디버그 로그 제거
* Git 작업 트리 상태 확인
* 변경 파일과 검증 결과 보고

## 18. 작업 결과 보고 형식

작업 완료 후 다음 형식으로 보고한다.

```text
작업 요약
- 구현한 기능

변경 파일
- 수정 또는 생성한 주요 파일

API 변경
- 추가 또는 변경된 API

DB 변경
- 추가된 테이블, 컬럼, migration

검증 결과
- backend test
- frontend lint
- frontend type check
- frontend build
- docker compose config

미검증 항목
- 실행하지 못한 검증과 이유

주의사항
- 남은 문제
- 운영 반영 시 필요한 설정

Git 상태
- 현재 브랜치
- 커밋 해시
- 작업 트리 상태
```

## 19. 금지 명령

사용자의 명시적인 요청 없이 다음 명령을 실행하지 않는다.

```text
git reset --hard
git clean -fd
git push --force
git rebase
git checkout -- .
git restore .
docker system prune
docker volume prune
DROP DATABASE
DROP TABLE
rm -rf
```

데이터를 삭제하거나 복구가 어려운 명령은 반드시 실행 전에 사용자 승인을 받는다.

## 20. 자동 승인 범위

다음 작업은 자동 진행 가능하다.

* 파일 읽기
* 코드 검색
* 새 브랜치 생성
* 코드 및 문서 수정
* 의존성 설치
* 테스트 실행
* lint 및 build 실행
* Docker 이미지 빌드
* migration 파일 생성
* 로컬 개발 환경 실행
* 커밋 생성

다음 작업은 자동 진행하지 않는다.

* main 병합
* 원격 push
* 태그 생성 및 push
* 운영 서버 배포
* 운영 DB migration
* 데이터 삭제
* 기존 브랜치 삭제
* Secret 변경
* 외부 서비스에서 실제 메일 발송
* Google Calendar 실제 일정 생성
* 유료 API 대량 호출
