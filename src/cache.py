from pathlib import Path

CACHE_DIR = Path(".cache")
COLLECTED_PATH = CACHE_DIR / "collected.json"
RANKED_CYBER_PATH = CACHE_DIR / "ranked_cyber.json"
RANKED_AI_PATH = CACHE_DIR / "ranked_ai.json"


def ensure_cache_dir() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
