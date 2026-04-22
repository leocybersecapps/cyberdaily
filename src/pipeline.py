import logging
import os
import sys

from src.collector.collect import collect_all
from src.publisher.render import render_site
from src.ranker.rank import rank_articles


def main() -> int:
    level = logging.DEBUG if os.environ.get("DEBUG") else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    log = logging.getLogger("pipeline")

    log.info("step 1/3: collect")
    candidates = collect_all()
    if not candidates:
        log.error("no candidates collected — aborting without publishing")
        return 1

    log.info("step 2/3: rank (%d candidates)", len(candidates))
    ranked = rank_articles(candidates)
    if not ranked:
        log.error("ranker returned zero articles — aborting without publishing")
        return 1

    log.info("step 3/3: publish")
    render_site(ranked)

    log.info("pipeline complete — %d articles published", len(ranked))
    return 0


if __name__ == "__main__":
    sys.exit(main())
