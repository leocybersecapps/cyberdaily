import json
import logging
import re
from pathlib import Path

from anthropic import Anthropic

from src.models import RankedArticle, RawArticle


log = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent / "prompt.md"
MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 4096
TEMPERATURE = 0.3

_FENCE_RE = re.compile(r"^```(?:json)?\s*\n(.*?)\n```\s*$", re.DOTALL)


def rank_articles(
    candidates: list[RawArticle],
    client: Anthropic | None = None,
) -> list[RankedArticle]:
    if not candidates:
        log.warning("no candidates to rank")
        return []

    client = client or Anthropic()
    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    user_message = _build_user_message(candidates)

    log.info("ranking %d candidates with %s", len(candidates), MODEL)
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
    return parse_ranker_response(text)


def parse_ranker_response(raw: str) -> list[RankedArticle]:
    text = raw.strip()
    fence = _FENCE_RE.match(text)
    if fence:
        text = fence.group(1).strip()

    parsed = json.loads(text)
    if not isinstance(parsed, list):
        raise ValueError(f"expected JSON array, got {type(parsed).__name__}")
    return [RankedArticle.model_validate(item) for item in parsed]


def _build_user_message(candidates: list[RawArticle]) -> str:
    payload = [c.model_dump(mode="json") for c in candidates]
    return (
        "Candidatas coletadas nas últimas 24h:\n\n"
        + json.dumps(payload, ensure_ascii=False, default=str, indent=2)
    )


def _extract_text(response) -> str:
    for block in response.content:
        if getattr(block, "type", None) == "text":
            return block.text
    raise ValueError("no text block in ranker response")
