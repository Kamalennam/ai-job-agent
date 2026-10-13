import asyncio
import socket
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import AppException
from app.schemas.auth import RegisterRequest
from app.services.email.email_service import (
    EmailDeliveryError,
    _open_ipv4_socket,
    send_verification_email,
)


def test_open_ipv4_socket_uses_ipv4_only() -> None:
    sock = MagicMock()
    family_seen: list[int] = []

    def fake_getaddrinfo(host, port, family, socktype):
        family_seen.append(family)
        return [(family, socktype, 0, "", ("192.0.2.10", port))]

    with (
        patch("app.services.email.email_service.socket.getaddrinfo", side_effect=fake_getaddrinfo),
        patch("app.services.email.email_service.socket.socket", return_value=sock),
    ):
        opened = _open_ipv4_socket("smtp.gmail.com", 587, 5)

    assert opened is sock
    assert family_seen == [socket.AF_INET]
    sock.connect.assert_called_once_with(("192.0.2.10", 587))


def test_send_verification_email_connects_over_ipv4_socket() -> None:
    settings = MagicMock()
    settings.smtp_configured = True
    settings.smtp_host = "smtp.gmail.com"
    settings.smtp_port = 587
    settings.smtp_user = "user@gmail.com"
    settings.smtp_password = "app-password"
    settings.smtp_from_email = "user@gmail.com"
    settings.email_verification_expire_hours = 24

    sock = MagicMock()
    client = MagicMock()
    client.connect = AsyncMock()
    client.send_message = AsyncMock()
    client.quit = AsyncMock()

    async def run() -> None:
        with (
            patch("app.services.email.email_service.get_settings", return_value=settings),
            patch(
                "app.services.email.email_service._open_ipv4_socket",
                return_value=sock,
            ) as open_sock,
            patch("app.services.email.email_service.aiosmtplib.SMTP", return_value=client) as smtp,
        ):
            await send_verification_email("person@example.com", "https://app.example/verify-email?token=abc")
            open_sock.assert_called_once_with("smtp.gmail.com", 587, 12)
            kwargs = smtp.call_args.kwargs
            assert kwargs["sock"] is sock
            assert kwargs["hostname"] == "smtp.gmail.com"
            assert kwargs["start_tls"] is True
            assert kwargs["use_tls"] is False
            assert "port" not in kwargs
            client.send_message.assert_awaited()

    asyncio.run(run())


def test_send_verification_email_logs_link_when_smtp_is_not_configured() -> None:
    settings = MagicMock()
    settings.smtp_configured = False
    settings.email_verification_expire_hours = 24

    async def run() -> None:
        with (
            patch("app.services.email.email_service.get_settings", return_value=settings),
            patch("app.services.email.email_service._open_ipv4_socket") as open_sock,
        ):
            await send_verification_email("person@example.com", "https://app.example/verify-email?token=abc")
            open_sock.assert_not_called()

    asyncio.run(run())


def test_register_keeps_account_when_email_delivery_fails() -> None:
    from app.services.auth.auth_service import AuthService

    created: list[object] = []
    saved_user = MagicMock()
    saved_user.id = "user-id"

    async def create_user(user):
        created.append(user)
        return saved_user

    settings = MagicMock()
    settings.email_verification_expire_hours = 24
    settings.frontend_base_url = "http://localhost:5173"

    async def run() -> None:
        with (
            patch("app.services.auth.auth_service.get_settings", return_value=settings),
            patch("app.services.auth.auth_service.User", return_value=MagicMock()),
            patch("app.services.auth.auth_service.Profile", return_value=MagicMock()),
            patch("app.services.auth.auth_service.UserSettings", return_value=MagicMock()),
            patch(
                "app.services.auth.auth_service.UserRepository.get_by_email",
                new=AsyncMock(return_value=None),
            ),
            patch("app.services.auth.auth_service.UserRepository.create", side_effect=create_user),
            patch("app.services.auth.auth_service.ProfileRepository.create", new=AsyncMock()),
            patch("app.services.auth.auth_service.SettingsRepository.create", new=AsyncMock()),
            patch(
                "app.services.auth.auth_service.send_verification_email",
                new=AsyncMock(side_effect=EmailDeliveryError("down")),
            ),
        ):
            with pytest.raises(AppException) as exc:
                await AuthService.register(
                    RegisterRequest(
                        email="person@example.com",
                        password="password123",
                        full_name="Person Example",
                    )
                )

        assert exc.value.code == "EMAIL_DELIVERY_FAILED"
        assert exc.value.status_code == 503
        assert created

    asyncio.run(run())
