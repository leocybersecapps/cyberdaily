import json

import pytest
from pydantic import ValidationError

from src.ranker.rank import parse_ranker_response, rank_articles


def _valid_item() -> dict:
    return {
        "titulo": "Zero-day crítico no Widget Engine",
        "resumo": "Vendor divulgou patch emergencial após exploração ativa observada por múltiplos grupos.",
        "por_que_importa": "Ambiente corporativo com Widget Engine exposto tem superfície imediata.",
        "gancho_conversa": "Se o cliente X ainda roda Widget Engine na borda, é conversa pra essa semana.",
        "fonte": "Fixture",
        "url": "https://example.com/zero-day",
        "data_publicacao": "2026-04-22T10:00:00Z",
    }


def test_parse_clean_json_array():
    raw = json.dumps([_valid_item()])
    out = parse_ranker_response(raw)
    assert len(out) == 1
    assert out[0].titulo == "Zero-day crítico no Widget Engine"


def test_parse_with_json_code_fence():
    raw = "```json\n" + json.dumps([_valid_item()]) + "\n```"
    out = parse_ranker_response(raw)
    assert len(out) == 1


def test_parse_with_plain_code_fence():
    raw = "```\n" + json.dumps([_valid_item()]) + "\n```"
    out = parse_ranker_response(raw)
    assert len(out) == 1


def test_parse_rejects_non_array_top_level():
    with pytest.raises(ValueError):
        parse_ranker_response('{"not": "an array"}')


def test_parse_rejects_missing_required_field():
    item = _valid_item()
    del item["gancho_conversa"]
    with pytest.raises(ValidationError):
        parse_ranker_response(json.dumps([item]))


def test_parse_rejects_extra_field():
    item = _valid_item()
    item["extra_campo"] = "nao deveria existir"
    with pytest.raises(ValidationError):
        parse_ranker_response(json.dumps([item]))


def test_parse_rejects_malformed_json():
    with pytest.raises(json.JSONDecodeError):
        parse_ranker_response("not json")


def test_rank_empty_candidates_returns_empty():
    assert rank_articles([]) == []
