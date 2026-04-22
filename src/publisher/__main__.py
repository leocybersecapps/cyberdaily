import json
import logging
import os
import sys

from src.cache import RANKED_PATH
from src.models import RankedArticle
from src.publisher.render import render_site


def main() -> None:
    level = logging.DEBUG if os.environ.get("DEBUG") else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    if not RANKED_PATH.exists():
        sys.exit(
            f"no ranker cache at {RANKED_PATH}. "
            "Run `uv run python -m src.ranker` first."
        )

    raw = json.loads(RANKED_PATH.read_text(encoding="utf-8"))
    articles = [RankedArticle.model_validate(item) for item in raw]
    render_site(articles)


if __name__ == "__main__":
    main()
