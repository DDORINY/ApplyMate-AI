from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

from app.integrations.gmail.base import GmailMessage, GmailMessageRef, GmailToken


class MockGmailProvider:
    def authorization_url(self, *, state: str, redirect_uri: str, scopes: list[str]) -> str:
        mock_code = f"mock-gmail-code-{state[:12]}"
        query = urlencode({"state": state, "code": mock_code, "redirect_uri": redirect_uri, "scope": " ".join(scopes)})
        return f"{redirect_uri}?{query}"

    async def exchange_code(self, *, code: str, redirect_uri: str) -> GmailToken:
        account_suffix = code.removeprefix("mock-gmail-code-") or "default"
        return GmailToken(
            access_token=f"mock-gmail-access-credential-{code}",
            refresh_token=f"mock-gmail-refresh-credential-{account_suffix}",
            expires_at=datetime.now(UTC) + timedelta(hours=1),
            provider_account_id=f"mock-gmail-user-{account_suffix}",
            email=f"mock-gmail-{account_suffix}@example.com",
            display_name="Mock Gmail User",
            scopes=["openid", "email", "profile", "https://www.googleapis.com/auth/gmail.readonly"],
        )

    async def refresh_token(self, *, refresh_token: str) -> GmailToken:
        return await self.exchange_code(code="refreshed", redirect_uri="")

    async def revoke_token(self, *, token: str) -> None:
        return None

    async def search_messages(self, *, access_token: str, query: str, max_results: int) -> list[GmailMessageRef]:
        refs = [
            GmailMessageRef(id="mock-application-received", thread_id="thread-1"),
            GmailMessageRef(id="mock-interview", thread_id="thread-2"),
            GmailMessageRef(id="mock-rejected", thread_id="thread-3"),
            GmailMessageRef(id="mock-schedule-change", thread_id="thread-4"),
        ]
        return refs[:max_results]

    async def get_message(self, *, access_token: str, message_id: str) -> GmailMessage:
        now = datetime.now(UTC)
        messages = {
            "mock-application-received": GmailMessage(
                id=message_id,
                thread_id="thread-1",
                sender="recruiter@alpha.example.com",
                subject="[Alpha] 백엔드 개발자 지원 접수 안내",
                received_at=now - timedelta(days=2),
                snippet="지원서가 정상 접수되었습니다.",
                text="Alpha 백엔드 개발자 포지션 지원서가 정상 접수되었습니다. 서류 검토 후 안내드리겠습니다.",
            ),
            "mock-interview": GmailMessage(
                id=message_id,
                thread_id="thread-2",
                sender="hr@bravo.example.com",
                subject="[Bravo] 1차 면접 일정 안내",
                received_at=now - timedelta(days=1),
                snippet="7월 25일 오후 2시에 화상 면접을 진행합니다.",
                text="Bravo 프론트엔드 개발자 1차 면접은 2026년 7월 25일 오후 2시에 진행됩니다. 링크: https://meet.example.com/bravo",
            ),
            "mock-rejected": GmailMessage(
                id=message_id,
                thread_id="thread-3",
                sender="no-reply@charlie.example.com",
                subject="[Charlie] 서류 전형 결과 안내",
                received_at=now - timedelta(hours=12),
                snippet="아쉽게도 이번 전형은 불합격입니다.",
                text="Charlie 데이터 분석가 포지션에 관심을 가져주셔서 감사합니다. 아쉽게도 이번 서류 전형은 불합격입니다.",
            ),
            "mock-schedule-change": GmailMessage(
                id=message_id,
                thread_id="thread-4",
                sender="talent@delta.example.com",
                subject="[Delta] 코딩테스트 일정 변경 안내",
                received_at=now - timedelta(hours=6),
                snippet="코딩테스트 일정이 7월 26일 오전 10시로 변경되었습니다.",
                text="Delta 플랫폼 엔지니어 코딩테스트 일정이 2026년 7월 26일 오전 10시로 변경되었습니다.",
            ),
        }
        return messages.get(
            message_id,
            GmailMessage(
                id=message_id,
                thread_id=None,
                sender="newsletter@example.com",
                subject="Weekly newsletter",
                received_at=now,
                snippet="일반 뉴스레터",
                text="채용과 무관한 일반 메일입니다.",
            ),
        )
