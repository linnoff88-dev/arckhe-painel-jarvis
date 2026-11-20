import asyncio
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.request

import pytest

from painel_jarvis import ferramentas, mcp, nucleo
from painel_jarvis.cartao import Cartao
from painel_jarvis.coletores import rotinas, servicos, uso_json


# --- coletores -----------------------------------------------------------------------------------
@pytest.mark.parametrize("unit,show,estado", [
    ("a.service", {"LoadState": "loaded", "ActiveState": "active", "SubState": "running", "Result": "success"}, "ok"),
    ("a.service", {"LoadState": "loaded", "ActiveState": "failed", "SubState": "failed", "Result": "exit-code"}, "erro"),
    ("a.service", {"LoadState": "loaded", "ActiveState": "inactive", "SubState": "dead", "Result": "success"}, "ok"),
    ("a.service", {"LoadState": "not-found", "ActiveState": "inactive", "Result": "success"}, "aviso"),
    ("a.timer", {"LoadState": "loaded", "ActiveState": "inactive"}, "erro"),
    ("a.timer", {"LoadState": "loaded", "ActiveState": "active", "LastTriggerUSec": "Sat 2026-11-14 07:10:00 -03"}, "ok"),
])
def test_servicos_avaliar(unit, show, estado):
    assert servicos.avaliar(unit, show)[0] == estado


def test_rotinas_log(tmp_path):
    ok, ruim = tmp_path / "ok.log", tmp_path / "ruim.log"
    ok.write_text("começou\nFIM ok\n")
    ruim.write_text("começou\nError: upsert: 500 statement timeout\n")
    assert rotinas.avaliar(str(ok), 26)[0] == "ok"
    assert rotinas.avaliar(str(ruim), 26)[0] == "erro"
    assert rotinas.avaliar(str(ok), 1, agora=time.time() + 7200)[0] == "aviso"  # parado além do prazo
    assert rotinas.avaliar(str(tmp_path / "nao.log"), 26)[0] == "aviso"


def test_uso_json(tmp_path):
    arq = tmp_path / "uso.json"
    arq.write_text(json.dumps({"v": {"d1": 222, "d7": 1794}, "lista": [{"n": 3}], "custo": 1.5}))
    c = uso_json.coletar({"id": "site", "titulo": "Site", "arquivo": str(arq), "frase": ["visitas em 24 h", "v.d1"],
                          "campos": [["7 dias", "v.d7"], ["primeiro", "lista.0.n"], ["custo", "custo"], ["falta", "x.y"]]})
    assert c.frase == "222 visitas em 24 h"
    assert [l.valor for l in c.linhas] == ["1.794", "3", "1,50", "–"]
    velho = uso_json.coletar({"arquivo": str(arq), "max_horas": 1}, agora=time.time() + 7200)
    assert velho.estado == "aviso"
    assert uso_json.coletar({"arquivo": str(tmp_path / "nao.json")}).estado == "sem"


def test_nucleo_isola_coletor_quebrado(monkeypatch):
    def quebra(cfg):
        raise RuntimeError("caiu")
    monkeypatch.setattr(nucleo, "QUADROS", [("maquina", "Máquina", quebra), ("sites", "Sites", lambda c: Cartao("sites", "Sites", frase="ok"))])
    d = nucleo.coletar({"maquina": {}, "sites": {}})
    assert [c["estado"] for c in d["cartoes"]] == ["sem", "ok"]
    assert "caiu" in d["cartoes"][0]["linhas"][0]["valor"]


# --- ferramentas e MCP -----------------------------------------------------------------------------
def falso():
    a = Cartao("maquina", "Máquina", frase="50 GB livres")
    b = Cartao("servicos", "Serviços", frase="1 de 2 em ordem").linha("bot", "falhou (exit-code)", "erro").piora("erro", "bot: falhou")
    return {"titulo": "Painel", "gerado_em": 0, "estado": "erro", "alertas": ["bot: falhou"], "cartoes": [a.dict(), b.dict()]}


def test_ferramentas_texto():
    assert "1 ponto(s)" in ferramentas.resumo(coletar=falso)
    assert "bot: falhou" in ferramentas.falhas(coletar=falso)
    assert "falhou (exit-code)" in ferramentas.cartao({"quadro": "servicos"}, coletar=falso)
    assert "Quadros: maquina, servicos" in ferramentas.cartao({"quadro": "xyz"}, coletar=falso)


def test_mcp_protocolo(monkeypatch):
    ini = mcp.responder({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}})
    assert ini["result"]["protocolVersion"] == "2025-06-18" and "tools" in ini["result"]["capabilities"]
    assert mcp.responder({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None
    nomes = [t["name"] for t in mcp.responder({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})["result"]["tools"]]
    assert nomes == ["painel_resumo", "painel_falhas", "painel_quadro"]
    monkeypatch.setattr(mcp, "chamar", lambda n, a: ferramentas.falhas(coletar=falso))
    r = mcp.responder({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "painel_falhas", "arguments": {}}})
    assert "bot: falhou" in r["result"]["content"][0]["text"] and r["result"]["isError"] is False
    assert mcp.responder({"jsonrpc": "2.0", "id": 4, "method": "xyz"})["error"]["code"] == -32601


def test_mcp_stdio_de_ponta_a_ponta(tmp_path):
    import io
    ent = io.StringIO('{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}\nlixo\n{"jsonrpc":"2.0","id":2,"method":"tools/list"}\n')
    sai = io.StringIO()
    mcp.servir(ent, sai)
    linhas = [json.loads(l) for l in sai.getvalue().splitlines()]
    assert [l.get("id") for l in linhas] == [1, None, 2] and linhas[1]["error"]["code"] == -32700


# --- web ----------------------------------------------------------------------------------------
@pytest.fixture
def web(tmp_path, monkeypatch):
    from painel_jarvis import config
    from painel_jarvis.web import senha, servidor
    monkeypatch.setattr(config, "PASTA", str(tmp_path))
    monkeypatch.setattr(nucleo, "coletar_cache", lambda cfg=None, max_idade=30: falso())
    servidor.Painel.config = {"painel": {"titulo": "Teste <b>"}}
    srv = servidor.ThreadingHTTPServer(("127.0.0.1", 0), servidor.Painel)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}", senha
    srv.shutdown()


class SemRedirecionar(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def pedir(url, dados=None, cookie=None):
    op = urllib.request.build_opener(SemRedirecionar)
    req = urllib.request.Request(url, data=dados, headers={"Cookie": cookie} if cookie else {})
    try:
        r = op.open(req, timeout=5)
        return r.status, r.headers, r.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.headers, e.read().decode(errors="replace")


def test_web_sem_senha_abre_e_escapa_titulo(web):
    base, _ = web
    st, _, corpo = pedir(base + "/")
    assert st == 200 and "Teste &lt;b&gt;" in corpo and 'rel="manifest"' in corpo
    st, h, corpo = pedir(base + "/api/painel")
    assert st == 200 and json.loads(corpo)["alertas"] == ["bot: falhou"]
    assert pedir(base + "/manifest.webmanifest")[0] == 200 and pedir(base + "/icone-512.png")[0] == 200


def test_web_com_senha_exige_login(web):
    base, senha = web
    senha.definir("uma senha bem longa")
    assert pedir(base + "/api/painel")[0] == 401
    assert pedir(base + "/")[0] == 303
    assert pedir(base + "/login", b"senha=errada")[0] == 401
    st, h, _ = pedir(base + "/login", b"senha=uma+senha+bem+longa")
    assert st == 303
    ck = h["Set-Cookie"].split(";")[0]
    assert "HttpOnly" in h["Set-Cookie"]
    assert pedir(base + "/api/painel", cookie=ck)[0] == 200
    assert pedir(base + "/manifest.webmanifest")[0] == 200  # o app instalável não precisa de login


def test_senha_curta_recusada(web):
    with pytest.raises(ValueError):
        web[1].definir("curta")


# --- plugin do intelecto ---------------------------------------------------------------------------
def test_plugin_intelecto():
    raiz = os.path.expanduser("~/projetos/intelecto-v2")
    if os.path.isdir(raiz) and raiz not in sys.path:
        sys.path.insert(0, raiz)
    pytest.importorskip("intelecto.ferramentas.base")
    from painel_jarvis import intelecto_plugin
    fs = intelecto_plugin.ferramentas()
    assert [f.nome for f in fs] == ["painel_resumo", "painel_falhas", "painel_quadro"]
    r = asyncio.run(fs[2].executar(quadro="nao-existe"))
    assert r.ok and "Não achei" in r.saida
