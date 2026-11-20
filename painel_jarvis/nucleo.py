"""Junta os quadros ligados no painel.toml. Cada coletor roda isolado: se um quebra, vira cartão "sem leitura"."""
import time
from concurrent.futures import ThreadPoolExecutor

from . import config as cfgmod
from .cartao import PESO, falhou
from .coletores import git, maquina, rotinas, servicos, sites, uso_json

# (seção do painel.toml, título padrão, função)
QUADROS = [
    ("maquina", "Máquina", maquina.coletar),
    ("servicos", "Serviços", servicos.coletar),
    ("rotinas", "Rotinas", rotinas.coletar),
    ("sites", "Sites", sites.coletar),
    ("git", "O que fizemos", git.coletar),
]
_cache = {"em": 0, "dados": None}


def _roda(fn, id, titulo, sec):
    try:
        return fn(sec)
    except Exception as e:  # um coletor quebrado não derruba o painel
        return falhou(id, sec.get("titulo", titulo), e)


def coletar(config=None):
    c = config if config is not None else cfgmod.carregar()
    tarefas = [(fn, id, t, c[id]) for id, t, fn in QUADROS if isinstance(c.get(id), dict)]
    tarefas += [(uso_json.coletar, u.get("id", "uso"), u.get("titulo", "Uso"), u) for u in c.get("uso", []) if isinstance(u, dict)]
    with ThreadPoolExecutor(6) as ex:
        cartoes = list(ex.map(lambda t: _roda(*t), tarefas))
    pior = max((x.estado for x in cartoes), key=lambda e: PESO.get(e, 0), default="ok")
    return {"titulo": c.get("painel", {}).get("titulo", "Painel"), "gerado_em": int(time.time()),
            "estado": pior, "alertas": [a for x in cartoes for a in x.alertas], "cartoes": [x.dict() for x in cartoes]}


def coletar_cache(config=None, max_idade=30):
    """Para a web: no máximo uma coleta a cada `max_idade` segundos."""
    if _cache["dados"] is None or time.time() - _cache["em"] > max_idade:
        _cache["dados"], _cache["em"] = coletar(config), time.time()
    return _cache["dados"]
