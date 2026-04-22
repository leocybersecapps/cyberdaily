import logging
import os
import sys

from src.collector.collect import collect_all
from src.models import RankedArticle, RawArticle
from src.publisher.render import render_site
from src.ranker.rank import PROMPT_AI, PROMPT_CYBER, rank_articles


log = logging.getLogger(__name__)


def _rank_category(
    candidates: list[RawArticle],
    prompt_path,
    label: str,
) -> list[RankedArticle]:
    """Rank one category. Returns [] on failure so the other track still publishes."""
    if not candidates:
        log.warning("%s: no candidates — skipping rank", label)
        return []
    try:
        ranked = rank_articles(candidates, prompt_path=prompt_path)
        log.info("%s: ranked %d articles", label, len(ranked))
        return ranked
    except Exception:
        log.exception("%s: ranker failed — section will be empty", label)
        return []


def main() -> int:
    level = logging.DEBUG if os.environ.get("DEBUG") else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    log.info("step 1/3: collect")
    candidates = collect_all()
    if not candidates:
        log.error("no candidates collected — aborting without publishing")
        return 1

    cyber_candidates = [c for c in candidates if c.source_category == "cyber"]
    ai_candidates = [c for c in candidates if c.source_category == "ai"]
    log.info(
        "candidates by category: cyber=%d ai=%d",
        len(cyber_candidates),
        len(ai_candidates),
    )

    log.info("step 2/3: rank")
    ranked_cyber = _rank_category(cyber_candidates, PROMPT_CYBER, "cyber")
    ranked_ai = _rank_category(ai_candidates, PROMPT_AI, "ai")

    if not ranked_cyber and not ranked_ai:
        log.error("both tracks returned zero articles — aborting without publishing")
        return 1

    log.info("step 3/3: publish")
    render_site(ranked_cyber, ranked_ai)

    log.info(
        "pipeline complete — %d cyber + %d ai articles published",
        len(ranked_cyber),
        len(ranked_ai),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
