# painel-jarvis

[![panel-jarvis: ¿qué falló hoy? Tu Jarvis responde](guia/assets/banner-es.jpg)](https://inematds.github.io/painel-jarvis/guia/es/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md) · [Guide/Guía](https://inematds.github.io/painel-jarvis/guia/es/)**

## Qué es

Quienes dejan cosas ejecutándose solas en la computadora (un asistente, una copia de seguridad, un robot que publica videos, un sitio web) suelen enterarse de que algo se rompió solo cuando alguien se queja. painel-jarvis es un pequeño programa en Python que revisa todo eso por ti: la memoria y el disco de la máquina, los servicios, las rutinas, los sitios web y los cambios en tus proyectos. Puedes verlo en un panel que se abre en el celular como una app, o simplemente preguntarle a tu asistente de IA: «¿qué falló hoy?». Necesitas una computadora con Linux y Python 3.11 o posterior.

Por ahora, los mensajes del programa y el panel web están en portugués.

## 📖 Guía de uso

Guía completa (página de presentación + paso a paso): **https://inematds.github.io/painel-jarvis/guia/es/**

Python puro (solo la biblioteca estándar, 3.11+). Un núcleo, tres formas de usarlo:

| Forma | Para qué sirve | Comando |
|---|---|---|
| Plugin de **INTELECTO v2** | Tu Jarvis en Python obtiene las herramientas `painel_resumo`, `painel_falhas` y `painel_quadro` | `INTELECTO_PLUGINS=painel intelecto` |
| Servidor **MCP** | Cualquier agente compatible con MCP (Claude Code, Codex, Cursor, otro Jarvis) usa las mismas herramientas | `claude mcp add painel -- painel-jarvis mcp` |
| **Panel web** instalable | Tarjetas en el navegador y el celular (PWA), protegidas con contraseña | `painel-jarvis web` |

## Los paneles

Cada sección de `painel.toml` activa un panel. Todo es de solo lectura.

| Panel | Qué muestra | Se pone amarillo/rojo cuando |
|---|---|---|
| `maquina` | memoria, disco, carga, GPU (nvidia-smi) | queda menos del 10 % de memoria libre, disco ≥ 90 % |
| `servicos` | servicios y temporizadores de systemd | falla un servicio, se detiene un temporizador o la unidad no existe |
| `rotinas` | rutinas de cron según el registro | hay errores en las últimas líneas o se supera el plazo sin actividad |
| `sites` | una solicitud GET ligera por sitio | el sitio está fuera de servicio |
| `git` | lo que hicimos: commits de las últimas 24 h y de los últimos 7 días | — |
| `uso` | cualquier JSON que escriba otro script (visitas, ventas, cola) | el archivo no se actualiza dentro del plazo |

El panel `uso` conecta tus datos: tu script los recopila (y decide si puede llamar a alguna API) y los guarda en un JSON; el panel solo lo lee.

## Instalación

```bash
pipx install git+https://github.com/inematds/painel-jarvis    # o pip install en un venv (activa el venv antes)
mkdir -p ~/.config/painel-jarvis
painel-jarvis exemplo > ~/.config/painel-jarvis/painel.toml   # activa la máquina; quita el "#" de las secciones que quieras
painel-jarvis cartoes                                          # revisa en la terminal
```

## El proceso de principio a fin

| # | Paso | Comando | Quién |
|---|---|---|---|
| 1 | Instalar el paquete | `pipx install git+https://github.com/inematds/painel-jarvis` | 🧠 tú |
| 2 | Escribir el `painel.toml` (qué vigilar) | `painel-jarvis exemplo > ~/.config/painel-jarvis/painel.toml` | 🧠 tú |
| 3 | Revisar los paneles en la terminal | `painel-jarvis cartoes` · `painel-jarvis falhas` | 🧠 tú |
| 4 | Conectarlo a Jarvis: INTELECTO (mismo Python: mismo venv o `pipx inject intelecto …`) | `"plugins": ["painel"]` en `config.json` o `INTELECTO_PLUGINS=painel` | 🧠 tú |
| 5 | Conectarlo a cualquier agente MCP | `claude mcp add painel -- painel-jarvis mcp` | 🧠 tú |
| 6 | Definir la contraseña del panel web | `painel-jarvis senha` | 🧠 tú |
| 7 | Mantener el panel web en funcionamiento | `painel-jarvis web --bind 0.0.0.0` (servicio systemd, ver más abajo) | ⚙️ systemd |
| 8 | Acceder desde fuera de casa | túnel (Cloudflare Tunnel, Tailscale) delante del puerto 8790 | ⚙️ túnel |
| 9 | Instalarlo en el celular | Chrome → ⋮ → Instalar app (iPhone: Compartir → Agregar a pantalla de inicio) | 🧠 tú |
| 10 | Preguntarle a Jarvis | «¿qué falló hoy?» → `painel_falhas` | 🤖 tu Jarvis |

### Servicio systemd (paso 7)

Define la contraseña antes (`painel-jarvis senha`); sin ella, el servicio solo escucha en 127.0.0.1.

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

`systemctl --user enable --now painel-jarvis` y `loginctl enable-linger $USER` (se inicia al arrancar y sigue activo después de cerrar sesión). ¿Lo instalaste en un venv? Cambia `ExecStart` por la ruta `~/.venv-painel/bin/painel-jarvis`.

## Seguridad

- Sin contraseña, el panel web solo escucha en `127.0.0.1`. Para acceder desde fuera de la máquina, usa una contraseña (scrypt, 12 caracteres o más), una cookie `HttpOnly`; 5 intentos fallidos = 15 min de espera.
- El panel no ofrece HTTPS por sí solo: para acceder por internet, usa un túnel con HTTPS delante.
- Las herramientas solo leen (`readOnlyHint` en MCP). En INTELECTO, un plugin nunca reemplaza una herramienta integrada (las restricciones de comandos siguen iguales).
- El manifiesto, `sw.js` y los íconos son públicos (no contienen datos). El service worker no guarda datos en caché.

## Pruebas

```bash
python3 -m pytest -q
```

Licencia MIT · hecho por [INEMA](https://inema.club).