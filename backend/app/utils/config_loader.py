
import yaml
from app.config import get_settings


def load_yaml(filename: str) -> dict:
    settings = get_settings()
    path = settings.resolved_configs_dir / filename
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_job_sources_config() -> dict:
    return load_yaml("job_sources.yaml")


def load_companies_config() -> dict:
    return load_yaml("companies.yaml")
