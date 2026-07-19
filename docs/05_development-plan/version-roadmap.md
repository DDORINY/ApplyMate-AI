# ApplyMate AI 버전별 개발 로드맵

## 버전 요약

```text
v0.1.x: 서비스 기반 구축
v0.2.x: 채용공고 관리와 공고/사용자 분석
v0.3.x: 이력서 분석과 AI 지원 문서
v0.4.x: 지원 현황과 일정 관리
v0.5.x: 외부 서비스 연동
v0.6.x: 자동 추천 시스템
v1.0.0: MVP 안정화
```

## v0.1.0 프로젝트 기반 구축

상태: 완료

- Next.js 프론트엔드
- FastAPI 백엔드
- PostgreSQL, Redis, Docker Compose
- Health API
- 공통 응답/오류 구조

## v0.1.1 회원 및 인증

상태: 완료

- 이메일 회원가입/로그인
- JWT Access Token
- Refresh Token HttpOnly Cookie, DB hash 저장, rotation/revocation
- 현재 사용자 조회, 로그아웃
- 회원가입/로그인 화면

## v0.1.2 커리어 프로필

상태: 완료

- 커리어 프로필, 기술 스택, 경력, 프로젝트 관리
- 프로젝트-기술 연결
- 희망 근무 조건, 지원 제외 조건, 포트폴리오 링크
- 사용자 소유권 검증
- `/profile` 화면

## v0.1.3 소셜 로그인

상태: 완료

- Google/GitHub OAuth 로그인
- OAuth authorize/callback/ticket exchange
- 기존 이메일 계정과 소셜 계정의 명시적 연결
- 연결된 소셜 계정 조회/해제
- `/auth/callback`, `/settings/accounts` 화면

## v0.1.4 계정 보안·복구

상태: 완료

- 이메일 인증
- 비밀번호 찾기/재설정
- 비밀번호 변경/설정
- 로그인 세션 관리
- 보안 이벤트 기록
- 로그인 실패 제한

## v0.2.0 채용공고 관리

상태: 완료

- 채용공고 직접 등록
- URL 기반 채용공고 등록
- 채용공고 목록/상세/수정/삭제
- 채용공고 상태, 관심 공고 관리
- 기업 정보 저장 및 재사용
- 중복 공고 감지
- SSRF 방어와 URL 수집 제한
- `/jobs`, `/jobs/new`, `/jobs/{jobId}` 화면

## v0.2.1 AI 채용공고 분석

상태: 완료

- 채용공고 본문 전처리와 분석 입력 hash 생성
- AI Provider 추상화: `disabled`, `mock`, `openai`
- 주요 업무, 필수/우대 조건, 기술 스택, 경력/학력, 채용 절차, 마감 정보, 키워드 추출
- `job_analyses`, `job_analysis_runs` 기반 현재 분석 결과와 실행 이력 저장
- 분석 실패, 재분석, 중복 실행 방지, 일일 한도와 cooldown 처리
- 공고 변경 시 `is_outdated` 표시
- 사용자 검토 수정/삭제 API
- `/jobs/{jobId}` 상세 화면의 AI 분석 패널

## v0.2.2 사용자-공고 적합도 분석

상태: 완료

- 커리어 프로필, 기술, 경력, 프로젝트, 희망 조건, 지원 제외 조건과 완료된 공고 분석 결과 비교
- 규칙 기반 deterministic 점수 계산
- 점수 가중치: 직무 25%, 기술 30%, 경력 15%, 프로젝트 15%, 희망 조건 10%, 위험/제외 조건 5%
- 등급: `EXCELLENT`, `GOOD`, `MODERATE`, `LOW`, `VERY_LOW`
- 추천 상태: `STRONGLY_RECOMMENDED`, `RECOMMENDED`, `CONSIDER`, `NOT_RECOMMENDED`, `INSUFFICIENT_DATA`
- `job_matches`, `job_match_runs`, `job_match_feedback` 저장
- 최신 프로필/공고 분석 hash 기반 `is_outdated` 표시
- AI Provider가 `disabled`여도 template 설명으로 동작
- `/jobs/{jobId}` 상세 화면의 적합도 분석 패널과 피드백 입력

제외 범위:

- 점수 자체를 AI가 변경하는 기능
- 여러 공고의 적합도 일괄 재계산
- 적합도 점수 기반 자동 추천 피드 반영
- 지원서/자기소개서 생성

## v0.3.x 이력서와 AI 문서

상태: 예정

- PDF/DOCX 이력서 업로드
- 이력서 텍스트 추출
- 경력/프로젝트 자동 추출
- 지원 동기, 직무 역량, 자기소개 문서 생성
- 근거 기반 문장 생성과 검증

## v0.4.x 지원 현황과 일정

상태: 예정

- 지원 공고 등록
- 지원 상태 관리
- 서류/면접/과제/마감 일정 관리
- 캘린더 UI

## v0.5.x 외부 서비스 연동

상태: 예정

- Google Calendar 연동
- Gmail 채용 메일 분석
- 외부 계정 연결/해제
- 동기화 로그

## v0.6.x 자동 추천

상태: 예정

- 매일 추천 공고 생성
- 사용자 조건 기반 필터링
- 적합도 기반 정렬
- 피드백 반영

## v1.0.0 MVP

상태: 예정

- 회원, 프로필, 공고, 분석, 문서, 지원 현황, 일정 관리 흐름 통합
- 주요 기능 통합 테스트
- 개인정보/권한 정책 점검
- 운영 배포 문서 정리
