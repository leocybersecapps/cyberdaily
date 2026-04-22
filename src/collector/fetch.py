import logging
from datetime import datetime, timezone

import feedparser
import httpx

from src.models import RawArticle, Source


log = logging.getLogger(__name__)

HTTP_TIMEOUT = 30.0
USER_AGENT = "CyberDaily/0.1 (+https://github.com/leonardohenriques/cyberdaily)"


def fetch_feed(client: httpx.Client, source: Source) -> bytes | None:
    try:
        response = client.get(str(source.url))
        response.raise_for_status()
    except httpx.HTTPError as exc:
        log.warning("fetch failed for %s: %s", source.name, exc)
        return None
    return response.content


def parse_feed(content: bytes, source: Source) -> list[RawArticle]:
    parsed = feedparser.parse(content)
    if parsed.bozo and not parsed.entries:
        log.warning(
            "unparseable feed: %s (%s)",
            source.name,
            getattr(parsed, "bozo_exception", "unknown error"),
        )
        return []

    articles: list[RawArticle] = []
    for entry in parsed.entries:
        article = _entry_to_article(entry, source)
        if article is not None:
            articles.append(article)
    return articles


def _entry_to_article(entry, source: Source) -> RawArticle | None:
    title = entry.get("title")
    url = entry.get("link")
    if not title or not url:
        return None

    published_at = _parse_entry_date(entry)
    if published_at is None:
        return None

    summary = entry.get("summary") or ""

    try:
        return RawArticle(
            title=title,
            url=url,
            summary=summary,
            published_at=published_at,
            source_name=source.name,
            source_tier=source.tier,
            source_category=source.category,
        )
    except Exception as exc:
        log.warning("skipping invalid entry from %s: %s", source.name, exc)
        return None


def _parse_entry_date(entry) -> datetime | None:
    for key in ("published_parsed", "updated_parsed"):
        struct = entry.get(key)
        if struct:
            return datetime(*struct[:6], tzinfo=timezone.utc)
    return None
