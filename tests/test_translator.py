import json
from datetime import datetime, timezone

import pytest

from src.models import RankedArticle
from src.translator.translate import (
    apply_translations,
    parse_translator_response,
    translate_to_english,
)


def _article(titulo: str = "Zero-day crítico") -> RankedArticle:
    return RankedArticle(
        titulo=titulo,
        resumo="Exploração ativa observada por múltiplos grupos.",
        por_que_importa="Ambientes expostos têm superfície imediata.",
        gancho_conversa="Vale forçar conversa com o CISO essa semana.",
        leitura_comercial="Clientes do setor financeiro vão perguntar sobre o tema.",
        fonte="Fixture",
        url="https://example.com/zero-day",
        data_publicacao=datetime(2026, 4, 22, 10, 0, tzinfo=timezone.utc),
    )


def _translation(id_: int = 0) -> dict:
    return {
        "id": id_,
        "titulo": "Critical zero-day",
        "resumo": "Active exploitation observed across multiple groups.",
        "por_que_importa": "Exposed environments have immediate surface.",
        "gancho_conversa": "Worth forcing a conversation with the CISO this week.",
        "leitura_comercial": "Financial-sector clients will ask about this.",
    }


def test_parse_clean_json_array():
    raw = json.dumps([_translation()])
    out = parse_translator_response(raw)
    assert isinstance(out, list)
    assert out[0]["titulo"] == "Critical zero-day"


def test_parse_with_json_code_fence():
    raw = "```json\n" + json.dumps([_translation()]) + "\n```"
    out = parse_translator_response(raw)
    assert len(out) == 1


def test_parse_with_plain_code_fence():
    raw = "```\n" + json.dumps([_translation()]) + "\n```"
    out = parse_translator_response(raw)
    assert len(out) == 1


def test_parse_rejects_non_array():
    with pytest.raises(ValueError):
        parse_translator_response('{"not": "an array"}')


def test_apply_translations_preserves_metadata():
    original = _article()
    result = apply_translations([original], [_translation()])
    assert len(result) == 1
    t = result[0]
    assert t.titulo == "Critical zero-day"
    assert t.resumo == "Active exploitation observed across multiple groups."
    # Metadata preserved from the original (not translated)
    assert t.fonte == original.fonte
    assert str(t.url) == str(original.url)
    assert t.data_publicacao == original.data_publicacao


def test_apply_translations_matches_by_id_not_order():
    a1 = _article("Primeiro")
    a2 = _article("Segundo")
    t2 = {**_translation(id_=1), "titulo": "Second"}
    t1 = {**_translation(id_=0), "titulo": "First"}
    # Pass translations in reversed order — apply should match by id
    result = apply_translations([a1, a2], [t2, t1])
    assert result[0].titulo == "First"
    assert result[1].titulo == "Second"


def test_apply_translations_rejects_count_mismatch():
    with pytest.raises(ValueError, match="count mismatch"):
        apply_translations([_article(), _article()], [_translation()])


def test_apply_translations_rejects_missing_id():
    bad = _translation()
    del bad["id"]
    with pytest.raises(ValueError, match="missing 'id'"):
        apply_translations([_article()], [bad])


def test_apply_translations_rejects_missing_id_value():
    # Two translations, but neither has id=1
    t1 = _translation(id_=0)
    t2 = {**_translation(id_=0), "titulo": "Dup"}
    with pytest.raises(ValueError, match="missing id="):
        apply_translations([_article(), _article()], [t1, t2])


def test_translate_empty_returns_empty():
    assert translate_to_english([]) == []
