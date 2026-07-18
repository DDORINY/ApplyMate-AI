# Codex 작업 요청 템플릿

## 1. 작업 정보

### 작업명

```text
예: v0.1.1 회원가입 및 로그인 구현
```

### 대상 버전

```text
v0.1.1
```

### 작업 유형

```text
기능 구현 / 버그 수정 / 리팩터링 / 문서 수정 / 테스트
```

## 2. 작업 목표

이번 작업에서 반드시 완료해야 할 목표를 작성한다.

```text
예:
이메일과 비밀번호를 사용하는 회원가입 및 로그인 기능을 구현한다.
JWT Access Token과 Refresh Token을 발급하고 인증이 필요한 API에
사용자 인증을 적용한다.
```

## 3. 참고 문서

작업 전 다음 문서를 확인한다.

```text
- AGENTS.md
- docs/01_planning/project-plan.md
- docs/02_technical/tech-stack.md
- docs/03_requirements/functional-specification.md
- docs/04_api/api-specification.md
- docs/05_development-plan/version-roadmap.md
```

추가 참고 문서:

```text
- 관련 문서 경로
```

## 4. 구현 범위

### Backend

```text
- 구현할 API
- Service
- Repository
- Schema
- Model
- 인증 및 권한
```

### Frontend

```text
- 구현할 페이지
- 컴포넌트
- API 연결
- 입력 검증
- 상태 관리
```

### Database

```text
- 생성할 테이블
- 추가할 컬럼
- index
- foreign key
- migration
```

### Document

```text
- 수정할 문서
```

## 5. 제외 범위

이번 작업에서 구현하지 않을 항목을 명시한다.

```text
예:
- 소셜 로그인
- 비밀번호 찾기
- 이메일 인증
- 관리자 기능
- Google OAuth
```

제외 범위는 선행 구현하지 않는다.

## 6. 세부 요구사항

```text
1. 이메일은 중복 등록할 수 없다.
2. 비밀번호는 평문으로 저장하지 않는다.
3. 로그인 실패 시 이메일 존재 여부를 노출하지 않는다.
4. Access Token과 Refresh Token을 분리한다.
5. 인증 오류는 공통 오류 응답 형식을 사용한다.
6. 사용자별 데이터 접근 권한을 검사한다.
```

## 7. API 요구사항

```text
POST /api/v1/auth/signup
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
GET  /api/v1/auth/me
```

API 응답은 `docs/04_api/api-specification.md`를 따른다.

기존 API 경로와 응답 구조를 임의로 변경하지 않는다.

## 8. UI 요구사항

```text
- 로딩 상태 표시
- API 오류 표시
- 입력값 검증 메시지 표시
- 모바일 화면 대응
- 비밀번호 입력값 숨김 처리
```

## 9. 보안 요구사항

```text
- 비밀번호 해시 저장
- Secret 환경변수 처리
- 민감정보 로그 출력 금지
- 인증 실패 메시지 통일
- 사용자 입력값 검증
```

## 10. 테스트 요구사항

다음 테스트를 작성한다.

```text
- 정상 회원가입
- 중복 이메일 회원가입 실패
- 정상 로그인
- 잘못된 비밀번호 로그인 실패
- 유효하지 않은 토큰 접근 실패
- 인증 사용자 정보 조회 성공
- Refresh Token 재발급
```

## 11. 검증 명령

프로젝트에 정의된 실제 명령을 확인한 후 실행한다.

예시:

```bash
# Backend
pytest

# Frontend
npm run lint
npm run type-check
npm run build

# Docker
docker compose config
docker compose build
```

존재하지 않는 명령을 임의로 가정하지 않는다.

## 12. Git 작업 규칙

```text
브랜치:
feature/v0.1.1-auth

커밋 예시:
feat: add jwt authentication
test: add authentication api tests
docs: update authentication api specification
```

사용자의 별도 요청이 없다면 다음은 수행하지 않는다.

* main 병합
* 원격 push
* 태그 생성
* 운영 배포

## 13. 완료 조건

```text
- 요구 기능 구현
- 테스트 작성
- 테스트 통과
- lint 통과
- type check 통과
- build 통과
- API 문서 수정
- migration 작성
- .env.example 수정
- 작업 트리 확인
```

## 14. 최종 보고

작업 완료 후 다음을 보고한다.

```text
1. 구현 내용
2. 변경 파일
3. API 변경
4. DB 변경
5. 테스트 결과
6. 빌드 결과
7. 실행하지 못한 검증
8. 주의사항
9. 현재 브랜치
10. 커밋 해시
11. 작업 트리 상태
```
