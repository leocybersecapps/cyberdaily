import logging
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import jinja2

from src.models import RankedArticle


log = logging.getLogger(__name__)

TEMPLATE_DIR = Path("templates")
TEMPLATE_NAME = "index.html.j2"
OUTPUT_DIR = Path("docs")
OUTPUT_FILE = OUTPUT_DIR / "index.html"
BRT = ZoneInfo("America/Sao_Paulo")

_MONTHS_PT = {
    1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
    5: "maio", 6: "junho", 7: "julho", 8: "agosto",
    9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro",
}


def render_site(
    articles: list[RankedArticle],
    generated_at: datetime | None = None,
    output_file: Path = OUTPUT_FILE,
    template_dir: Path = TEMPLATE_DIR,
) -> Path:
    if generated_at is None:
        generated_at = datetime.now(tz=timezone.utc)

    generated_at_brt = generated_at.astimezone(BRT)

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir),
        autoescape=True,
        undefined=jinja2.StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["to_brt"] = lambda dt: dt.astimezone(BRT)

    template = env.get_template(TEMPLATE_NAME)
    html = template.render(
        articles=articles,
        data_formatada=_format_date_pt(generated_at_brt),
        gerado_em=generated_at_brt.strftime("%d/%m/%Y %H:%M (BRT)"),
    )

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(html, encoding="utf-8")
    log.info("wrote %s (%d articles)", output_file, len(articles))
    return output_file


def _format_date_pt(dt: datetime) -> str:
    return f"{dt.day} de {_MONTHS_PT[dt.month]} de {dt.year}"
