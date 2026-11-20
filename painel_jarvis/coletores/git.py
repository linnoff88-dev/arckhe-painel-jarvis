"""O que fizemos: commits de 24 h e 7 dias e os últimos títulos de cada projeto (git local, sem rede).

[git]
projetos = ["~/projetos/meu-app", "~/projetos/site"]
"""
import os
import subprocess

from ..cartao import Cartao


def _git(repo, *a):
    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True, timeout=20).stdout.strip()


def resumo(repo):
    n1 = len([l for l in _git(repo, "log", "--since=1 day ago", "--format=%h").splitlines() if l])
    n7 = len([l for l in _git(repo, "log", "--since=7 days ago", "--format=%h").splitlines() if l])
    ult = _git(repo, "log", "-3", "--format=%cd\t%s", "--date=format:%d/%m %H:%M").splitlines()
    return n1, n7, [u.split("\t", 1) for u in ult if "\t" in u]


def coletar(cfg):
    c = Cartao("git", cfg.get("titulo", "O que fizemos"))
    t1 = t7 = 0
    for p in cfg.get("projetos", []):
        repo = os.path.expanduser(p)
        nome = os.path.basename(repo.rstrip("/"))
        if not os.path.isdir(os.path.join(repo, ".git")):
            c.linha(nome, "não é um repositório git", "aviso")
            continue
        n1, n7, ult = resumo(repo)
        t1, t7 = t1 + n1, t7 + n7
        c.linha(nome, f"{n1} em 24 h · {n7} em 7 dias")
        for quando, titulo in ult:
            c.mais(f"{nome} · {quando}", titulo[:120])
    c.frase = f"{t1} commits em 24 h · {t7} em 7 dias"
    return c
