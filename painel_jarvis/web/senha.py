"""Senha do painel (scrypt da stdlib) e sessões por cookie, guardadas em ~/.config/painel-jarvis/ (modo 600)."""
import hashlib
import hmac
import json
import os
import secrets
import time

from .. import config as cfgmod

N, R, P = 2 ** 14, 8, 1
SESSAO_S = 365 * 86400


def _arq(nome):
    return os.path.join(cfgmod.PASTA, nome)


def _grava600(caminho, dado):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    tmp = caminho + ".tmp"
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(dado, f)
    os.replace(tmp, caminho)


def _hash(senha, sal):
    return hashlib.scrypt(senha.encode(), salt=bytes.fromhex(sal), n=N, r=R, p=P, maxmem=64 * 1024 * 1024).hex()


def definir(senha):
    if len(senha) < 12:
        raise ValueError("a senha precisa de pelo menos 12 caracteres")
    sal = secrets.token_hex(16)
    _grava600(_arq("senha.json"), {"algo": "scrypt", "sal": sal, "hash": _hash(senha, sal)})


def tem_senha():
    return os.path.isfile(_arq("senha.json"))


def conferir(senha):
    try:
        with open(_arq("senha.json")) as f:
            h = json.load(f)
    except (OSError, ValueError):
        return False
    return hmac.compare_digest(_hash(senha, h["sal"]), h["hash"])


def _sessoes():
    try:
        with open(_arq("sessoes.json")) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def nova_sessao():
    tok = secrets.token_urlsafe(32)
    s = {k: v for k, v in _sessoes().items() if v > time.time()}
    s[hashlib.sha256(tok.encode()).hexdigest()] = time.time() + SESSAO_S
    _grava600(_arq("sessoes.json"), s)
    return tok


def sessao_valida(tok):
    if not tok:
        return False
    return _sessoes().get(hashlib.sha256(tok.encode()).hexdigest(), 0) > time.time()


def sair(tok):
    s = _sessoes()
    s.pop(hashlib.sha256((tok or "").encode()).hexdigest(), None)
    _grava600(_arq("sessoes.json"), s)
