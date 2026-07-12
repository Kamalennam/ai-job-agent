from types import SimpleNamespace

from app.services.resume.resume_storage import ResumeStorageService


def test_build_file_url_prefers_stored_url() -> None:
    from app.services.resume.resume_service import ResumeService

    resume = SimpleNamespace(
        file_url="http://187.127.146.159:8001/storage/resumes/user/a.pdf",
        file_path="user/a.pdf",
    )
    assert ResumeService._build_file_url(resume) == resume.file_url


def test_build_file_url_computes_when_stored_url_missing(tmp_path, monkeypatch) -> None:
    from app.config import get_settings
    from app.services.resume.resume_service import ResumeService

    monkeypatch.setenv("STORAGE_ROOT", str(tmp_path))
    monkeypatch.setenv("RESUME_STORAGE_DIR", "resumes")
    monkeypatch.setenv("API_BASE_URL", "https://jobs.example.com")
    get_settings.cache_clear()

    resume = SimpleNamespace(file_url=None, file_path="user/a.pdf")
    assert ResumeService._build_file_url(resume) == (
        "https://jobs.example.com/storage/resumes/user/a.pdf"
    )

    get_settings.cache_clear()


def test_upload_public_url_pattern(tmp_path, monkeypatch) -> None:
    from app.config import get_settings

    monkeypatch.setenv("STORAGE_ROOT", str(tmp_path))
    monkeypatch.setenv("RESUME_STORAGE_DIR", "resumes")
    monkeypatch.setenv("API_BASE_URL", "http://187.127.146.159:8001")
    get_settings.cache_clear()

    relative = "user123/abc.pdf"
    expected = ResumeStorageService.build_public_url(relative)
    assert expected == "http://187.127.146.159:8001/storage/resumes/user123/abc.pdf"

    get_settings.cache_clear()
