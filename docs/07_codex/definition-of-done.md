# Definition of Done

ApplyMate AI 작업은 다음 조건을 만족해야 완료로 본다.

## 공통 완료 조건

* 요청된 범위가 구현되어 있다.
* 관련 문서가 최신 상태다.
* 불필요한 파일 변경이 없다.
* Secret, 토큰, 비밀번호가 저장소에 포함되지 않는다.
* Git 작업 트리가 의도한 변경만 포함한다.

## Backend

* API 응답이 공통 응답 구조를 따른다.
* 오류 응답이 공통 오류 구조를 따른다.
* Router, Service, Repository, Schema, Model 책임이 분리되어 있다.
* DB 변경이 Alembic migration으로 관리된다.
* migration은 upgrade와 downgrade를 제공한다.
* 관련 Pytest가 통과한다.
* Ruff 검사가 통과한다.

## Frontend

* TypeScript 검사에 통과한다.
* ESLint 검사에 통과한다.
* production build에 통과한다.
* 로딩, 오류, 성공 상태를 고려한다.
* API Base URL을 하드코딩하지 않는다.
* 입력 폼은 검증 메시지를 제공한다.

## Docker 및 운영

* `docker compose config`가 통과한다.
* 필요한 경우 `docker compose up --build -d`가 정상 실행된다.
* 컨테이너 종료 시 volume을 임의로 삭제하지 않는다.
* 운영 배포는 별도 승인 없이 수행하지 않는다.

## 문서

* 기능명세서와 실제 구현이 일치한다.
* API 명세서와 실제 endpoint가 일치한다.
* DB 문서와 migration이 일치한다.
* README에 실행 방법과 현재 구현 범위가 반영되어 있다.
