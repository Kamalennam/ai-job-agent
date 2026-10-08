from app.ai.ollama_client import consume_stream_line
from app.services.resume.parse_progress import analysis_progress
from app.services.resume.resume_storage import ResumeStorageService


def test_analysis_progress_moves_as_content_arrives() -> None:
    start = analysis_progress(0)
    mid = analysis_progress(400)
    later = analysis_progress(2000)

    assert start == 35
    assert mid > start
    assert later > mid
    assert later <= 90


def test_consume_stream_line_collects_response_text() -> None:
    parts: list[str] = []
    added, done = consume_stream_line(parts, '{"response":"{\\"name\\":","done":false}')
    assert added > 0
    assert done is False
    added, done = consume_stream_line(parts, '{"response":"","done":true}')
    assert added == 0
    assert done is True
    assert "".join(parts).startswith('{"name":')


def test_storage_delete_removes_saved_file(tmp_path, monkeypatch) -> None:
    from app.config import get_settings

    monkeypatch.setenv("STORAGE_ROOT", str(tmp_path))
    monkeypatch.setenv("RESUME_STORAGE_DIR", "resumes")
    get_settings.cache_clear()

    relative, path = ResumeStorageService.save("user", b"%PDF-1.4")
    assert path.is_file()
    ResumeStorageService.delete(relative)
    assert not path.exists()

    get_settings.cache_clear()
