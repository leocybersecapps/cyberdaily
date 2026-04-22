import json
import logging
import os
import sys

from src.cache import COLLECTED_PATH, RANKED_PATH, ensure_cache_dir
from src.models import RawArticle
from src.ranker.rank import rank_articles


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
    ranked = rank_articles(candidates)

    ensure_cache_dir()
    payload = [a.model_dump(mode="json") for a in ranked]
    RANKED_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, default=str, indent=2),
        encoding="utf-8",
    )
    log.info("wrote %d ranked articles to %s", len(ranked), RANKED_PATH)


if __name__ == "__main__":
    main()
