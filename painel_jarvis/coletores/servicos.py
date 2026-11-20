"""Serviços e timers do systemd: rodando ou parado, última e próxima execução, último resultado.

[servicos]
usuario = true                     # systemctl --user (false = do sistema)
lista = ["meu-bot.service", "backup.timer"]
"""
import subprocess
import time

from ..cartao import Cartao

PROPS = "LoadState,ActiveState,SubState,Result,Description,LastTriggerUSec,NextElapseUSecRealtime,ExecMainExitTimestamp"


def _show(unit, usuario):
    cmd = ["systemctl"] + (["--user"] if usuario else []) + ["show", unit, "-p", PROPS]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    return dict(l.split("=", 1) for l in r.stdout.splitlines() if "=" in l)


def _quando(txt):
    """'Sat 2026-11-14 07:10:00 -03' → '14/11 07:10'; vazio/n/a → '–'."""
    p = (txt or "").split()
    if len(p) >= 3 and "-" in p[1]:
        a, m, d = p[1].split("-")
        return f"{d}/{m} {p[2][:5]}"
    return "–"


def avaliar(unit, s):
    """(estado, texto) de uma unidade a partir do `systemctl show`."""
    ativo, sub, res = s.get("ActiveState", ""), s.get("SubState", ""), s.get("Result", "")
    if s.get("LoadState") == "not-found":
        return "aviso", "não existe nesta máquina"
    if unit.endswith(".timer"):
        if ativo != "active":
            return "erro", "timer parado"
        ult, prox = _quando(s.get("LastTriggerUSec")), _quando(s.get("NextElapseUSecRealtime"))
        return "ok", (f"última {ult} · " if ult != "–" else "ainda não rodou · ") + f"próxima {prox}"
    if ativo == "failed" or res not in ("", "success"):
        return "erro", f"falhou ({res or sub})"
    if ativo == "active":
        return "ok", "rodando" if sub == "running" else sub
    if ativo == "inactive" and res == "success":
        return "ok", f"terminou bem {_quando(s.get('ExecMainExitTimestamp'))}"
    return "aviso", f"{ativo}/{sub}"


def coletar(cfg):
    c = Cartao("servicos", cfg.get("titulo", "Serviços"))
    lista, usuario = cfg.get("lista", []), cfg.get("usuario", True)
    ok = 0
    for u in lista:
        try:
            est, txt = avaliar(u, _show(u, usuario))
        except Exception as e:
            est, txt = "aviso", f"sem leitura: {e}"
        ok += est == "ok"
        nome = u.rsplit(".", 1)[0]
        (c.linha if est != "ok" or len(c.linhas) < 6 else c.mais)(nome, txt, "" if est == "ok" else est)
        if est != "ok":
            c.piora(est, f"{nome}: {txt}")
    c.frase = f"{ok} de {len(lista)} em ordem" if lista else "nenhum serviço na lista"
    c.mais("lido em", time.strftime("%d/%m %H:%M"))
    return c
