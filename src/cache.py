from pathlib import Path

CACHE_DIR = Path(".cache")
COLLECTED_PATH = CACHE_DIR / "collected.json"
RANKED_PATH = CACHE_DIR / "ranked.json"


def ensure_cache_dir() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
