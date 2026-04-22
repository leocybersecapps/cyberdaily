from pathlib import Path

import pytest
from pydantic import ValidationError

from src.collector.sources import load_sources


def test_load_real_sources_yaml():
    sources = load_sources(Path("config/sources.yaml"))
    assert len(sources) > 0
    assert all(str(s.url).startswith("https://") for s in sources)
    assert all(s.tier in (1, 2) for s in sources)


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
