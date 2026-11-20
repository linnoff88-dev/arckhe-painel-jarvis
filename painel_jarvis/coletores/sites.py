"""Sites no ar: um GET leve por site (timeout 8 s, sem cookie), em paralelo.

[sites]
lista = ["https://meusite.com", "https://outro.com"]
"""
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from ..cartao import Cartao


def checar(url):
    t0 = time.time()
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "painel-jarvis/1 (disponibilidade)"}), timeout=8)
        r.close()
        return url, r.status < 400, f"{int((time.time() - t0) * 1000)} ms"
    except urllib.error.HTTPError as e:
        return url, e.code < 400, f"HTTP {e.code}"
    except Exception as e:
        return url, False, type(e).__name__ if not str(e) else str(e)[:60]


def coletar(cfg):
    c = Cartao("sites", cfg.get("titulo", "Sites"))
    lista = cfg.get("lista", [])
    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(checar, lista))
    fora = [r for r in res if not r[1]]
    c.frase = f"{len(fora)} fora do ar" if fora else f"{len(res)} de {len(res)} no ar"
    for url, ok, txt in fora + [r for r in res if r[1]]:
        host = url.split("://", 1)[-1].rstrip("/")
        c.linha(host, txt if ok else f"fora · {txt}", "" if ok else "erro")
        if not ok:
            c.piora("erro", f"{host} fora do ar ({txt})")
    return c
