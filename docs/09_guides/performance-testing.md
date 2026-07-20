# Performance Testing Guide

## 목적

v0.9.0 성능 검증은 병목 후보를 기록하고, v1.0.0 이전에 대량 목록 API와 대시보드 조회의 기준선을 만드는 것을 목표로 한다.

## 우선 대상

- `GET /api/v1/dashboard`
- `GET /api/v1/jobs`
- `GET /api/v1/applications`
- `GET /api/v1/calendar/events`
- `GET /api/v1/recommendations/jobs`
- `GET /api/v1/notifications`

## 로컬 기준 목표

- 일반 목록 API p95: 500ms 미만
- 상세 API p95: 300ms 미만
- 대시보드 p95: 800ms 미만
- 오류율: 1% 미만

실행하지 않은 수치는 완료로 표시하지 않는다. 테스트 머신, Docker project, 데이터 건수, provider mock 여부를 함께 기록한다.

## DB 점검

- pagination 조건과 정렬 컬럼을 확인한다.
- `user_id`, `status`, `created_at`, `scheduled_at`, `job_id`, `application_id`, `document_id` 조건을 우선 점검한다.
- `EXPLAIN ANALYZE` 결과는 운영 데이터가 아닌 테스트 데이터 기준임을 명시한다.
