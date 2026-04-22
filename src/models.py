from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


Tier = Literal[1, 2]


class Source(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    url: HttpUrl
    tier: Tier
    tags: list[str] = Field(default_factory=list)

    @field_validator("url")
    @classmethod
    def require_https(cls, v: HttpUrl) -> HttpUrl:
        if v.scheme != "https":
            raise ValueError(f"URL must use HTTPS, got: {v}")
        return v


class RawArticle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    url: HttpUrl
    summary: str = ""
    published_at: datetime
    source_name: str
    source_tier: Tier


class RankedArticle(BaseModel):
    """Output of the ranker — the exact shape the site template consumes.

    Field names are Portuguese by design (per CLAUDE.md ranking spec).
    """

    model_config = ConfigDict(extra="forbid")

    titulo: str
    resumo: str
    por_que_importa: str
    gancho_conversa: str
    fonte: str
    url: HttpUrl
    data_publicacao: datetime
