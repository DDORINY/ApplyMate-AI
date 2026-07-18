# 용어집

## 서비스 용어

| 용어 | 설명 |
| ---- | ---- |
| ApplyMate AI | 개인용 AI 취업 매니저 서비스 |
| 사용자 | ApplyMate AI에 가입하여 커리어 정보와 지원 현황을 관리하는 사람 |
| 커리어 프로필 | 희망 직무, 기술, 경력, 프로젝트, 선호 조건을 포함한 사용자 기본 데이터 |
| 채용공고 | 사용자가 직접 등록하거나 외부 연동으로 수집할 채용 정보 |
| 적합도 분석 | 사용자 프로필과 채용공고 요구사항을 비교해 강점, 부족한 점, 위험 요소를 분석하는 기능 |
| 지원 문서 | 자기소개서, 지원 동기, 직무 역량 답변 등 지원 과정에서 제출하는 문서 |
| 근거 데이터 | AI 문서 생성에 사용된 사용자 경력, 프로젝트, 기술, 이력서 내용 |
| 지원 상태 | 관심, 지원 준비, 지원 완료, 결과 대기, 면접, 최종 결과 등 지원 진행 단계 |
| 일정 신뢰도 | 일정이 확정인지, 시스템 추정인지, 사용자가 직접 입력했는지 구분하는 값 |

## 인증 용어

| 용어 | 설명 |
| ---- | ---- |
| Access Token | 보호 API 호출에 사용하는 짧은 수명의 JWT |
| Refresh Token | Access Token 재발급에 사용하는 긴 수명의 토큰 |
| HttpOnly Cookie | JavaScript에서 읽을 수 없도록 제한된 Cookie |
| Token Rotation | Refresh Token 재발급 시 기존 토큰을 폐기하고 새 토큰을 발급하는 정책 |
| Token Hash | Refresh Token 원문 대신 DB에 저장하는 SHA-256 해시 |
| 사용자 상태 | `ACTIVE`, `INACTIVE`, `WITHDRAWN` 중 하나로 관리되는 계정 상태 |

## 기술 용어

| 용어 | 설명 |
| ---- | ---- |
| FastAPI | Backend REST API 구현에 사용하는 Python 웹 프레임워크 |
| Next.js App Router | Frontend 화면과 라우팅을 구성하는 Next.js 구조 |
| SQLAlchemy | Python ORM 및 DB 연결 도구 |
| Alembic | SQLAlchemy 기반 DB migration 도구 |
| PostgreSQL | 주요 서비스 데이터를 저장하는 관계형 데이터베이스 |
| Redis | 캐시, 세션 보조 정보, 비동기 작업 확장에 사용할 저장소 |
| pgvector | 향후 임베딩 벡터 검색을 위해 사용할 PostgreSQL 확장 |
| TanStack Query | Frontend 서버 상태 조회와 캐싱에 사용하는 라이브러리 |
