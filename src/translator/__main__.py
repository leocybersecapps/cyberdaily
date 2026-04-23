import json
import logging
import os
import sys

from src.cache import (
    RANKED_AI_EN_PATH,
    RANKED_AI_PATH,
    RANKED_CYBER_EN_PATH,
    RANKED_CYBER_PATH,
    ensure_cache_dir,
)
from src.models import RankedArticle
from src.translator.translate import translate_to_english


def _load(path) -> list[RankedArticle]:
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [RankedArticle.model_validate(item) for item in raw]


def _write(path, articles: list[RankedArticle]) -> None:
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
    log = logging.getLogger("translator")

    cyber = _load(RANKED_CYBER_PATH)
    ai = _load(RANKED_AI_PATH)

    if not cyber and not ai:
        sys.exit(
            f"no ranker cache at {RANKED_CYBER_PATH} or {RANKED_AI_PATH}. "
            "Run `uv run python -m src.ranker` first."
        )

    ensure_cache_dir()

    cyber_en = translate_to_english(cyber)
    _write(RANKED_CYBER_EN_PATH, cyber_en)
    log.info("wrote %d EN cyber articles to %s", len(cyber_en), RANKED_CYBER_EN_PATH)

    ai_en = translate_to_english(ai)
    _write(RANKED_AI_EN_PATH, ai_en)
    log.info("wrote %d EN ai articles to %s", len(ai_en), RANKED_AI_EN_PATH)


if __name__ == "__main__":
    main()
