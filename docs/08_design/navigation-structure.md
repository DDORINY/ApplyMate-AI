# 네비게이션 구조

ApplyMate AI의 화면 이동 구조를 정리합니다. 이 문서는 실제 구현된 프론트 화면과 다음 버전에서 확장될 화면 후보를 함께 관리합니다.

## 현재 구현 화면

v0.1.3 기준 실제 구현된 화면은 다음과 같습니다.

| 경로 | 화면 이름 | 접근 | 상태 | 역할 |
| --- | --- | --- | --- | --- |
| `/` | 홈 | 공개 | 완료 | 서비스 상태 확인과 주요 화면 진입 |
| `/signup` | 회원가입 | 공개 | 완료 | 이메일 계정 생성 및 소셜 로그인 시작 |
| `/login` | 로그인 | 공개 | 완료 | 이메일 로그인 및 소셜 로그인 시작 |
| `/auth/callback` | 소셜 로그인 callback | 공개 | 완료 | OAuth login ticket을 서비스 토큰으로 교환 |
| `/me` | 내 계정 | 인증 필요 | 완료 | 현재 로그인 사용자 정보 확인 |
| `/profile` | 커리어 프로필 | 인증 필요 | 완료 | 프로필, 기술, 경력, 프로젝트, 희망 조건 관리 |
| `/settings/accounts` | 소셜 계정 연결 | 인증 필요 | 완료 | Google/GitHub 계정 연결, 목록 조회, 해제 |

## 공통 네비게이션

모든 주요 화면은 같은 상단 네비게이션을 사용합니다.

```text
ApplyMate AI
홈 | 회원가입 | 로그인 | 내 계정 | 프로필 | 계정 연결
```

정책:

- 공개 화면과 보호 화면을 모두 네비게이션에 표시합니다.
- 보호 화면에서 인증이 없으면 로그인 화면으로 이동합니다.
- v0.1.3 범위를 벗어난 화면은 아직 네비게이션에 노출하지 않습니다.

## 인증 화면

### 회원가입 `/signup`

구성:

- Google/GitHub 소셜 로그인 버튼
- 이메일 회원가입 폼
- 로그인 화면 이동 링크

완료 후:

- 이메일 회원가입 성공 시 `/login`으로 이동합니다.
- 소셜 로그인 성공 시 `/auth/callback`에서 token 교환 후 `/me`로 이동합니다.

### 로그인 `/login`

구성:

- Google/GitHub 소셜 로그인 버튼
- 이메일 로그인 폼
- 회원가입 화면 이동 링크

완료 후:

- 이메일 로그인 성공 시 `/me`로 이동합니다.
- 소셜 로그인 성공 시 `/auth/callback`에서 token 교환 후 `/me`로 이동합니다.

### 소셜 로그인 callback `/auth/callback`

역할:

- URL query의 `ticket`, `error`, `redirect_path`를 읽습니다.
- `ticket`이 있으면 `POST /auth/oauth/exchange`를 호출합니다.
- 교환 성공 시 응답의 `redirect_path`로 이동합니다.
- 오류가 있으면 사용자에게 안내 후 `/login`으로 돌아갈 수 있게 합니다.

## 내 계정 `/me`

역할:

- 이름, 이메일, 계정 상태, 이메일 검증 여부, 최근 로그인 시각 표시
- 프로필 관리 이동
- 소셜 계정 연결 이동
- 로그아웃

## 소셜 계정 연결 `/settings/accounts`

역할:

- 연결된 Google/GitHub 계정 목록 표시
- provider 이메일, username, 최근 사용 시각 표시
- 새 provider 연결 시작
- 연결 해제

정책:

- 마지막 로그인 수단은 해제할 수 없습니다.
- provider access token은 화면이나 DB에 저장/표시하지 않습니다.
- 같은 이메일의 기존 계정과 소셜 계정은 자동 병합하지 않습니다.

## 커리어 프로필 `/profile`

v0.1.2 범위의 단일 화면 안에서 카드형 섹션으로 관리합니다.

섹션:

1. 기본 프로필
2. 기술 스택
3. 경력
4. 프로젝트
5. 희망 조건
6. 지원 제외 조건
7. 포트폴리오 링크

## 아직 노출하지 않는 화면

- 채용공고 관리
- 적합도 분석
- 이력서 업로드
- AI 지원 문서
- 지원 현황
- 캘린더
- 외부 연동 설정

## 향후 화면 후보

| 버전 | 화면 후보 | 목적 |
| --- | --- | --- |
| v0.2.0 | `/jobs`, `/jobs/new`, `/jobs/{id}` | 채용공고 관리 |
| v0.2.2 | `/matches`, `/jobs/{id}/matches` | 적합도 분석 |
| v0.3.x | `/resumes`, `/documents` | 이력서/AI 문서 |
| v0.4.x | `/applications`, `/calendar` | 지원 현황과 일정 |
| v0.5.x | `/settings/integrations` | 외부 서비스 연동 |

## 구현 파일 매핑

| 화면 | 주요 파일 |
| --- | --- |
| 홈 | `frontend/src/app/page.tsx` |
| 회원가입 | `frontend/src/app/signup/page.tsx`, `frontend/src/components/auth/signup-form.tsx`, `frontend/src/components/auth/oauth-buttons.tsx` |
| 로그인 | `frontend/src/app/login/page.tsx`, `frontend/src/components/auth/login-form.tsx`, `frontend/src/components/auth/oauth-buttons.tsx` |
| 소셜 callback | `frontend/src/app/auth/callback/page.tsx`, `frontend/src/components/auth/oauth-callback-panel.tsx` |
| 내 계정 | `frontend/src/app/me/page.tsx`, `frontend/src/components/auth/protected-user-panel.tsx` |
| 소셜 계정 연결 | `frontend/src/app/settings/accounts/page.tsx`, `frontend/src/components/auth/oauth-accounts-manager.tsx` |
| 커리어 프로필 | `frontend/src/app/profile/page.tsx`, `frontend/src/components/profile/profile-manager.tsx` |
| 공통 네비게이션 | `frontend/src/components/app-header.tsx` |
