import logging
from datetime import datetime, timedelta, timezone

import httpx

from src.collector.fetch import HTTP_TIMEOUT, USER_AGENT, fetch_feed, parse_feed
from src.collector.sources import load_sources
from src.models import RawArticle, Source


log = logging.getLogger(__name__)

DEFAULT_WINDOW_HOURS = 24


def collect_all(
    sources: list[Source] | None = None,
    window_hours: int = DEFAULT_WINDOW_HOURS,
    now: datetime | None = None,
) -> list[RawArticle]:
    if sources is None:
        sources = load_sources()
    if now is None:
        now = datetime.now(tz=timezone.utc)

    cutoff = now - timedelta(hours=window_hours)
    collected: list[RawArticle] = []

    with httpx.Client(
        timeout=HTTP_TIMEOUT,
        follow_redirects=True,
        headers={"User-Agent": USER_AGENT},
    ) as client:
        for source in sources:
            log.info("fetching %s", source.name)
            content = fetch_feed(client, source)
            if content is None:
                continue
            parsed = parse_feed(content, source)
            fresh = [a for a in parsed if a.published_at >= cutoff]
            log.info(
                "%s: %d entries, %d within %dh window",
                source.name,
                len(parsed),
                len(fresh),
                window_hours,
            )
            collected.extend(fresh)

    deduped = dedupe_by_url(collected)
    log.info(
        "collected %d unique articles (%d before dedupe)",
        len(deduped),
        len(collected),
    )
    return deduped


def dedupe_by_url(articles: list[RawArticle]) -> list[RawArticle]:
    seen: set[str] = set()
    out: list[RawArticle] = []
    for article in articles:
        key = str(article.url)
        if key in seen:
            continue
        seen.add(key)
        out.append(article)
    return out
