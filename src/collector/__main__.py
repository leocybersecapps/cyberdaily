import json
import logging
import os

from src.cache import COLLECTED_PATH, ensure_cache_dir
from src.collector.collect import collect_all


def main() -> None:
    level = logging.DEBUG if os.environ.get("DEBUG") else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    log = logging.getLogger("collector")

    articles = collect_all()
    ensure_cache_dir()
    payload = [a.model_dump(mode="json") for a in articles]
    COLLECTED_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, default=str, indent=2),
        encoding="utf-8",
    )
    log.info("wrote %d articles to %s", len(articles), COLLECTED_PATH)


if __name__ == "__main__":
    main()
