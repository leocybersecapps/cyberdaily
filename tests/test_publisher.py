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
        fonte="Fixture",
        url="https://example.com/zero-day",
        data_publicacao=datetime(2026, 4, 22, 10, 0, tzinfo=timezone.utc),
    )


def test_render_writes_file_with_content(tmp_path: Path):
    out = tmp_path / "index.html"
    render_site(
        [_article("Breach massivo"), _article("Zero-day crítico")],
        generated_at=datetime(2026, 4, 22, 9, 30, tzinfo=timezone.utc),
        output_file=out,
    )
    html = out.read_text(encoding="utf-8")

    assert "CyberDaily" in html
    assert "Breach massivo" in html
    assert "Zero-day crítico" in html
    assert "22 de abril de 2026" in html
    assert "22/04/2026" in html
    assert 'href="https://example.com/zero-day"' in html


def test_render_escapes_html_in_fields(tmp_path: Path):
    article = _article('Alerta <script>alert("x")</script>')
    out = tmp_path / "index.html"
    render_site([article], output_file=out)
    html = out.read_text(encoding="utf-8")

    # Jinja autoescape must neutralize the payload
    assert '<script>alert("x")</script>' not in html
    assert "&lt;script&gt;" in html


def test_render_empty_shows_placeholder(tmp_path: Path):
    out = tmp_path / "index.html"
    render_site([], output_file=out)
    html = out.read_text(encoding="utf-8")
    assert "Sem notícias disponíveis hoje." in html


def test_render_includes_csp_header(tmp_path: Path):
    out = tmp_path / "index.html"
    render_site([_article()], output_file=out)
    html = out.read_text(encoding="utf-8")
    assert "Content-Security-Policy" in html
    assert "default-src 'none'" in html
    assert "script-src" not in html  # scripts blocked via default-src 'none'
