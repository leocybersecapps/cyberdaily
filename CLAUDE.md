# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status do projeto

**Pré-implementação.** Neste momento, o repositório contém apenas este `CLAUDE.md`. A arquitetura, stack e convenções abaixo são o *contrato alvo* — diretrizes para o código a ser escrito. Arquivos e diretórios mencionados (ex.: `src/`, `config/sources.yaml`, `templates/`, `.github/workflows/daily.yml`) ainda não existem; criá-los é parte do trabalho.

# CyberDaily — Top 5 Cyber News

Agregador diário de notícias de cybersecurity. Script agendado coleta feeds de fontes confiáveis, usa a API do Claude para rankear as 5 mais relevantes do dia, e publica um site estático.

## Objetivo do projeto

Me manter atualizado na área de cyber e me dar **ganchos de conversa** para usar com pares, clientes e prospects. O valor não está em "listar notícias" — está em destilar o que importa e explicar *por que* importa para uma audiência executiva (CISOs, heads de segurança, compradores B2B).

## Arquitetura

- **Coletor** (`src/collector/`): lê feeds RSS/Atom das fontes em `config/sources.yaml`, dedup por URL, janela de 24h.
- **Ranker** (`src/ranker/`): envia candidatos para a API do Claude (modelo Sonnet), retorna JSON estruturado com top 5.
- **Publisher** (`src/publisher/`): renderiza `index.html` estático a partir de template + JSON, grava em `docs/` (servido pelo GitHub Pages).
- **Scheduler**: GitHub Actions workflow em `.github/workflows/daily.yml`, roda 1x/dia de manhã (horário de Brasília).

Fluxo: `collect → rank → publish → commit → deploy`. Tudo idempotente; rodar 2x no mesmo dia sobrescreve a saída.

## Stack

- Python 3.11+, `feedparser`, `httpx`, `pydantic`, `jinja2`, `anthropic` (SDK oficial).
- Gerenciamento de deps: `uv` (preferência) ou `pip` com `requirements.txt`.
- Frontend: HTML/CSS puro, sem build step, sem JS framework. Tailwind via CDN é aceitável.
- Testes: `pytest`. Rodar com `uv run pytest` antes de qualquer commit que mexa em `src/`.

## Princípios de segurança (críticos — é um projeto de cyber)

- **Zero coleta de dados do usuário final.** Nada de cookies, analytics, fontes externas com tracking, formulários. Site é 100% estático e read-only.
- **Sem dependências sketchy.** Qualquer lib nova precisa ser mainstream (>1k stars, mantida). Em dúvida, me pergunte.
- **Secrets só via variáveis de ambiente** (`ANTHROPIC_API_KEY`). Nunca em código, nunca em commit. GitHub Actions usa `secrets.`.
- **CSP restritiva no HTML final.** `default-src 'self'; script-src 'none'` se possível. Sem inline scripts.
- **Feeds sempre por HTTPS.** Rejeitar fonte que não sirva TLS válido.

## Critérios de ranqueamento (do prompt enviado ao Claude)

O prompt do ranker deve instruir o modelo a priorizar, nesta ordem:
1. Impacto real (zero-day ativamente explorado, CVE crítico com PoC, breach de escala relevante, nova regulação que afeta CISOs BR).
2. Relevância para conversa executiva (algo que um CISO/CSO citaria numa reunião essa semana).
3. Diversidade temática (não 5 itens sobre o mesmo incidente — agrupar quando repetido).
4. Fonte confiável (ver `config/sources.yaml` — tiers 1 e 2 preferidos).

Cada item do top 5 deve retornar: `titulo`, `resumo` (2-3 linhas), `por_que_importa` (1 linha), `gancho_conversa` (1 linha pensada para cliente/prospect), `fonte`, `url`, `data_publicacao`.

## Convenções de código

- Type hints em todo código novo. `pydantic.BaseModel` para qualquer dado que entra ou sai de API/arquivo.
- Logging estruturado (`logging` stdlib é suficiente), nível `INFO` padrão, `DEBUG` via env var.
- Funções pequenas e testáveis. Side effects (I/O, rede) isolados em módulos de borda.
- Commits: Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`).
- Não deixar `print()` ou código comentado em PRs.

## Coisas que eu NÃO quero

- Banco de dados. Se precisar persistir algo além do HTML gerado, primeiro discute comigo.
- Backend dinâmico. Nada de Flask/FastAPI servindo requests — é site estático.
- Frameworks JS (React, Vue, etc). Overkill pra esse caso.
- Analytics de qualquer tipo (GA, Plausible, etc) — viola o princípio de zero tracking.
- Over-engineering. Prefira solução simples e legível a solução "arquiteturalmente elegante".

## Comandos úteis

```bash
uv sync                          # instalar deps
uv run python -m src.pipeline    # rodar pipeline completo localmente
uv run pytest                    # rodar testes
uv run python -m src.collector   # só coletar (debug)
uv run python -m src.ranker      # só rankear (usa cache do collector)
```

## Referências

- Lista de fontes e tiers: `@config/sources.yaml`
- Prompt do ranker: `@src/ranker/prompt.md`
- Template do site: `@templates/index.html.j2`
