"""Máquina: memória, disco, carga e GPU (nvidia-smi, se houver). Só lê /proc e chama comandos de leitura."""
import os
import shutil
import subprocess

from ..cartao import Cartao


def br(x, casas=1):
    """1234.5 → '1.234,5' (número em português)."""
    return f"{x:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _meminfo():
    m = {}
    with open("/proc/meminfo") as f:
        for l in f:
            k, v = l.split(":", 1)
            m[k] = int(v.split()[0]) / 1048576  # GB
    return m


def _gpu():
    if not shutil.which("nvidia-smi"):
        return None
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu",
                            "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=8)
        nome, uso, usada, total, temp = [x.strip() for x in r.stdout.splitlines()[0].split(",")]
        return {"nome": nome, "uso": uso, "usada": usada, "total": total, "temp": temp}
    except Exception:
        return None


def coletar(cfg):
    c = Cartao("maquina", cfg.get("titulo", "Máquina"))
    m = _meminfo()
    total, livre = m.get("MemTotal", 0), m.get("MemAvailable", 0)
    pct_livre = 100 * livre / total if total else 0
    c.frase = f"{br(livre)} GB livres de {br(total, 0)}"
    c.linha("memória em uso", f"{100 - pct_livre:.0f} %")
    if pct_livre < cfg.get("memoria_min_pct", 10):
        c.piora("aviso", f"memória quase cheia: {br(livre)} GB livres")
    disco = cfg.get("disco", "/")
    d = shutil.disk_usage(disco)
    pct = 100 * d.used / d.total
    c.linha(f"disco {disco}", f"{pct:.0f} % · {br(d.free / 1e9, 0)} GB livres", "aviso" if pct >= cfg.get("disco_max_pct", 90) else "")
    if pct >= cfg.get("disco_max_pct", 90):
        c.piora("aviso", f"disco {disco} em {pct:.0f} %")
    c1, c5, c15 = os.getloadavg()
    c.linha("carga (1 min)", f"{br(c1, 2)} em {os.cpu_count()} núcleos")
    g = _gpu()
    if g:
        c.linha("GPU", f"{g['uso']} % · {g['temp']} °C")
        c.mais("GPU", f"{g['nome']} · memória {g['usada']}/{g['total']} MiB")
    c.mais("swap em uso", f"{br(m.get('SwapTotal', 0) - m.get('SwapFree', 0))} GB")
    c.mais("cache de disco", f"{br(m.get('Cached', 0))} GB")
    c.mais("carga 5 · 15 min", f"{br(c5, 2)} · {br(c15, 2)}")
    return c
