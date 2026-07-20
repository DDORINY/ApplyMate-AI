import asyncio

from app.db.session import AsyncSessionLocal
from app.services.notification import NotificationService


async def run_due_notifications() -> None:
    async with AsyncSessionLocal() as session:
        await NotificationService(session).run_due(user_id=None)


def main() -> None:
    asyncio.run(run_due_notifications())


if __name__ == "__main__":
    main()
