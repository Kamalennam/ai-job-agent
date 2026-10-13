import asyncio
from unittest.mock import MagicMock, patch


def test_publish_queues_worker_when_broker_is_available() -> None:
    with (
        patch("app.events.resume_uploaded.parse_resume") as task,
        patch("app.events.resume_uploaded._parse_in_process") as fallback,
        patch("app.events.resume_uploaded._running_loop", return_value=None),
    ):
        from app.events.resume_uploaded import publish

        publish("resume-1", "user-1")

    task.delay.assert_called_once_with("resume-1")
    fallback.assert_not_called()


def test_publish_parses_in_process_when_broker_is_down() -> None:
    with (
        patch("app.events.resume_uploaded.parse_resume") as task,
        patch("app.events.resume_uploaded._parse_in_process") as fallback,
        patch("app.events.resume_uploaded._running_loop", return_value=None),
    ):
        task.delay.side_effect = ConnectionError("redis down")
        from app.events.resume_uploaded import publish

        publish("resume-1", "user-1")

    fallback.assert_called_once_with("resume-1")


def test_publish_schedules_parse_off_the_caller_when_a_loop_is_running() -> None:
    loop = MagicMock()

    def capture(coro: asyncio.Future[None]) -> asyncio.Task[None]:
        coro.close()
        return MagicMock()

    loop.create_task.side_effect = capture

    with (
        patch("app.events.resume_uploaded.parse_resume") as task,
        patch("app.events.resume_uploaded._running_loop", return_value=loop),
    ):
        from app.events.resume_uploaded import publish

        publish("resume-1", "user-1")

    loop.create_task.assert_called_once()
    task.delay.assert_not_called()
