# 비기능 요구사항

## 보안

* 비밀번호는 평문으로 저장하지 않는다.
* JWT Secret과 외부 API Key는 저장소에 커밋하지 않는다.
* Refresh Token 원문은 DB에 저장하지 않는다.
* 인증 오류는 공격자가 계정 존재 여부를 추론하기 어렵게 처리한다.
* 내부 예외 메시지, SQL 오류, Secret 값은 API 응답에 노출하지 않는다.
* 운영 환경에서는 HTTPS와 `COOKIE_SECURE=true`를 사용한다.

## 개인정보

* 사용자 이메일, 경력, 프로젝트, 이력서 정보는 개인정보로 취급한다.
* 로그에는 비밀번호, 토큰, API Key, OAuth Token을 남기지 않는다.
* AI 생성 결과는 사용자 실제 경험을 근거로 해야 한다.
* 사용자가 제공하지 않은 성과, 수치, 경험을 임의로 생성하지 않는다.

## 가용성

* Health API는 Backend, Database, Redis 상태를 확인할 수 있어야 한다.
* PostgreSQL 또는 Redis 연결 실패 시 서비스 전체가 불필요하게 민감정보를 노출하지 않는다.
* 외부 API 연동 실패가 내부 데이터 저장 실패로 이어지지 않도록 설계한다.

## 성능

* 일반 API 응답은 로컬 개발 환경 기준 1초 이내를 목표로 한다.
* 대용량 문서 파싱, AI 분석, 추천 계산은 향후 비동기 작업으로 분리한다.
* 목록 API는 페이지네이션을 고려한다.

## 유지보수성

* Backend는 Router, Service, Repository, Schema, Model 책임을 분리한다.
* Frontend는 페이지, 컴포넌트, API client, 타입을 분리한다.
* API와 DB 변경 시 관련 문서를 함께 갱신한다.
* migration은 upgrade와 downgrade를 모두 제공한다.

## 확장성

* AI 분석 기능은 별도 서비스 계층으로 확장할 수 있게 설계한다.
* Redis는 캐시와 비동기 작업 queue 확장에 사용할 수 있다.
* PostgreSQL pgvector는 의미 기반 검색이 필요한 시점에 도입한다.

## 테스트

* Backend 기능은 Pytest로 검증한다.
* Frontend는 최소 lint, type-check, production build를 통과해야 한다.
* Docker Compose config와 실행 가능성을 검증한다.
* DB 변경은 Alembic upgrade/downgrade를 검증한다.
