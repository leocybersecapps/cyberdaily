from datetime import datetime, timezone
from pathlib import Path

from src.models import RankedArticle
from src.publisher.render import render_site


def _article(titulo: str = "Zero-day no Widget Engine") -> RankedArticle:
    return RankedArticle(
        titulo=titulo,
        resumo="Exploração ativa observada por múltiplos grupos.",
        por_que_importa="Ambientes expostos têm superfície imediata.",
        gancho_conversa="Vale forçar conversa com o CISO essa semana.",
        leitura_comercial="Clientes do setor financeiro vão perguntar sobre o tema — boa deixa para reabrir conversa.",
        fonte="Fixture",
        url="https://example.com/zero-day",
        data_publicacao=datetime(2026, 4, 22, 10, 0, tzinfo=timezone.utc),
    )


def _ai_article(titulo: str = "GPT-X lançado em GA") -> RankedArticle:
    return RankedArticle(
        titulo=titulo,
        resumo="Vendor anunciou novo modelo com SLA enterprise.",
        por_que_importa="Muda a conta de POC para produção para quem esperava GA.",
        gancho_conversa="Quem barrou POC por 'risco de suporte' perdeu o argumento essa semana.",
        leitura_comercial="Clientes com projeto de IA parado por falta de garantia enterprise agora têm argumento para destravar orçamento.",
        fonte="OpenAI News",
        url="https://example.com/gpt-x",
        data_publicacao=datetime(2026, 4, 22, 12, 0, tzinfo=timezone.utc),
    )


def test_render_writes_file_with_content(tmp_path: Path):
    out = tmp_path / "index.html"
    render_site(
        [_article("Breach massivo"), _article("Zero-day crítico")],
        [_ai_article("Novo modelo GA")],
        generated_at=datetime(2026, 4, 22, 9, 30, tzinfo=timezone.utc),
        output_file=out,
    )
    html = out.read_text(encoding="utf-8")

    assert "CyberDaily" in html
    assert "Breach massivo" in html
    assert "Zero-day crítico" in html
    assert "Novo modelo GA" in html
    assert "22 de abril de 2026" in html
    assert "22/04/2026" in html
    assert 'href="https://example.com/zero-day"' in html
    assert 'href="https://example.com/gpt-x"' in html


def test_render_has_both_sections(tmp_path: Path):
    out = tmp_path / "index.html"
    render_site([_article()], [_ai_article()], output_file=out)
    html = out.read_text(encoding="utf-8")
    assert "section-cyber" in html
    assert "section-ai" in html
    assert "Top Cyber" in html
    assert "IA &amp; Tech" in html


def test_render_shows_both_tech_and_biz_hooks(tmp_path: Path):
    out = tmp_path / "index.html"
    render_site([_article()], [_ai_article()], output_file=out)
    html = out.read_text(encoding="utf-8")
    # Both labels present
    assert "Leitura técnica" in html
    assert "Leitura comercial" in html
    # Both content fields rendered
    assert "Vale forçar conversa com o CISO essa semana." in html
    assert "reabrir conversa" in html  # from _article leitura_comercial
    assert "destravar orçamento" in html  # from _ai_article leitura_comercial


def test_render_uses_brt_timezone(tmp_path: Path):
    # UTC 02:00 on 2026-04-23 == BRT 23:00 on 2026-04-22.
    out = tmp_path / "index.html"
    render_site(
        [_article()],
        [_ai_article()],
        generated_at=datetime(2026, 4, 23, 2, 0, tzinfo=timezone.utc),
        output_file=out,
    )
    html = out.read_text(encoding="utf-8")

    assert "22 de abril de 2026" in html  # BRT-adjusted header date
    assert "22/04/2026 23:00 (BRT)" in html  # BRT-adjusted footer stamp
    assert "UTC" not in html


def test_article_date_converted_to_brt(tmp_path: Path):
    # UTC 01:30 on 2026-04-22 == BRT 22:30 on 2026-04-21.
    article = RankedArticle(
        titulo="Notícia madrugada",
        resumo="R",
        por_que_importa="P",
        gancho_conversa="G",
        leitura_comercial="L",
        fonte="F",
        url="https://example.com/n",
        data_publicacao=datetime(2026, 4, 22, 1, 30, tzinfo=timezone.utc),
    )
    out = tmp_path / "index.html"
    render_site([article], output_file=out)
    html = out.read_text(encoding="utf-8")

    assert "21/04/2026" in html
    assert "22/04/2026" not in html.split("<span class=\"date\">")[1].split("</span>")[0]


def test_render_escapes_html_in_fields(tmp_path: Path):
    article = _article('Alerta <script>alert("x")</script>')
    out = tmp_path / "index.html"
    render_site([article], output_file=out)
    html = out.read_text(encoding="utf-8")

    # Jinja autoescape must neutralize the payload
    assert '<script>alert("x")</script>' not in html
    assert "&lt;script&gt;" in html


def test_render_empty_cyber_shows_placeholder(tmp_path: Path):
    out = tmp_path / "index.html"
    render_site([], [_ai_article()], output_file=out)
    html = out.read_text(encoding="utf-8")
    assert "Sem curadoria de cyber hoje." in html


def test_render_empty_ai_shows_placeholder(tmp_path: Path):
    out = tmp_path / "index.html"
    render_site([_article()], [], output_file=out)
    html = out.read_text(encoding="utf-8")
    assert "Sem curadoria de IA hoje." in html


def test_render_both_empty_shows_both_placeholders(tmp_path: Path):
    out = tmp_path / "index.html"
    render_site([], [], output_file=out)
    html = out.read_text(encoding="utf-8")
    assert "Sem curadoria de cyber hoje." in html
    assert "Sem curadoria de IA hoje." in html


def test_ai_articles_default_to_empty_when_omitted(tmp_path: Path):
    out = tmp_path / "index.html"
    render_site([_article()], output_file=out)
    html = out.read_text(encoding="utf-8")
    assert "Sem curadoria de IA hoje." in html


def test_render_includes_csp_header(tmp_path: Path):
    out = tmp_path / "index.html"
    render_site([_article()], output_file=out)
    html = out.read_text(encoding="utf-8")
    assert "Content-Security-Policy" in html
    assert "default-src 'none'" in html
    assert "script-src" not in html  # scripts blocked via default-src 'none'


def test_render_pt_has_language_switcher_to_en(tmp_path: Path):
    out = tmp_path / "index.html"
    render_site([_article()], [_ai_article()], output_file=out, lang="pt")
    html = out.read_text(encoding="utf-8")
    assert 'lang="pt-BR"' in html
    assert 'href="en/index.html"' in html
    assert 'hreflang="en"' in html


def test_render_en_writes_english_content(tmp_path: Path):
    out = tmp_path / "en" / "index.html"
    article_en = RankedArticle(
        titulo="Critical zero-day in Widget Engine",
        resumo="Active exploitation observed across multiple groups.",
        por_que_importa="Exposed environments have immediate surface.",
        gancho_conversa="Worth forcing a conversation with the CISO this week.",
        leitura_comercial="Financial-sector clients will ask about response plans — good reopener.",
        fonte="Fixture",
        url="https://example.com/zero-day",
        data_publicacao=datetime(2026, 4, 22, 10, 0, tzinfo=timezone.utc),
    )
    render_site(
        [article_en],
        [],
        generated_at=datetime(2026, 4, 22, 9, 30, tzinfo=timezone.utc),
        output_file=out,
        lang="en",
    )
    html = out.read_text(encoding="utf-8")

    assert 'lang="en"' in html
    assert "Critical zero-day in Widget Engine" in html
    assert "Why it matters" in html
    assert "Technical read" in html
    assert "Business read" in html
    assert "No AI curation today." in html
    assert "April 22, 2026" in html
    assert "2026-04-22" in html  # short date in EN
    assert 'href="../index.html"' in html
    assert 'hreflang="pt-BR"' in html
    # PT-only strings must not leak
    assert "Por que importa" not in html
    assert "Leitura técnica" not in html
    assert "Sem curadoria" not in html


def test_render_rejects_unknown_lang(tmp_path: Path):
    import pytest as _pytest
    with _pytest.raises(ValueError):
        render_site([_article()], output_file=tmp_path / "x.html", lang="fr")
