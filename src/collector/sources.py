from pathlib import Path

import yaml

from src.models import Source


DEFAULT_SOURCES_PATH = Path("config/sources.yaml")


def load_sources(path: Path = DEFAULT_SOURCES_PATH) -> list[Source]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "sources" not in data:
        raise ValueError(f"{path} must contain a top-level 'sources' key")
    return [Source.model_validate(item) for item in data["sources"]]
