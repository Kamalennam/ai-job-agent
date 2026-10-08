import asyncio
from unittest.mock import MagicMock, patch


def test_publish_queues_worker_when_broker_is_available() -> None:
    with (
        patch("app.events.resume_uploaded.parse_resume") as task,
        patch("app.events.resume_uploaded._parse_in_process") as fallback,
    ):
        from app.events.resume_uploaded import publish

        publish("resume-1", "user-1")

    task.delay.assert_called_once_with("resume-1")
    fallback.assert_not_called()


def test_publish_parses_in_process_when_broker_is_down() -> None:
    loop = MagicMock()
    created: list[asyncio.Task[None]] = []

    def capture(coro: asyncio.Future[None]) -> asyncio.Task[None]:
        coro.close()
        task = MagicMock()
        created.append(task)
        return task

    loop.create_task.side_effect = capture

    with (
        patch("app.events.resume_uploaded.parse_resume") as task,
        patch("app.events.resume_uploaded.asyncio.get_running_loop", return_value=loop),
    ):
        task.delay.side_effect = ConnectionError("redis down")
        from app.events.resume_uploaded import publish

        publish("resume-1", "user-1")

    loop.create_task.assert_called_once()
    created[0].add_done_callback.assert_called_once()
