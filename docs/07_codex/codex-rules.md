# Codex 작업 규칙

이 문서는 ApplyMate AI에서 Codex가 작업할 때 따라야 하는 실무 규칙을 요약한다. 상세 규칙은 루트 `AGENTS.md`를 우선한다.

## 작업 전 확인

* 현재 브랜치
* Git 작업 트리 상태
* 관련 문서
* 관련 코드
* 테스트 구조
* 환경변수와 Secret 처리

## 문서 우선

기능 구현 전 다음 문서를 확인한다.

* `docs/01_planning/project-plan.md`
* `docs/02_technical/tech-stack.md`
* `docs/03_requirements/functional-specification.md`
* `docs/04_api/api-specification.md`
* `docs/05_development-plan/version-roadmap.md`

문서와 코드가 충돌하면 문서를 기준으로 하되, 문서끼리 충돌하면 충돌 내용을 보고한다.

## 코드 변경 원칙

* 요청 범위만 변경한다.
* 관련 없는 리팩터링을 하지 않는다.
* API 변경 시 API 문서를 수정한다.
* DB 변경 시 migration과 DB 문서를 수정한다.
* 환경변수 변경 시 `.env.example`과 운영 문서를 수정한다.
* 테스트를 통과시키기 위해 기능이나 테스트를 삭제하지 않는다.

## 보안 원칙

* Secret을 커밋하지 않는다.
* 비밀번호와 토큰을 로그에 남기지 않는다.
* Refresh Token 원문을 DB에 저장하지 않는다.
* 외부 서비스 호출은 사용자의 승인 범위 안에서만 수행한다.

## 완료 보고

완료 보고에는 다음을 포함한다.

* 작업 요약
* 변경 파일
* API 변경
* DB 변경
* 검증 결과
* 미검증 항목
* 주의사항
* Git 상태
