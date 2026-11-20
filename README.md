# painel-jarvis

<div align="center">
  <img src="capa/logo.svg" alt="Arckhé AI" height="48" />
  <p><strong>Arckhé AI</strong></p>
</div>


[![painel-jarvis: o que falhou hoje? Seu Jarvis responde](guia/assets/banner.jpg)](https://inematds.github.io/painel-jarvis/guia/)

**ðŸ‡§ðŸ‡· [PortuguÃªs](README.md) Â· ðŸ‡ºðŸ‡¸ [English](README.en.md) Â· ðŸ‡ªðŸ‡¸ [EspaÃ±ol](README.es.md)**

## O que Ã©

Quem deixa coisas rodando sozinhas no computador (um assistente, um backup, um robÃ´ que publica vÃ­deo, um site) costuma saber que algo quebrou sÃ³ quando alguÃ©m reclama. O painel-jarvis Ã© um pequeno programa em Python que olha tudo isso por vocÃª: memÃ³ria e disco da mÃ¡quina, serviÃ§os, rotinas, sites e o que mudou nos seus projetos. VocÃª vÃª num painel que abre no celular como um app, ou simplesmente pergunta ao seu assistente de IA "o que falhou hoje?". Precisa de um computador com Linux e Python 3.11 ou mais novo.

## ðŸ“– Guia de uso

Guia completo (landing + passo a passo): **https://inematds.github.io/painel-jarvis/guia/**

Python puro (sÃ³ a biblioteca padrÃ£o, 3.11+). Um nÃºcleo, trÃªs jeitos de usar:

| Jeito | Para quÃª | Comando |
|---|---|---|
| Plugin do **INTELECTO v2** | o seu Jarvis em Python ganha as ferramentas `painel_resumo`, `painel_falhas` e `painel_quadro` | `INTELECTO_PLUGINS=painel intelecto` |
| Servidor **MCP** | qualquer agente que fale MCP (Claude Code, Codex, Cursor, outro Jarvis) usa as mesmas ferramentas | `claude mcp add painel -- painel-jarvis mcp` |
| **Painel web** instalÃ¡vel | cards no navegador e no celular (PWA), com senha | `painel-jarvis web` |

## Os quadros

Cada seÃ§Ã£o do `painel.toml` liga um quadro. Tudo Ã© sÃ³ leitura.

| Quadro | O que mostra | Fica amarelo/vermelho quando |
|---|---|---|
| `maquina` | memÃ³ria, disco, carga, GPU (nvidia-smi) | memÃ³ria < 10 % livre, disco â‰¥ 90 % |
| `servicos` | serviÃ§os e timers do systemd | serviÃ§o falhou, timer parado, unidade nÃ£o existe |
| `rotinas` | rotinas do cron pelo log | erro nas Ãºltimas linhas, ou parada alÃ©m do prazo |
| `sites` | um GET leve por site | site fora do ar |
| `git` | o que fizemos: commits de 24 h e 7 dias | â€” |
| `uso` | qualquer JSON que outro script grava (visitas, vendas, fila) | arquivo parado alÃ©m do prazo |

O quadro `uso` Ã© a ponte para os seus nÃºmeros: o seu script coleta (e decide se pode chamar alguma API) e grava um JSON; o painel sÃ³ lÃª.

## Instalar

```bash
pipx install git+https://github.com/inematds/painel-jarvis    # ou pip install num venv (ative o venv antes)
mkdir -p ~/.config/painel-jarvis
painel-jarvis exemplo > ~/.config/painel-jarvis/painel.toml   # liga a mÃ¡quina; tire o "#" das seÃ§Ãµes que quiser
painel-jarvis cartoes                                          # confere no terminal
```

## O processo, do inÃ­cio ao fim

| # | Passo | Comando | Quem |
|---|---|---|---|
| 1 | Instalar o pacote | `pipx install git+https://github.com/inematds/painel-jarvis` | ðŸ§  vocÃª |
| 2 | Escrever o `painel.toml` (o que vigiar) | `painel-jarvis exemplo > ~/.config/painel-jarvis/painel.toml` | ðŸ§  vocÃª |
| 3 | Conferir os quadros no terminal | `painel-jarvis cartoes` Â· `painel-jarvis falhas` | ðŸ§  vocÃª |
| 4 | Ligar no Jarvis: INTELECTO (mesmo Python: mesmo venv ou `pipx inject intelecto â€¦`) | `"plugins": ["painel"]` no `config.json` ou `INTELECTO_PLUGINS=painel` | ðŸ§  vocÃª |
| 5 | Ligar em qualquer agente MCP | `claude mcp add painel -- painel-jarvis mcp` | ðŸ§  vocÃª |
| 6 | Definir a senha do painel web | `painel-jarvis senha` | ðŸ§  vocÃª |
| 7 | Deixar o painel web no ar | `painel-jarvis web --bind 0.0.0.0` (serviÃ§o systemd, ver abaixo) | âš™ï¸ systemd |
| 8 | Abrir fora de casa | tÃºnel (Cloudflare Tunnel, Tailscale) na frente da porta 8790 | âš™ï¸ tÃºnel |
| 9 | Instalar no celular | Chrome â†’ â‹® â†’ Instalar app (iPhone: Compartilhar â†’ Tela de InÃ­cio) | ðŸ§  vocÃª |
| 10 | Perguntar ao Jarvis | "o que falhou hoje?" â†’ `painel_falhas` | ðŸ¤– seu Jarvis |

### ServiÃ§o systemd (passo 7)

Defina a senha antes (`painel-jarvis senha`); sem ela o serviÃ§o fica sÃ³ em 127.0.0.1.

```bash
mkdir -p ~/.config/systemd/user
cat > ~/.config/systemd/user/painel-jarvis.service <<'FIM'
[Unit]
Description=painel-jarvis web
[Service]
ExecStart=%h/.local/bin/painel-jarvis web --bind 0.0.0.0
Restart=on-failure
[Install]
WantedBy=default.target
FIM
systemctl --user daemon-reload
```

`systemctl --user enable --now painel-jarvis` e `loginctl enable-linger $USER` (sobe no boot e nÃ£o morre no logout). Instalou num venv? Troque o `ExecStart` pelo caminho `~/.venv-painel/bin/painel-jarvis`.

## SeguranÃ§a

- Sem senha, o painel web sÃ³ escuta em `127.0.0.1`. Fora da mÃ¡quina, sÃ³ com senha (scrypt, 12+ caracteres), cookie `HttpOnly`, 5 tentativas erradas = 15 min de espera.
- O painel nÃ£o fala HTTPS sozinho: para abrir pela internet, use um tÃºnel com HTTPS na frente.
- As ferramentas sÃ³ leem (`readOnlyHint` no MCP). No INTELECTO, um plugin nunca substitui uma ferramenta de fÃ¡brica (a trava de comandos continua a mesma).
- O manifesto, o `sw.js` e os Ã­cones sÃ£o pÃºblicos (nÃ£o tÃªm dado). O service worker nÃ£o guarda dado em cache.

## Testes

```bash
python3 -m pytest -q
```

LicenÃ§a MIT Â· feito pelo [INEMA](https://inema.club).

---

<div align="center">
  <img src="capa/logo.svg" alt="Arckhé AI" height="32" />
  <p><strong>Arckhé AI</strong></p>
</div>