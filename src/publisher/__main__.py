import json
import logging
import os
import sys

from src.cache import RANKED_AI_PATH, RANKED_CYBER_PATH
from src.models import RankedArticle
from src.publisher.render import render_site


def _load(path) -> list[RankedArticle]:
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [RankedArticle.model_validate(item) for item in raw]


def main() -> None:
    level = logging.DEBUG if os.environ.get("DEBUG") else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    articles_cyber = _load(RANKED_CYBER_PATH)
    articles_ai = _load(RANKED_AI_PATH)

    if not articles_cyber and not articles_ai:
        sys.exit(
            f"no ranker cache at {RANKED_CYBER_PATH} or {RANKED_AI_PATH}. "
            "Run `uv run python -m src.ranker` first."
        )

    render_site(articles_cyber, articles_ai)


if __name__ == "__main__":
    main()
