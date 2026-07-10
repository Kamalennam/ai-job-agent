from pathlib import Path

from app.services.resume.resume_storage import ResumeStorageService


def test_save_persists_relative_path_only(tmp_path, monkeypatch) -> None:
    from app.config import get_settings

    monkeypatch.setenv("STORAGE_ROOT", str(tmp_path))
    monkeypatch.setenv("RESUME_STORAGE_DIR", "resumes")
    monkeypatch.setenv("API_BASE_URL", "https://jobs.example.com")
    get_settings.cache_clear()

    relative, absolute = ResumeStorageService.save("user123", b"%PDF-1.4")

    assert relative.startswith("user123/")
    assert relative.endswith(".pdf")
    assert absolute.exists()
    assert absolute.read_bytes() == b"%PDF-1.4"
    assert ResumeStorageService.build_public_url(relative) == (
        f"https://jobs.example.com/storage/resumes/{relative}"
    )

    get_settings.cache_clear()
