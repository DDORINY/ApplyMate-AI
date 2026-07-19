# External API Integration

외부 API 연동은 사용자의 명시적 승인, 최소 권한, 안전한 토큰 저장을 기준으로 단계적으로 도입한다.

| Service | Purpose | Status |
| --- | --- | --- |
| Google OAuth | Login/account linking | Implemented |
| GitHub OAuth | Login/account linking | Implemented |
| OpenAI API | AI analysis/generation | Mock implemented, real calls NEEDS_VERIFICATION |
| Google Calendar API | Schedule sync | v0.5.0 structure implemented, real calls NEEDS_VERIFICATION |
| Gmail API | Recruitment email analysis candidates | v0.5.1 structure implemented, real calls NEEDS_VERIFICATION |

## Gmail v0.5.1 principles

- Gmail OAuth is separate from login and Calendar OAuth.
- Gmail uses read-only `gmail.readonly` scope.
- ApplyMate AI never modifies, deletes, or sends Gmail messages in v0.5.1.
- Status changes and schedule creation require explicit user approval.
- Real Gmail token exchange, message search, and message fetch require operational Google Cloud verification.
