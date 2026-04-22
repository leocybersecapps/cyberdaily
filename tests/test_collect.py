from datetime import datetime, timezone

from src.collector.collect import dedupe_by_url
from src.models import RawArticle


def _article(url: str, title: str = "T") -> RawArticle:
    return RawArticle(
        title=title,
        url=url,
        published_at=datetime(2026, 4, 22, 10, 0, tzinfo=timezone.utc),
        source_name="S",
        source_tier=2,
    )


def test_dedupe_keeps_first_occurrence():
    articles = [
        _article("https://a.com/1", title="first"),
        _article("https://b.com/1"),
        _article("https://a.com/1", title="duplicate — should drop"),
    ]
    out = dedupe_by_url(articles)
    assert len(out) == 2
    assert out[0].title == "first"


def test_dedupe_empty():
    assert dedupe_by_url([]) == []
