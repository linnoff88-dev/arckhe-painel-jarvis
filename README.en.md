# painel-jarvis

[![painel-jarvis: what failed today? Your Jarvis answers](guia/assets/banner-en.jpg)](https://inematds.github.io/painel-jarvis/guia/en/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md) · [Guide/Guía](https://inematds.github.io/painel-jarvis/guia/en/)**

## What it is

People who leave things running unattended on their computer—an assistant, a backup, a video publishing bot, a website—often find out something broke only when someone complains. painel-jarvis is a small Python program that checks all of this for you: the computer’s memory and disk, services, scheduled tasks, websites, and what changed in your projects. You can view everything in a dashboard that opens on your phone like an app, or simply ask your AI assistant, “What failed today?” It requires a computer running Linux and Python 3.11 or later.

For now, the program’s messages and web panel are in Portuguese.

## 📖 User guide

Complete guide (landing page + walkthrough): **https://inematds.github.io/painel-jarvis/guia/en/**

Pure Python (standard library only, 3.11+). One core, three ways to use it:

| Method | Purpose | Command |
|---|---|---|
| **INTELECTO v2** plugin | Your Python Jarvis gets the `painel_resumo`, `painel_falhas`, and `painel_quadro` tools | `INTELECTO_PLUGINS=painel intelecto` |
| **MCP** server | Any agent that speaks MCP (Claude Code, Codex, Cursor, another Jarvis) can use the same tools | `claude mcp add painel -- painel-jarvis mcp` |
| Installable **web dashboard** | Cards in your browser and on your phone (PWA), protected by a password | `painel-jarvis web` |

## Dashboards

Each section in `painel.toml` enables a dashboard. Everything is read-only.

| Dashboard | What it shows | Turns yellow/red when |
|---|---|---|
| `maquina` | Memory, disk, load, GPU (`nvidia-smi`) | Free memory < 10%, disk ≥ 90% |
| `servicos` | systemd services and timers | A service fails, a timer stops, or a unit does not exist |
| `rotinas` | Cron tasks from the log | An error appears in the latest lines, or a task is overdue |
| `sites` | A lightweight GET request to each site | A site is down |
| `git` | What we’ve done: commits from the last 24 hours and 7 days | — |
| `uso` | Any JSON file written by another script (visits, sales, queue) | The file is overdue for an update |

The `uso` dashboard connects to your metrics: your script collects them (and decides whether it can call an API) and writes a JSON file; the dashboard only reads it.

## Install

```bash
pipx install git+https://github.com/inematds/painel-jarvis    # or pip install in a venv (activate the venv first)
mkdir -p ~/.config/painel-jarvis
painel-jarvis exemplo > ~/.config/painel-jarvis/painel.toml   # enables the machine; remove "#" from the sections you want
painel-jarvis cartoes                                          # check in the terminal
```

## The process, from start to finish

| # | Step | Command | Who |
|---|---|---|---|
| 1 | Install the package | `pipx install git+https://github.com/inematds/painel-jarvis` | 🧠 You |
| 2 | Write `painel.toml` (what to monitor) | `painel-jarvis exemplo > ~/.config/painel-jarvis/painel.toml` | 🧠 You |
| 3 | Check the dashboards in the terminal | `painel-jarvis cartoes` · `painel-jarvis falhas` | 🧠 You |
| 4 | Connect to Jarvis: INTELECTO (same Python environment: same venv or `pipx inject intelecto …`) | `"plugins": ["painel"]` in `config.json` or `INTELECTO_PLUGINS=painel` | 🧠 You |
| 5 | Connect to any MCP agent | `claude mcp add painel -- painel-jarvis mcp` | 🧠 You |
| 6 | Set the web dashboard password | `painel-jarvis senha` | 🧠 You |
| 7 | Keep the web dashboard running | `painel-jarvis web --bind 0.0.0.0` (systemd service, see below) | ⚙️ systemd |
| 8 | Access it from outside your home | Put a tunnel (Cloudflare Tunnel, Tailscale) in front of port 8790 | ⚙️ Tunnel |
| 9 | Install it on your phone | Chrome → ⋮ → Install app (iPhone: Share → Add to Home Screen) | 🧠 You |
| 10 | Ask Jarvis | “What failed today?” → `painel_falhas` | 🤖 Your Jarvis |

### systemd service (step 7)

Set the password first (`painel-jarvis senha`); without one, the service only listens on 127.0.0.1.

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

`systemctl --user enable --now painel-jarvis` and `loginctl enable-linger $USER` (starts at boot and keeps running after logout). Installed in a venv? Replace `ExecStart` with the path `~/.venv-painel/bin/painel-jarvis`.

## Security

- Without a password, the web dashboard only listens on `127.0.0.1`. Access from outside the computer requires a password (scrypt, 12+ characters); cookies are `HttpOnly`, and 5 failed attempts trigger a 15-minute wait.
- The dashboard does not provide HTTPS on its own. To access it over the internet, put an HTTPS tunnel in front.
- The tools only read (`readOnlyHint` in MCP). In INTELECTO, a plugin never replaces a built-in tool (the command restrictions remain the same).
- The manifest, `sw.js`, and icons are public (they contain no data). The service worker does not store data in its cache.

## Tests

```bash
python3 -m pytest -q
```

MIT License · made by [INEMA](https://inema.club).