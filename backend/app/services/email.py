from dataclasses import dataclass
from email.message import EmailMessage
import smtplib

from app.core.config import settings
from app.core.exceptions import AppError


@dataclass(frozen=True)
class SentEmail:
    to: str
    subject: str
    body: str


development_outbox: list[SentEmail] = []


def clear_development_outbox() -> None:
    development_outbox.clear()


class EmailSender:
    async def send(self, to: str, subject: str, body: str) -> None:
        raise NotImplementedError


class DevelopmentEmailSender(EmailSender):
    async def send(self, to: str, subject: str, body: str) -> None:
        development_outbox.append(SentEmail(to=to, subject=subject, body=body))


class DisabledEmailSender(EmailSender):
    async def send(self, to: str, subject: str, body: str) -> None:
        raise AppError("EMAIL_PROVIDER_DISABLED", "이메일 발송 기능이 비활성화되어 있습니다.", 503)


class SmtpEmailSender(EmailSender):
    async def send(self, to: str, subject: str, body: str) -> None:
        if not settings.smtp_host or not settings.email_from_address:
            raise AppError("EMAIL_PROVIDER_NOT_CONFIGURED", "SMTP 이메일 설정이 필요합니다.", 500)

        message = EmailMessage()
        message["From"] = f"{settings.email_from_name} <{settings.email_from_address}>"
        message["To"] = to
        message["Subject"] = subject
        message.set_content(body)

        try:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
                if settings.smtp_use_tls:
                    smtp.starttls()
                if settings.smtp_username and settings.smtp_password:
                    smtp.login(settings.smtp_username, settings.smtp_password)
                smtp.send_message(message)
        except smtplib.SMTPException as exc:
            raise AppError("EMAIL_DELIVERY_FAILED", "이메일 발송에 실패했습니다.", 502) from exc


def get_email_sender() -> EmailSender:
    provider = settings.email_provider.strip().lower()
    if provider == "smtp":
        return SmtpEmailSender()
    if provider == "disabled":
        return DisabledEmailSender()
    return DevelopmentEmailSender()
