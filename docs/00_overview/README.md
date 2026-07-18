# ApplyMate AI 개요

ApplyMate AI는 개인용 AI 취업 매니저다. 사용자의 경력, 기술, 프로젝트 경험, 희망 직무와 조건을 기반으로 채용공고를 관리하고, 지원 전략과 자기소개서 작성을 돕는 웹 서비스로 발전시킨다.

## 해결하려는 문제

취업 준비 과정에서는 공고 탐색, 조건 비교, 지원서 작성, 일정 관리가 여러 도구에 흩어진다. ApplyMate AI는 이 과정을 하나의 흐름으로 묶어 사용자가 다음 지원 행동을 빠르게 결정하도록 돕는다.

## 핵심 가치

* 사용자의 실제 경험을 기준으로 지원 전략을 만든다.
* 채용공고와 사용자 프로필의 적합도를 구조적으로 비교한다.
* 지원 일정과 상태를 한곳에서 관리한다.
* AI 생성 결과에는 가능한 경우 근거 데이터를 연결한다.
* 예상 정보와 확정 정보를 구분해 과도한 단정을 피한다.

## 현재 버전

현재 구현 버전은 `v0.1.1`이다.

구현된 범위:

* 프로젝트 기본 실행 환경
* Backend Health API
* Frontend 서비스 상태 화면
* 이메일 회원가입 및 로그인
* JWT Access Token
* HttpOnly Cookie Refresh Token
* Refresh Token 저장, 재발급, 폐기
* 현재 로그인 사용자 조회
* 인증 관련 DB migration

## 목표 사용자

* 신입 및 주니어 개발자
* 직무 전환 준비자
* 여러 기업에 동시에 지원하는 취업 준비생
* 경력직 이직 준비자

## 문서 읽기 순서

1. `docs/00_overview/README.md`
2. `docs/01_planning/project-plan.md`
3. `docs/01_planning/service-scope.md`
4. `docs/02_technical/system-architecture.md`
5. `docs/03_requirements/functional-specification.md`
6. `docs/04_api/api-specification.md`
7. `docs/05_development-plan/version-roadmap.md`
