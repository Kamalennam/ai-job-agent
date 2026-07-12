from pathlib import Path

from app.config import _detect_project_root, get_settings


def test_detect_project_root_points_at_backend_parent() -> None:
    root = _detect_project_root()
    assert (root / "backend" / "app" / "config.py").exists() or (root / "app" / "config.py").exists()


def test_relative_prompts_dir_resolves_under_project_root(tmp_path, monkeypatch) -> None:
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "resume_extraction.md").write_text("test", encoding="utf-8")

    monkeypatch.setattr(
        "app.config._detect_project_root",
        lambda: tmp_path,
    )
    monkeypatch.setenv("PROMPTS_DIR", "prompts")
    get_settings.cache_clear()

    settings = get_settings()
    assert settings.resolved_prompts_dir == prompts_dir
    assert (settings.resolved_prompts_dir / "resume_extraction.md").exists()

    get_settings.cache_clear()
