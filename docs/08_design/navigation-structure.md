# 내비게이션 구조

ApplyMate AI의 화면 이동 구조를 정리합니다. 이 문서는 실제 구현된 프론트 화면과 다음 버전에서 확장할 화면 후보를 함께 관리합니다.

## 1. 현재 구현 화면

v0.1.2 기준으로 실제 구현된 화면은 다음과 같습니다.

| 경로 | 화면 이름 | 접근 | 상태 | 역할 |
| --- | --- | --- | --- | --- |
| `/` | 홈 | 공개 | 완료 | 서비스 상태 확인과 주요 화면 진입 |
| `/signup` | 회원가입 | 공개 | 완료 | 이메일 기반 계정 생성 |
| `/login` | 로그인 | 공개 | 완료 | Access Token/Refresh Token 발급 |
| `/me` | 내 계정 | 인증 필요 | 완료 | 현재 로그인 사용자 정보 확인 |
| `/profile` | 커리어 프로필 | 인증 필요 | 완료 | 프로필, 기술, 경력, 프로젝트, 선호 조건 관리 |

## 2. 공통 내비게이션

모든 주요 화면은 같은 상단 내비게이션을 사용합니다.

```text
ApplyMate AI
홈 | 회원가입 | 로그인 | 내 계정 | 프로필
```

내비게이션 원칙:

- 사용자는 어느 화면에서든 홈으로 돌아갈 수 있어야 합니다.
- 인증 관련 화면(`/signup`, `/login`)은 서로 이동할 수 있어야 합니다.
- 보호 화면(`/me`, `/profile`)은 로그인하지 않은 경우 로그인 화면으로 이동합니다.
- 현재 구현 범위를 벗어난 메뉴는 아직 노출하지 않습니다.

## 3. 홈 화면

경로: `/`

홈 화면은 서비스의 현재 상태와 핵심 진입점을 제공합니다.

구성:

- 제품명과 현재 버전
- v0.1.2에서 가능한 작업 설명
- 회원가입, 로그인, 내 계정, 프로필 버튼
- Frontend, Backend, Database, Redis 상태 패널

## 4. 인증 화면

### 회원가입

경로: `/signup`

입력 항목:

- 이름
- 이메일
- 비밀번호
- 비밀번호 확인

완료 후 로그인 화면으로 이동합니다.

### 로그인

경로: `/login`

입력 항목:

- 이메일
- 비밀번호

완료 후 내 계정 화면으로 이동합니다.

## 5. 내 계정 화면

경로: `/me`

역할:

- 현재 로그인 사용자 이름과 이메일 확인
- 계정 상태 확인
- 최근 로그인 시각 확인
- 로그아웃
- 커리어 프로필 화면으로 이동

인증되지 않은 사용자는 `/login`으로 이동합니다.

## 6. 커리어 프로필 화면

경로: `/profile`

v0.1.2 범위는 한 화면 안에서 카드형 섹션으로 관리합니다.

섹션:

1. 기본 프로필
2. 기술 스택
3. 경력
4. 프로젝트
5. 희망 조건
6. 지원 제외 조건
7. 포트폴리오 링크

화면 원칙:

- 모바일에서는 세로 스크롤 중심으로 사용합니다.
- 각 섹션은 독립적인 저장/추가/삭제 흐름을 가집니다.
- 삭제 작업은 사용자 확인 후 실행합니다.
- 입력 검증은 프론트엔드 Zod와 백엔드 Pydantic에서 함께 처리합니다.
- 인증 만료 시 기존 Refresh Token 흐름을 재사용합니다.

## 7. v0.1.2에서 노출하지 않는 화면

다음 화면은 아직 구현 범위가 아니므로 내비게이션에 노출하지 않습니다.

- 채용공고 관리
- 적합도 분석
- 이력서 업로드
- AI 지원 문서
- 지원 현황
- 캘린더
- 외부 연동 설정

## 8. 향후 화면 후보

| 버전 | 화면 후보 | 목적 |
| --- | --- | --- |
| v0.2.0 | `/jobs`, `/jobs/new`, `/jobs/{id}` | 채용공고 관리 |
| v0.2.2 | `/matches`, `/jobs/{id}/matches` | 적합도 분석 |
| v0.3.x | `/resumes`, `/documents` | 이력서와 AI 문서 |
| v0.4.x | `/applications`, `/calendar` | 지원 현황과 일정 |
| v0.5.x | `/settings/integrations` | 외부 서비스 연동 |

## 9. 구현 파일 매핑

| 화면 | 주요 파일 |
| --- | --- |
| 홈 | `frontend/src/app/page.tsx` |
| 회원가입 | `frontend/src/app/signup/page.tsx`, `frontend/src/components/auth/signup-form.tsx` |
| 로그인 | `frontend/src/app/login/page.tsx`, `frontend/src/components/auth/login-form.tsx` |
| 내 계정 | `frontend/src/app/me/page.tsx`, `frontend/src/components/auth/protected-user-panel.tsx` |
| 커리어 프로필 | `frontend/src/app/profile/page.tsx`, `frontend/src/components/profile/profile-manager.tsx` |
| 공통 내비게이션 | `frontend/src/components/app-header.tsx` |
