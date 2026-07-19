# 문서 불일치 점검 보고서

## 점검 기준

- 기준 branch: `main`
- 기준 commit: `8d003c3`
- 기준 tag: `v0.2.2`
- 점검 대상: Git log, tag, PR #1~#6, Markdown 문서, Alembic migration, Backend router, DB model, Frontend App Router, `.env.example`, tests

## 누락된 버전 문서

기존에는 다음 버전에 대한 상세 문서가 충분하지 않았다.

- v0.1.4 계정 보안·복구
- v0.2.1 AI 채용공고 분석
- v0.2.2 사용자-공고 적합도 분석

조치: `docs/11_releases/`에 v0.1.0~v0.2.2 상세 문서를 모두 생성했다.

## 완료 상태 불일치

기존 로드맵 일부는 예정/완료 상태가 섞여 있었다. v0.2.2 기준으로 v0.1.0~v0.2.2는 완료, v0.3.x 이후는 예정으로 재정리했다.

## 중복된 버전

기존 `version-roadmap.md`에는 v0.2.1 상세 내용이 중복으로 존재했다. 조치: 로드맵을 단일 버전 항목만 갖도록 재작성했다.

## 코드에는 있지만 문서가 부족했던 기능

- v0.1.4 이메일 인증/비밀번호 복구/세션/보안 이벤트
- v0.2.1 AI Provider와 job analysis run
- v0.2.2 job matching과 feedback

조치: 릴리즈 문서, API 문서, DB 문서, 상태 문서에 반영했다.

## 문서에는 있지만 코드에 없는 기능

다음은 아직 구현되지 않았거나 제외/보류로 분리해야 한다.

- 이력서 업로드/분석
- 자기소개서 생성
- 지원 현황 관리
- 일정/Google Calendar 연동
- Gmail 채용 메일 분석
- 자동 추천
- pgvector 기반 추천
- Celery 기반 비동기 queue

조치: `excluded-features.md`, `deferred-features.md`, `future-detailed-plan.md`에 분리했다.

## 오래된 API 설명

기존 API 문서는 인코딩이 깨진 부분과 버전별 연결 부족이 있었다. 조치: 실제 router 기준으로 `docs/04_api/api-specification.md`를 재작성했다.

## 오래된 DB 구조

기존 DB 문서는 v0.2.2 최신 테이블을 한 번에 보기 어려웠다. 조치: `docs/06_database/database-design.md`와 `docs/06_database/erd.md`를 최신 모델 기준으로 재작성했다.

## 잘못된 Frontend 경로

현재 App Router 기준 실제 경로는 다음이다.

```text
/
/signup
/login
/auth/callback
/me
/profile
/jobs
/jobs/new
/jobs/{jobId}
/settings/accounts
/settings/security
/verify-email
/forgot-password
/reset-password
```

조치: navigation 문서를 최신 경로 기준으로 정리했다.

## 조치 결과

- 상태 문서 생성
- 릴리즈 상세 문서 생성
- API/DB/ERD/navigation 문서 정렬
- 미검증/제외/보류/기술부채 문서 분리
- README와 docs index 최신화
