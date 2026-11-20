"""Quadro a partir de um JSON qualquer que outro script grava (estatística de site, vendas, fila...).

O painel só LÊ o arquivo: quem coleta (e decide se pode chamar alguma API) é o seu script.

[[uso]]
id = "loja"
titulo = "Loja"
arquivo = "~/.local/share/loja/uso.json"
max_horas = 30                       # arquivo mais velho que isso = aviso "parado"
frase = ["visitas em 24 h", "visitas_24h.total"]
campos = [
  ["pedidos 7 dias", "pedidos_7d"],
  ["faturamento 7 dias", "receita_7d"],
]
"""
import json
import os
import time

from ..cartao import Cartao


def pegar(dado, caminho):
    """'a.b.0.c' dentro de dicts/listas; None se não existir."""
    for p in caminho.split("."):
        if isinstance(dado, list) and p.isdigit() and int(p) < len(dado):
            dado = dado[int(p)]
        elif isinstance(dado, dict) and p in dado:
            dado = dado[p]
        else:
            return None
    return dado


def fmt(v):
    if v is None:
        return "–"
    if isinstance(v, float):
        return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    if isinstance(v, int):
        return f"{v:,}".replace(",", ".")
    return str(v)[:80]


def coletar(cfg, agora=None):
    c = Cartao(cfg.get("id", "uso"), cfg.get("titulo", "Uso"))
    arq = os.path.expanduser(cfg.get("arquivo", ""))
    if not os.path.isfile(arq):
        c.estado, c.frase = "sem", "sem arquivo"
        c.linha("arquivo", cfg.get("arquivo", "?"), "aviso")
        return c
    with open(arq, encoding="utf-8") as f:
        d = json.load(f)
    idade_h = ((agora or time.time()) - os.path.getmtime(arq)) / 3600
    if idade_h > float(cfg.get("max_horas", 30)):
        c.piora("aviso", f"{c.titulo}: dados parados há {idade_h:.0f} h")
    fr = cfg.get("frase")
    if fr:
        c.frase = f"{fmt(pegar(d, fr[1]))} {fr[0]}"
    for rot, cam in cfg.get("campos", []):
        c.linha(rot, fmt(pegar(d, cam)))
    for rot, cam in cfg.get("detalhe", []):
        c.mais(rot, fmt(pegar(d, cam)))
    c.mais("atualizado", time.strftime("%d/%m %H:%M", time.localtime(os.path.getmtime(arq))))
    return c
