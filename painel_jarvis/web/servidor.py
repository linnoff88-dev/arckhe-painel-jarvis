"""Servidor do painel (http.server da stdlib).

Sem senha definida, só escuta em 127.0.0.1 (só a própria máquina vê). Com senha (`painel-jarvis senha`), pode
escutar na rede e exige login; o aparelho fica lembrado por um ano. Para abrir fora de casa, ponha um túnel
(Cloudflare Tunnel, Tailscale) na frente: o painel não fala HTTPS sozinho.
"""
import html
import json
import os
import time
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

from .. import config as cfgmod
from .. import nucleo
from . import pagina, senha

AQUI = os.path.dirname(__file__)
COOKIE = "painel_jarvis"
CSP = ("default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src 'self'; connect-src 'self'; "
       "manifest-src 'self'; worker-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'")
ICONES = {"/icone-180.png", "/icone-192.png", "/icone-512.png", "/icone-maskable.png"}
_erros = {}  # ip -> [horários de senha errada]


def bloqueado(ip, agora=None):
    agora = agora or time.time()
    _erros[ip] = [t for t in _erros.get(ip, []) if agora - t < 900]
    return len(_erros[ip]) >= 5


class Painel(BaseHTTPRequestHandler):
    config = None
    server_version = "painel-jarvis"

    def log_message(self, *a):  # silencioso: o painel é consultado a cada minuto
        pass

    def _envia(self, status, corpo, tipo="text/html; charset=utf-8", extra=None, cache="no-store"):
        b = corpo if isinstance(corpo, bytes) else corpo.encode()
        self.send_response(status)
        for k, v in {"Content-Type": tipo, "Content-Length": str(len(b)), "Cache-Control": cache,
                     "Content-Security-Policy": CSP, "X-Content-Type-Options": "nosniff",
                     "X-Frame-Options": "DENY", "Referrer-Policy": "same-origin", **(extra or {})}.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(b)

    def _ir(self, para, extra=None):
        self.send_response(303)
        self.send_header("Location", para)
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()

    def _tok(self):
        c = cookies.SimpleCookie(self.headers.get("Cookie", ""))
        return c[COOKIE].value if COOKIE in c else None

    def _logado(self):
        return not senha.tem_senha() or senha.sessao_valida(self._tok())

    def _titulo(self):
        return html.escape(self.config.get("painel", {}).get("titulo", "Painel"))

    def do_GET(self):
        p = self.path.split("?", 1)[0]
        if p == "/manifest.webmanifest":
            return self._envia(200, json.dumps(pagina.manifesto(self.config.get("painel", {}).get("titulo", "Painel"))),
                               "application/manifest+json; charset=utf-8", cache="public, max-age=3600")
        if p == "/sw.js":
            return self._envia(200, pagina.SW, "text/javascript; charset=utf-8", {"Service-Worker-Allowed": "/"}, cache="no-cache")
        if p in ICONES:
            with open(os.path.join(AQUI, p[1:]), "rb") as f:
                return self._envia(200, f.read(), "image/png", cache="public, max-age=86400")
        if p == "/login":
            return self._ir("/") if self._logado() else self._envia(200, pagina.login(self._titulo()))
        if not self._logado():
            return self._envia(401, '{"erro":"entre no painel"}', "application/json") if p.startswith("/api/") else self._ir("/login")
        if p == "/api/painel":
            return self._envia(200, json.dumps(nucleo.coletar_cache(self.config), ensure_ascii=False), "application/json; charset=utf-8")
        if p == "/":
            pn = self.config.get("painel", {})
            return self._envia(200, pagina.painel(self._titulo(), pn.get("atualizar_s", 60), senha.tem_senha()))
        self._envia(404, "não achei")

    def do_POST(self):
        p = self.path.split("?", 1)[0]
        orig = self.headers.get("Origin")
        if orig and orig.split("://", 1)[-1] != self.headers.get("Host"):
            return self._envia(403, "origem recusada")
        if p == "/logout":
            senha.sair(self._tok())
            return self._ir("/login", {"Set-Cookie": f"{COOKIE}=; Max-Age=0; Path=/; HttpOnly; SameSite=Lax"})
        if p != "/login":
            return self._envia(404, "não achei")
        ip = self.client_address[0]
        if ip in ("127.0.0.1", "::1"):  # só um túnel/proxy local pode dizer o IP de verdade
            ip = self.headers.get("X-Forwarded-For", ip).split(",")[-1].strip()
        if bloqueado(ip):
            return self._envia(429, pagina.login(self._titulo(), "Muitas tentativas. Espere 15 minutos."))
        n = min(int(self.headers.get("Content-Length") or 0), 4096)
        s = parse_qs(self.rfile.read(n).decode(errors="replace")).get("senha", [""])[0]
        if not senha.conferir(s):
            _erros.setdefault(ip, []).append(time.time())
            return self._envia(401, pagina.login(self._titulo(), "Senha errada."))
        seguro = "; Secure" if self.headers.get("X-Forwarded-Proto") == "https" else ""
        tok = senha.nova_sessao()
        self._ir("/", {"Set-Cookie": f"{COOKIE}={tok}; Max-Age={senha.SESSAO_S}; Path=/; HttpOnly; SameSite=Lax{seguro}"})


def servir(porta=8790, bind=None, config=None):
    cfg = config if config is not None else cfgmod.carregar()
    bind = bind or cfg.get("painel", {}).get("bind", "127.0.0.1")
    if bind not in ("127.0.0.1", "localhost", "::1") and not senha.tem_senha():
        print(f"sem senha definida: ficando em 127.0.0.1 (pedido: {bind}). Defina com: painel-jarvis senha", flush=True)
        bind = "127.0.0.1"
    Painel.config = cfg
    srv = ThreadingHTTPServer((bind, porta), Painel)
    print(f"painel-jarvis em http://{bind}:{srv.server_address[1]}/ ({'com senha' if senha.tem_senha() else 'sem senha, só esta máquina'})", flush=True)
    srv.serve_forever()
