ï»¿# painel-jarvis

<div align="center">
  <img src="capa/logo.svg" alt="Arckhé AI" height="48" />
  <p><strong>Arckhé AI</strong></p>
</div>


[![painel-jarvis: o que falhou hoje? Seu Jarvis responde](guia/assets/banner.jpg)](https://inematds.github.io/painel-jarvis/guia/)

**ê°Å¸â¡Â§ê°Å¸â¡Â· [PortuguêÂªs](README.md) êÂ· ê°Å¸â¡Âºê°Å¸â¡Â¸ [English](README.en.md) êÂ· ê°Å¸â¡Âªê°Å¸â¡Â¸ [EspaêÂ±ol](README.es.md)**

## O que êÂ©

Quem deixa coisas rodando sozinhas no computador (um assistente, um backup, um robêÂ´ que publica vêÂ­deo, um site) costuma saber que algo quebrou sêÂ³ quando alguêÂ©m reclama. O painel-jarvis êÂ© um pequeno programa em Python que olha tudo isso por vocêÂª: memêÂ³ria e disco da mêÂ¡quina, serviêÂ§os, rotinas, sites e o que mudou nos seus projetos. VocêÂª vêÂª num painel que abre no celular como um app, ou simplesmente pergunta ao seu assistente de IA "o que falhou hoje?". Precisa de um computador com Linux e Python 3.11 ou mais novo.

## ê°Å¸ââ Guia de uso

Guia completo (landing + passo a passo): **https://inematds.github.io/painel-jarvis/guia/**

Python puro (sêÂ³ a biblioteca padrêÂ£o, 3.11+). Um nêÂºcleo, trêÂªs jeitos de usar:

| Jeito | Para quêÂª | Comando |
|---|---|---|
| Plugin do **INTELECTO v2** | o seu Jarvis em Python ganha as ferramentas `painel_resumo`, `painel_falhas` e `painel_quadro` | `INTELECTO_PLUGINS=painel intelecto` |
| Servidor **MCP** | qualquer agente que fale MCP (Claude Code, Codex, Cursor, outro Jarvis) usa as mesmas ferramentas | `claude mcp add painel -- painel-jarvis mcp` |
| **Painel web** instalêÂ¡vel | cards no navegador e no celular (PWA), com senha | `painel-jarvis web` |

## Os quadros

Cada seêÂ§êÂ£o do `painel.toml` liga um quadro. Tudo êÂ© sêÂ³ leitura.

| Quadro | O que mostra | Fica amarelo/vermelho quando |
|---|---|---|
| `maquina` | memêÂ³ria, disco, carga, GPU (nvidia-smi) | memêÂ³ria < 10 % livre, disco ê¢â°Â¥ 90 % |
| `servicos` | serviêÂ§os e timers do systemd | serviêÂ§o falhou, timer parado, unidade nêÂ£o existe |
| `rotinas` | rotinas do cron pelo log | erro nas êÂºltimas linhas, ou parada alêÂ©m do prazo |
| `sites` | um GET leve por site | site fora do ar |
| `git` | o que fizemos: commits de 24 h e 7 dias | ê¢â¬â |
| `uso` | qualquer JSON que outro script grava (visitas, vendas, fila) | arquivo parado alêÂ©m do prazo |

O quadro `uso` êÂ© a ponte para os seus nêÂºmeros: o seu script coleta (e decide se pode chamar alguma API) e grava um JSON; o painel sêÂ³ lêÂª.

## Instalar

```bash
pipx install git+https://github.com/inematds/painel-jarvis    # ou pip install num venv (ative o venv antes)
mkdir -p ~/.config/painel-jarvis
painel-jarvis exemplo > ~/.config/painel-jarvis/painel.toml   # liga a mêÂ¡quina; tire o "#" das seêÂ§êÂµes que quiser
painel-jarvis cartoes                                          # confere no terminal
```

## O processo, do inêÂ­cio ao fim

| # | Passo | Comando | Quem |
|---|---|---|---|
| 1 | Instalar o pacote | `pipx install git+https://github.com/inematds/painel-jarvis` | ê°Å¸Â§Â  vocêÂª |
| 2 | Escrever o `painel.toml` (o que vigiar) | `painel-jarvis exemplo > ~/.config/painel-jarvis/painel.toml` | ê°Å¸Â§Â  vocêÂª |
| 3 | Conferir os quadros no terminal | `painel-jarvis cartoes` êÂ· `painel-jarvis falhas` | ê°Å¸Â§Â  vocêÂª |
| 4 | Ligar no Jarvis: INTELECTO (mesmo Python: mesmo venv ou `pipx inject intelecto ê¢â¬Â¦`) | `"plugins": ["painel"]` no `config.json` ou `INTELECTO_PLUGINS=painel` | ê°Å¸Â§Â  vocêÂª |
| 5 | Ligar em qualquer agente MCP | `claude mcp add painel -- painel-jarvis mcp` | ê°Å¸Â§Â  vocêÂª |
| 6 | Definir a senha do painel web | `painel-jarvis senha` | ê°Å¸Â§Â  vocêÂª |
| 7 | Deixar o painel web no ar | `painel-jarvis web --bind 0.0.0.0` (serviêÂ§o systemd, ver abaixo) | ê¢Å¡â¢ê¯Â¸Â systemd |
| 8 | Abrir fora de casa | têÂºnel (Cloudflare Tunnel, Tailscale) na frente da porta 8790 | ê¢Å¡â¢ê¯Â¸Â têÂºnel |
| 9 | Instalar no celular | Chrome ê¢â â ê¢â¹Â® ê¢â â Instalar app (iPhone: Compartilhar ê¢â â Tela de InêÂ­cio) | ê°Å¸Â§Â  vocêÂª |
| 10 | Perguntar ao Jarvis | "o que falhou hoje?" ê¢â â `painel_falhas` | ê°Å¸Â¤â seu Jarvis |

### ServiêÂ§o systemd (passo 7)

Defina a senha antes (`painel-jarvis senha`); sem ela o serviêÂ§o fica sêÂ³ em 127.0.0.1.

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

`systemctl --user enable --now painel-jarvis` e `loginctl enable-linger $USER` (sobe no boot e nêÂ£o morre no logout). Instalou num venv? Troque o `ExecStart` pelo caminho `~/.venv-painel/bin/painel-jarvis`.

## SeguranêÂ§a

- Sem senha, o painel web sêÂ³ escuta em `127.0.0.1`. Fora da mêÂ¡quina, sêÂ³ com senha (scrypt, 12+ caracteres), cookie `HttpOnly`, 5 tentativas erradas = 15 min de espera.
- O painel nêÂ£o fala HTTPS sozinho: para abrir pela internet, use um têÂºnel com HTTPS na frente.
- As ferramentas sêÂ³ leem (`readOnlyHint` no MCP). No INTELECTO, um plugin nunca substitui uma ferramenta de fêÂ¡brica (a trava de comandos continua a mesma).
- O manifesto, o `sw.js` e os êÂ­cones sêÂ£o pêÂºblicos (nêÂ£o têÂªm dado). O service worker nêÂ£o guarda dado em cache.

## Testes

```bash
python3 -m pytest -q
```

LicenêÂ§a MIT êÂ· feito pelo [INEMA](https://inema.club).

---

<div align="center">
  <img src="capa/logo.svg" alt="Arckhé AI" height="32" />
  <p><strong>Arckhé AI</strong></p>
</div>