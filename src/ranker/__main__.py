import json
import logging
import os
import sys

from src.cache import (
    COLLECTED_PATH,
    RANKED_AI_PATH,
    RANKED_CYBER_PATH,
    ensure_cache_dir,
)
from src.models import RankedArticle, RawArticle
from src.ranker.rank import PROMPT_AI, PROMPT_CYBER, rank_articles


def _write_ranked(path, articles: list[RankedArticle]) -> None:
    payload = [a.model_dump(mode="json") for a in articles]
    path.write_text(
        json.dumps(payload, ensure_ascii=False, default=str, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    level = logging.DEBUG if os.environ.get("DEBUG") else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    log = logging.getLogger("ranker")

    if not COLLECTED_PATH.exists():
        sys.exit(
            f"no collector cache at {COLLECTED_PATH}. "
            "Run `uv run python -m src.collector` first."
        )

    raw = json.loads(COLLECTED_PATH.read_text(encoding="utf-8"))
    candidates = [RawArticle.model_validate(item) for item in raw]

    cyber = [c for c in candidates if c.source_category == "cyber"]
    ai = [c for c in candidates if c.source_category == "ai"]

    ensure_cache_dir()

    ranked_cyber = rank_articles(cyber, prompt_path=PROMPT_CYBER)
    _write_ranked(RANKED_CYBER_PATH, ranked_cyber)
    log.info("wrote %d cyber articles to %s", len(ranked_cyber), RANKED_CYBER_PATH)

    ranked_ai = rank_articles(ai, prompt_path=PROMPT_AI)
    _write_ranked(RANKED_AI_PATH, ranked_ai)
    log.info("wrote %d ai articles to %s", len(ranked_ai), RANKED_AI_PATH)


if __name__ == "__main__":
    main()
