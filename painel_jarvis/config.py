"""Configuração em painel.toml (stdlib: tomllib). Cada seção liga um quadro; sem a seção, o quadro não aparece.

Procura, nesta ordem: $PAINEL_JARVIS_CONFIG, ./painel.toml, ~/.config/painel-jarvis/painel.toml.
Sem arquivo nenhum, liga só o quadro da máquina (funciona em qualquer Linux).
"""
import os

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    tomllib = None

PASTA = os.path.expanduser(os.environ.get("PAINEL_JARVIS_HOME", "~/.config/painel-jarvis"))
PADRAO = {"painel": {"titulo": "Painel", "atualizar_s": 60}, "maquina": {"disco": "/"}}


def caminho():
    for c in (os.environ.get("PAINEL_JARVIS_CONFIG"), "painel.toml", os.path.join(PASTA, "painel.toml")):
        if c and os.path.isfile(c):
            return c
    return None


def carregar(arq=None):
    arq = arq or caminho()
    if not arq:
        return dict(PADRAO)
    if tomllib is None:
        raise RuntimeError("painel.toml precisa de Python 3.11+ (tomllib)")
    with open(arq, "rb") as f:
        c = tomllib.load(f)
    c.setdefault("painel", {})
    c["painel"].setdefault("titulo", "Painel")
    c["painel"].setdefault("atualizar_s", 60)
    c["_arquivo"] = arq
    return c
