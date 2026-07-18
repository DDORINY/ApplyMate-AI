# ApplyMate AI 버전별 개발 로드맵

## 버전 요약

```text
v0.1.x: 서비스 기반 구축
v0.2.x: 채용공고 관리와 적합도 분석
v0.3.x: 이력서 분석과 AI 지원 문서
v0.4.x: 지원 현황과 일정 관리
v0.5.x: 외부 서비스 연동
v0.6.x: 자동 추천 시스템
v1.0.0: 정식 MVP
```

## v0.1.0 프로젝트 기반 구축

상태: 완료

- Next.js 프론트엔드
- FastAPI 백엔드
- PostgreSQL, Redis 연결
- Docker Compose 개발 환경
- Health API
- 공통 응답/오류 구조

## v0.1.1 회원 및 인증

상태: 완료

- 이메일 회원가입
- 이메일 로그인
- JWT Access Token
- Refresh Token HttpOnly Cookie
- Refresh Token DB hash 저장, rotation, 폐기
- 현재 사용자 조회
- 로그아웃
- 회원가입/로그인/보호 페이지
- 인증 테스트와 문서 갱신

## v0.1.2 커리어 프로필

상태: 완료

- 기본 커리어 프로필 관리
- 기술 스택 관리
- 경력 관리
- 프로젝트 관리
- 프로젝트-기술 연결
- 희망 근무 조건 관리
- 지원 제외 조건 관리
- 포트폴리오 URL 관리
- 사용자 소유권 검증
- URL, 날짜, Enum, 중복 입력 검증
- `/profile` 프론트엔드 화면
- Alembic migration과 Backend 테스트

## v0.1.3 소셜 로그인

상태: 완료

구현 범위:

- Google OAuth 로그인
- GitHub OAuth 로그인
- OAuth provider 활성화 상태 API
- OAuth authorize URL 생성 API
- Provider callback 처리
- 1회용 OAuth login ticket 교환 API
- 소셜 로그인 사용자 생성
- 기존 이메일 계정과 동일 이메일 소셜 계정의 자동 병합 방지
- 로그인 후 명시적 소셜 계정 연결
- 연결된 소셜 계정 조회/해제
- 마지막 로그인 수단 해제 방지
- `email_verified`, nullable `password_hash`
- `oauth_accounts`, `oauth_states`, `oauth_login_tickets`
- `/auth/callback`, `/settings/accounts` 프론트 화면
- OAuth 테스트, migration, 문서 업데이트

제외 범위:

- Kakao/Naver/Apple 로그인
- Google Calendar/Gmail 연동
- GitHub repository 수집
- provider access token 저장
- production OAuth app 생성/배포

## v0.1.4 계정 보안·복구

상태: 완료

구현 범위:

- 이메일 인증 발송, 재발송, 검증
- 비밀번호 찾기와 재설정
- 로그인 사용자 비밀번호 변경
- 소셜 로그인 사용자 비밀번호 설정
- refresh token 기반 세션/기기 관리
- 개별 세션 로그아웃, 다른 모든 세션 로그아웃, 전체 세션 로그아웃
- 로그인 실패 횟수 제한
- 보안 이벤트 기록
- 개발용 이메일 발송 Adapter와 SMTP 설정 문서
- 계정 보안/복구 프론트 화면

제외 범위:

- 이메일 주소 변경
- 회원 탈퇴
- TOTP 2단계 인증
- SMS 인증
- WebAuthn
- 실제 SMTP 계정 생성 또는 운영 메일 발송
- 운영 배포와 운영 DB migration

## v0.2.0 채용공고 관리

상태: 예정

목표:

- 사용자가 채용공고를 직접 등록하고 관리합니다.
- 이후 적합도 분석에 사용할 구조화된 공고 데이터를 저장합니다.

예정 범위:

- 채용공고 직접 등록
- URL 기반 공고 등록 준비
- 공고 목록/상세 조회
- 공고 수정/삭제
- 공고 상태 관리
- 기업 정보 저장
- 중복 공고 감지 기준 설계

## v0.2.1 AI 채용공고 분석

상태: 예정

- 공고 본문 전처리
- 주요 업무 추출
- 필수/우대 조건 추출
- 기술 스택 추출
- 경력 조건 추출
- 채용 절차와 마감일 추출

## v0.2.2 사용자-공고 적합도 분석

상태: 예정

- 직무 적합도 계산
- 기술 적합도 계산
- 경력 적합도 계산
- 프로젝트 적합도 계산
- 지원 위험 요소 표시
- 강점/보완점 표시

## v0.3.x 이력서/AI 문서

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

완료 조건:

- 회원, 프로필, 공고, 분석, 문서, 지원 현황, 일정 관리 흐름 통합
- 주요 기능 통합 테스트 완료
- 개인정보/권한 정책 점검
- 운영 배포 문서 정리
