import socket
from email.message import EmailMessage

import aiosmtplib
from loguru import logger

from app.config import get_settings

_CONNECT_TIMEOUT_SECONDS = 12


class EmailDeliveryError(Exception):
    """Raised when a verification message cannot be handed to the mail server."""


def _open_ipv4_socket(host: str, port: int, timeout: float) -> socket.socket:
    """Connect with IPv4 only.

    asyncio and aiosmtplib follow the system address order. On networks where
    IPv6 to the SMTP host is unreachable, that attempt waits until the whole
    timeout and the verification email is never sent. Port 587 on IPv4 is the
    path that actually accepts the connection.
    """
    infos = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
    if not infos:
        raise OSError(f"No IPv4 address for {host}")

    last_error: OSError | None = None
    for info in infos:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        try:
            sock.connect(info[4])
            sock.settimeout(None)
            return sock
        except OSError as exc:
            last_error = exc
            sock.close()

    raise last_error or OSError(f"Could not connect to {host}:{port}")


async def send_verification_email(to_email: str, verification_url: str) -> None:
    settings = get_settings()
    subject = "Verify your AI Job Agent account"
    body = (
        "Welcome to AI Job Agent.\n\n"
        "Confirm your email address by opening this link:\n\n"
        f"{verification_url}\n\n"
        f"The link expires in {settings.email_verification_expire_hours} hours.\n"
        "If you did not create an account, you can ignore this message.\n"
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

    use_implicit_tls = settings.smtp_port == 465
    sock = _open_ipv4_socket(settings.smtp_host, settings.smtp_port, _CONNECT_TIMEOUT_SECONDS)
    client = aiosmtplib.SMTP(
        hostname=settings.smtp_host,
        username=settings.smtp_user or None,
        password=settings.smtp_password or None,
        timeout=_CONNECT_TIMEOUT_SECONDS,
        use_tls=use_implicit_tls,
        start_tls=not use_implicit_tls,
        sock=sock,
    )

    try:
        await client.connect()
        await client.send_message(message)
        await client.quit()
    except Exception as exc:
        client.close()
        logger.error("Verification email to {} failed: {}", to_email, exc)
        logger.info("Verification link for {}: {}", to_email, verification_url)
        raise EmailDeliveryError("Could not send the verification email") from exc
