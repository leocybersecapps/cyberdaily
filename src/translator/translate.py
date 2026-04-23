import json
import logging
import re
from pathlib import Path

from anthropic import Anthropic

from src.models import RankedArticle


log = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent / "prompt.md"

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 4096
TEMPERATURE = 0.2

_FENCE_RE = re.compile(r"^```(?:json)?\s*\n(.*?)\n```\s*$", re.DOTALL)


def translate_to_english(
    articles: list[RankedArticle],
    client: Anthropic | None = None,
) -> list[RankedArticle]:
    if not articles:
        return []

    client = client or Anthropic()
    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    user_message = _build_user_message(articles)

    log.info("translating %d articles to EN with %s", len(articles), MODEL)
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_message}],
    )

    text = _extract_text(response)
    translations = parse_translator_response(text)
    return apply_translations(articles, translations)


def parse_translator_response(raw: str) -> list[dict]:
    text = raw.strip()
    fence = _FENCE_RE.match(text)
    if fence:
        text = fence.group(1).strip()

    parsed = json.loads(text)
    if not isinstance(parsed, list):
        raise ValueError(f"expected JSON array, got {type(parsed).__name__}")
    return parsed


def apply_translations(
    originals: list[RankedArticle], translations: list[dict]
) -> list[RankedArticle]:
    if len(translations) != len(originals):
        raise ValueError(
            f"translation count mismatch: expected {len(originals)}, "
            f"got {len(translations)}"
        )
    by_id: dict[int, dict] = {}
    for t in translations:
        if "id" not in t:
            raise ValueError("translation item missing 'id'")
        by_id[int(t["id"])] = t

    out: list[RankedArticle] = []
    for i, original in enumerate(originals):
        t = by_id.get(i)
        if t is None:
            raise ValueError(f"translation missing id={i}")
        out.append(
            RankedArticle(
                titulo=t["titulo"],
                resumo=t["resumo"],
                por_que_importa=t["por_que_importa"],
                gancho_conversa=t["gancho_conversa"],
                leitura_comercial=t["leitura_comercial"],
                fonte=original.fonte,
                url=str(original.url),
                data_publicacao=original.data_publicacao,
            )
        )
    return out


def _build_user_message(articles: list[RankedArticle]) -> str:
    payload = [
        {
            "id": i,
            "titulo": a.titulo,
            "resumo": a.resumo,
            "por_que_importa": a.por_que_importa,
            "gancho_conversa": a.gancho_conversa,
            "leitura_comercial": a.leitura_comercial,
        }
        for i, a in enumerate(articles)
    ]
    return (
        "Itens curados (pt-BR) para traduzir para inglês:\n\n"
        + json.dumps(payload, ensure_ascii=False, indent=2)
    )


def _extract_text(response) -> str:
    for block in response.content:
        if getattr(block, "type", None) == "text":
            return block.text
    raise ValueError("no text block in translator response")
