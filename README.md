# CyberDaily

Curadoria diária de cybersecurity + IA & tech, feita com a API do Claude — com ângulo executivo para quem usa o tema como conversa de negócio.

🔗 **Site ao vivo:** https://leocybersecapps.github.io/cyberdaily/

---

## O que é

Agregador diário que:

1. Coleta feeds RSS de fontes confiáveis, divididas em duas trilhas: **cyber** (vendor threat intel, avisos oficiais, veículos de notícias) e **IA & tech** (vendors de IA, pesquisa primária, imprensa especializada).
2. Manda as candidatas de cada trilha para o Claude Sonnet, que seleciona as mais relevantes do dia (até 5 em cyber, até 3 em IA) usando critérios de impacto real, relevância executiva e diversidade temática.
3. Renderiza um site estático minimalista com as duas seções, publicado automaticamente via GitHub Pages.

**Diferencial:** cada notícia vem com um campo `gancho_conversa` — uma frase afiada, pronta para usar em reunião com CISO, cliente ou prospect. Não é resumo, é ângulo.

---

## Filosofia de segurança e privacidade

Projeto de cyber construído por gente de cyber — então leva isso a sério:

- **Zero coleta de dados do usuário.** Sem cookies, sem analytics, sem fontes externas de tracking, sem formulários.
- **Site 100% estático e read-only.** Superfície de ataque mínima.
- **CSP restritiva** (`default-src 'none'`), sem JavaScript, sem fontes web externas.
- **HTTPS obrigatório** em todos os feeds (fontes sem TLS válido são rejeitadas).
- **Secrets apenas via env vars** — nunca em código nem em commit.

---

## Arquitetura

```
collect  →  rank  →  publish
 (RSS)     (Claude)   (HTML estático)
```

| Módulo | Responsabilidade |
|---|---|
| `src/collector/` | Lê `config/sources.yaml`, baixa feeds (httpx), parseia (feedparser), dedupa por URL, filtra janela 24h |
| `src/ranker/` | Envia candidatas ao Claude Sonnet com prompts curados por trilha (`src/ranker/prompt.md` para cyber, `src/ranker/prompt_ai.md` para IA), valida JSON de resposta via pydantic |
| `src/publisher/` | Renderiza `templates/index.html.j2` com Jinja2, grava `docs/index.html` |
| `src/pipeline.py` | Orquestração: collect → rank → publish |
| `.github/workflows/daily.yml` | Cron diário (07:00 BRT) + deploy automático no GitHub Pages |

Stack: Python 3.11+, `feedparser`, `httpx`, `pydantic`, `jinja2`, `anthropic`, `pyyaml`. Frontend em HTML/CSS puro, sem build step.

---

## Faça seu próprio CyberDaily

### Setup

1. **Fork** deste repo (botão no topo da página do GitHub) ou clone e suba no seu próprio repo.
2. **Conta Anthropic:** crie em [console.anthropic.com](https://console.anthropic.com), gere uma API key. Recomendo definir um spending limit (ex: $10/mês) como seguro.
3. **Secret:** no seu fork → **Settings → Secrets and variables → Actions → New repository secret**
   - Name: `ANTHROPIC_API_KEY`
   - Secret: sua chave
4. **GitHub Pages:** repo público é suficiente (Pages em repo privado exige GitHub Pro). O workflow habilita Pages sozinho na primeira rodada.
5. **Primeira rodada:** **Actions → Daily build → Run workflow**.

Em ~3 minutos seu site está no ar em `https://<seu-user>.github.io/<nome-do-repo>/`.

### Customizar as fontes

Edite `config/sources.yaml`. Cada entrada tem o formato:

```yaml
- name: Nome legível que aparece no site
  url: https://exemplo.com/feed.xml    # HTTPS obrigatório
  tier: 1                              # 1 = primária (vendor/oficial), 2 = veículo de notícias
  category: cyber                      # "cyber" (padrão) ou "ai" — define a seção no site
  tags: [advisory, gov]                # opcional, só pra seu controle
```

Regras:
- **Só HTTPS.** Feeds em `http://` são rejeitados por segurança.
- **Tier 1 ou 2** — nada fora disso. Tier 1 tem prioridade sobre tier 2 em casos de desempate no ranqueamento.
- **Category** — `cyber` ou `ai`. Cada trilha roda com prompt dedicado e aparece numa seção separada do site. Se omitir, assume `cyber`.
- Comente linhas com `#` para desabilitar fontes temporariamente sem apagar.

Depois do push, o próximo run (manual ou agendado) já usa as fontes novas.

**Dica:** se quer focar em outra área (AppSec, cloud, OT/ICS, fraude), ajuste fontes **e** prompt juntos — fonte boa sem critério de ranqueamento adequado não funciona.

### Customizar o prompt de ranqueamento

Os prompts são o coração do produto — é o que transforma "lista de links" em "seleção com ângulo". Dois arquivos, um por trilha:

- `src/ranker/prompt.md` — cyber (até 5 itens, mínimo 3)
- `src/ranker/prompt_ai.md` — IA & tech (até 3 itens, mínimo 2)

Edite cada um para mudar foco temático, tom dos campos de saída ou critérios da sua vertical. Se quiser desligar uma trilha, basta remover as fontes daquela categoria do `sources.yaml` — o pipeline publica parcial quando uma das trilhas fica vazia.

Para iterar rápido sem pagar o cron, rode local: `uv run python -m src.ranker` (precisa do collector ter rodado antes).

### Customizar o visual

`templates/index.html.j2` tem CSS inline no mesmo arquivo. Sem build step. As variáveis CSS no `:root` controlam a paleta. Dark/light mode alternam automaticamente via `prefers-color-scheme`.

---

## Rodar localmente

```bash
uv sync                                    # instala deps
uv run pytest                              # testes offline (sem chamadas à API)
uv run python -m src.collector             # grava .cache/collected.json
uv run python -m src.ranker                # precisa ANTHROPIC_API_KEY; grava .cache/ranked_cyber.json + ranked_ai.json
uv run python -m src.publisher             # gera docs/index.html
uv run python -m src.pipeline              # end-to-end em memória
```

Para exportar a API key no Windows PowerShell:

```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-..."
```

No bash/zsh:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

---

## Custos

Rodando 1x/dia com `claude-sonnet-4-6`, duas trilhas (cyber + IA) e ~50 candidatas combinadas por run:

- ~8-12k tokens de input + ~3k tokens de output somando as duas chamadas
- **~$2-5 por mês**, dependendo do volume

---

## Licença e uso

Código disponibilizado como referência. Use, fork e adapte livremente — a ideia é que cada profissional de cyber consiga ter seu próprio resumo diário ajustado ao que importa pra ele.
