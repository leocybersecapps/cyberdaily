from pathlib import Path

CACHE_DIR = Path(".cache")
COLLECTED_PATH = CACHE_DIR / "collected.json"
RANKED_CYBER_PATH = CACHE_DIR / "ranked_cyber.json"
RANKED_AI_PATH = CACHE_DIR / "ranked_ai.json"
RANKED_CYBER_EN_PATH = CACHE_DIR / "ranked_cyber_en.json"
RANKED_AI_EN_PATH = CACHE_DIR / "ranked_ai_en.json"


def ensure_cache_dir() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
