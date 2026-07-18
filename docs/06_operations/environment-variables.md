# 환경변수

## v0.1.1 인증 환경변수

| 변수 | 설명 | 예시 |
| ---- | ---- | ---- |
| JWT_SECRET_KEY | Access Token 서명 Secret | 실제 값은 `.env`에만 저장 |
| JWT_REFRESH_SECRET_KEY | Refresh Token 서명 Secret | 실제 값은 `.env`에만 저장 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Access Token 만료 시간 | `30` |
| REFRESH_TOKEN_EXPIRE_DAYS | Refresh Token 만료 일수 | `14` |
| COOKIE_SECURE | HTTPS 환경 Cookie Secure 여부 | 개발 `false`, 운영 `true` |
| COOKIE_SAMESITE | Cookie SameSite 정책 | `lax` |

Secret 값은 저장소에 커밋하지 않는다. `.env.example`에는 변수명과 형식만 기록한다.
