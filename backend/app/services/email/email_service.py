from email.message import EmailMessage

import aiosmtplib
from loguru import logger

from app.config import get_settings


async def send_verification_email(to_email: str, verification_url: str) -> None:
    settings = get_settings()
    subject = "Verify your AI Job Agent account"
    body = (
        "Welcome to AI Job Agent!\n\n"
        "Please verify your email address by clicking the link below:\n\n"
        f"{verification_url}\n\n"
        "This link expires in 24 hours.\n"
    )

    if not settings.smtp_configured:
        logger.info(
            "SMTP not configured — verification email for {}: {}",
            to_email,
            verification_url,
        )
        return

    message = EmailMessage()
    message["From"] = settings.smtp_from_email
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_user or None,
        password=settings.smtp_password or None,
        start_tls=True,
    )
