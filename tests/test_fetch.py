from datetime import timezone
from pathlib import Path

from src.collector.fetch import parse_feed
from src.models import Source


def _source() -> Source:
    return Source(
        name="Fixture",
        url="https://example.com/feed.xml",
        tier=2,
    )


def test_parse_feed_extracts_entries(fixtures_dir: Path):
    content = (fixtures_dir / "sample_feed.xml").read_bytes()
    articles = parse_feed(content, _source())

    # 3 entries in fixture; one has no pubDate → skipped
    assert len(articles) == 2
    titles = [a.title for a in articles]
    assert "Critical zero-day exploited in the wild" in titles
    assert "Old story from last year" in titles


def test_parse_feed_sets_source_metadata(fixtures_dir: Path):
    content = (fixtures_dir / "sample_feed.xml").read_bytes()
    source = _source()
    articles = parse_feed(content, source)

    for article in articles:
        assert article.source_name == source.name
        assert article.source_tier == source.tier
        assert article.published_at.tzinfo is not None


def test_parse_feed_dates_are_utc(fixtures_dir: Path):
    content = (fixtures_dir / "sample_feed.xml").read_bytes()
    articles = parse_feed(content, _source())
    for article in articles:
        assert article.published_at.utcoffset() == timezone.utc.utcoffset(None)


def test_parse_feed_empty_on_garbage():
    articles = parse_feed(b"not xml at all", _source())
    assert articles == []
