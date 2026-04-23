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
OUTPUT_FILE_EN = OUTPUT_DIR / "en" / "index.html"
BRT = ZoneInfo("America/Sao_Paulo")

_MONTHS_PT = {
    1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
    5: "maio", 6: "junho", 7: "julho", 8: "agosto",
    9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro",
}

_MONTHS_EN = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December",
}

STRINGS: dict[str, dict[str, str]] = {
    "pt": {
        "lang_code": "pt-BR",
        "meta_description": "Curadoria diária de cybersecurity + IA com ângulo executivo.",
        "subtitle": "Cyber + IA",
        "section_cyber": "Top Cyber",
        "section_ai": "IA & Tech",
        "count_suffix": "hoje",
        "why_label": "Por que importa",
        "hook_tech_label": "Leitura técnica",
        "hook_biz_label": "Leitura comercial",
        "empty_cyber": "Sem curadoria de cyber hoje.",
        "empty_ai": "Sem curadoria de IA hoje.",
        "footer_prefix": "Gerado automaticamente em",
        "this_lang_label": "PT",
        "other_lang_label": "EN",
        "other_lang_href": "en/index.html",
        "other_lang_hreflang": "en",
    },
    "en": {
        "lang_code": "en",
        "meta_description": "Daily cybersecurity + AI curation with an executive angle.",
        "subtitle": "Cyber + AI",
        "section_cyber": "Top Cyber",
        "section_ai": "AI & Tech",
        "count_suffix": "today",
        "why_label": "Why it matters",
        "hook_tech_label": "Technical read",
        "hook_biz_label": "Business read",
        "empty_cyber": "No cyber curation today.",
        "empty_ai": "No AI curation today.",
        "footer_prefix": "Automatically generated at",
        "this_lang_label": "EN",
        "other_lang_label": "PT",
        "other_lang_href": "../index.html",
        "other_lang_hreflang": "pt-BR",
    },
}


def render_site(
    articles_cyber: list[RankedArticle],
    articles_ai: list[RankedArticle] | None = None,
    generated_at: datetime | None = None,
    output_file: Path = OUTPUT_FILE,
    template_dir: Path = TEMPLATE_DIR,
    lang: str = "pt",
) -> Path:
    if articles_ai is None:
        articles_ai = []
    if generated_at is None:
        generated_at = datetime.now(tz=timezone.utc)
    if lang not in STRINGS:
        raise ValueError(f"unsupported lang: {lang!r}")

    strings = STRINGS[lang]
    generated_at_brt = generated_at.astimezone(BRT)

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir),
        autoescape=True,
        undefined=jinja2.StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["to_brt"] = lambda dt: dt.astimezone(BRT)
    env.filters["short_date"] = lambda dt: _format_short_date(dt, lang)

    template = env.get_template(TEMPLATE_NAME)
    html = template.render(
        articles_cyber=articles_cyber,
        articles_ai=articles_ai,
        lang=lang,
        strings=strings,
        data_formatada=_format_long_date(generated_at_brt, lang),
        gerado_em=_format_timestamp(generated_at_brt, lang),
    )

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(html, encoding="utf-8")
    log.info(
        "wrote %s (lang=%s, %d cyber, %d ai)",
        output_file,
        lang,
        len(articles_cyber),
        len(articles_ai),
    )
    return output_file


def _format_long_date(dt: datetime, lang: str) -> str:
    if lang == "en":
        return f"{_MONTHS_EN[dt.month]} {dt.day}, {dt.year}"
    return f"{dt.day} de {_MONTHS_PT[dt.month]} de {dt.year}"


def _format_short_date(dt: datetime, lang: str) -> str:
    if lang == "en":
        return dt.strftime("%Y-%m-%d")
    return dt.strftime("%d/%m/%Y")


def _format_timestamp(dt: datetime, lang: str) -> str:
    if lang == "en":
        return dt.strftime("%Y-%m-%d %H:%M (BRT)")
    return dt.strftime("%d/%m/%Y %H:%M (BRT)")
