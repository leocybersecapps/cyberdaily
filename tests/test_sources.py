from pathlib import Path

import pytest
from pydantic import ValidationError

from src.collector.sources import load_sources


def test_load_real_sources_yaml():
    sources = load_sources(Path("config/sources.yaml"))
    assert len(sources) > 0
    assert all(str(s.url).startswith("https://") for s in sources)
    assert all(s.tier in (1, 2) for s in sources)
    assert all(s.category in ("cyber", "ai") for s in sources)
    # both tracks must have at least one source
    categories = {s.category for s in sources}
    assert categories == {"cyber", "ai"}


def test_category_defaults_to_cyber(tmp_path: Path):
    yaml_content = """
sources:
  - name: Legacy
    url: https://example.com/feed.xml
    tier: 2
"""
    p = tmp_path / "legacy.yaml"
    p.write_text(yaml_content)
    sources = load_sources(p)
    assert sources[0].category == "cyber"


def test_rejects_unknown_category(tmp_path: Path):
    yaml_content = """
sources:
  - name: Bad Category
    url: https://example.com/feed.xml
    tier: 2
    category: sports
"""
    p = tmp_path / "bad.yaml"
    p.write_text(yaml_content)
    with pytest.raises(ValidationError):
        load_sources(p)


def test_rejects_http_source(tmp_path: Path):
    yaml_content = """
sources:
  - name: Insecure
    url: http://example.com/feed.xml
    tier: 2
"""
    p = tmp_path / "bad.yaml"
    p.write_text(yaml_content)
    with pytest.raises(ValidationError):
        load_sources(p)


def test_rejects_invalid_tier(tmp_path: Path):
    yaml_content = """
sources:
  - name: Bad Tier
    url: https://example.com/feed.xml
    tier: 99
"""
    p = tmp_path / "bad.yaml"
    p.write_text(yaml_content)
    with pytest.raises(ValidationError):
        load_sources(p)


def test_rejects_missing_top_level(tmp_path: Path):
    p = tmp_path / "empty.yaml"
    p.write_text("foo: bar\n")
    with pytest.raises(ValueError):
        load_sources(p)
