# CLAUDE.md — painel-jarvis

Painel da máquina e das rotinas como plugin de Jarvis (INTELECTO v2, MCP) e PWA no celular. Python puro (stdlib, 3.11+).
Repo público `inematds/painel-jarvis`, autor `inematds <inematds@gmail.com>`. Publicação = commit + push.

- Testes: `python3 -m pytest -q` passam antes de todo commit. Sem dependência obrigatória.
- Todo coletor só LÊ (disco, /proc, systemctl show, git log, GET de site, JSON local). Nada de API com chave aqui: dado de serviço externo entra pelo quadro `uso` (JSON que outro script grava).
- Coletor quebrado vira cartão "sem leitura"; nunca derruba o painel.
- Nasceu do painel do v3 (`openpcbotv3`, ccc.inema.pro) em 14/11/2026; o v3 continua com os quadros privados (PIX, filas dos bots, Supabase).
- Guia em `guia/` (PT) + `guia/en/` + `guia/es/`; README em 3 idiomas. Mudou o fluxo, atualize a tabela "O processo, do início ao fim" no mesmo commit.

## Self-learning

Quando eu for corrigido ou perceber um erro: antes de seguir, acrescente a lição como regra de uma linha no TOPO de `## Lessons`.

## Lessons
- `systemctl show` de unidade que não existe responde ActiveState=inactive e Result=success: confira `LoadState=not-found` antes, senão ela aparece "em ordem" (14/11/2026).
