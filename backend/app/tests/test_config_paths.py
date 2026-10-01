from pathlib import Path

from app.config import _detect_project_root, _resolve_env_file, _resolve_env_files, get_settings


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


def test_resolve_env_files_layers_local_over_env(tmp_path, monkeypatch) -> None:
    (tmp_path / ".env").write_text("APP_ENV=production\n", encoding="utf-8")
    (tmp_path / ".env.local").write_text("APP_ENV=development\n", encoding="utf-8")

    monkeypatch.setattr("app.config._detect_project_root", lambda: tmp_path)

    assert _resolve_env_files() == (str(tmp_path / ".env"), str(tmp_path / ".env.local"))
    assert _resolve_env_file() == str(tmp_path / ".env.local")


def test_resolve_env_files_env_only_on_production_server(tmp_path, monkeypatch) -> None:
    (tmp_path / ".env").write_text("APP_ENV=production\n", encoding="utf-8")

    monkeypatch.setattr("app.config._detect_project_root", lambda: tmp_path)

    assert _resolve_env_files() == (str(tmp_path / ".env"),)
    assert _resolve_env_file() == str(tmp_path / ".env")
