"""Rotinas (cron ou scripts) pelo log: rodou dentro do prazo? A última linha fala em erro?

[rotinas]
lista = [
  { nome = "backup", log = "~/logs/backup.log", max_horas = 26 },
]
"""
import os
import re
import time

from ..cartao import Cartao

ERRO = re.compile(r"\b(erro|error|falhou|failed|traceback|exception)\b", re.I)


def avaliar(log, max_horas, agora=None):
    """(estado, texto, ultima_linha) de um log."""
    agora = agora or time.time()
    p = os.path.expanduser(log)
    if not os.path.exists(p):
        return "aviso", "log não encontrado", ""
    mt = os.path.getmtime(p)
    with open(p, encoding="utf-8", errors="replace") as f:
        fim = [l.strip() for l in f.read()[-20000:].splitlines() if l.strip()]
    ult = fim[-1][:160] if fim else ""
    quando = time.strftime("%d/%m %H:%M", time.localtime(mt))
    if any(ERRO.search(l) for l in fim[-5:]):
        return "erro", f"erro na última execução ({quando})", ult
    if agora - mt > max_horas * 3600:
        return "aviso", f"parada desde {quando}", ult
    return "ok", f"ok {quando}", ult


def coletar(cfg):
    c = Cartao("rotinas", cfg.get("titulo", "Rotinas"))
    lista = cfg.get("lista", [])
    ok = 0
    for r in lista:
        est, txt, ult = avaliar(r.get("log", ""), float(r.get("max_horas", 26)))
        ok += est == "ok"
        c.linha(r.get("nome", "?"), txt, "" if est == "ok" else est)
        c.mais(f"{r.get('nome', '?')} · última linha", ult or "–")
        if est != "ok":
            c.piora(est, f"rotina {r.get('nome')}: {txt}")
    c.frase = f"{ok} de {len(lista)} em ordem" if lista else "nenhuma rotina na lista"
    return c
