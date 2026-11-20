"""Servidor MCP mínimo (stdio, JSON-RPC 2.0 uma mensagem por linha), sem dependência.

Qualquer Jarvis ou agente que fale MCP (Claude Code, Codex, Cursor...) passa a ter painel_resumo, painel_falhas e
painel_quadro. Ex. no Claude Code:  claude mcp add painel -- painel-jarvis mcp
"""
import json
import sys

from . import VERSAO
from .ferramentas import FERRAMENTAS, chamar

PROTOCOLOS = ("2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05")


def responder(msg):
    """Uma mensagem → resposta (dict) ou None (notificação)."""
    metodo, id_ = msg.get("method"), msg.get("id")
    if id_ is None:
        return None  # notificações (ex.: notifications/initialized) não têm resposta
    try:
        if metodo == "initialize":
            pedido = (msg.get("params") or {}).get("protocolVersion")
            r = {"protocolVersion": pedido if pedido in PROTOCOLOS else PROTOCOLOS[0],
                 "capabilities": {"tools": {}}, "serverInfo": {"name": "painel-jarvis", "version": VERSAO}}
        elif metodo == "ping":
            r = {}
        elif metodo == "tools/list":
            r = {"tools": [{"name": f["nome"], "description": f["descricao"], "inputSchema": f["parametros"],
                            "annotations": {"readOnlyHint": True}} for f in FERRAMENTAS]}
        elif metodo == "tools/call":
            p = msg.get("params") or {}
            try:
                texto, erro = chamar(p.get("name"), p.get("arguments") or {}), False
            except KeyError:
                return {"jsonrpc": "2.0", "id": id_, "error": {"code": -32602, "message": f"ferramenta desconhecida: {p.get('name')}"}}
            except Exception as e:
                texto, erro = f"erro ao ler o painel: {e}", True
            r = {"content": [{"type": "text", "text": texto}], "isError": erro}
        else:
            return {"jsonrpc": "2.0", "id": id_, "error": {"code": -32601, "message": f"método não suportado: {metodo}"}}
        return {"jsonrpc": "2.0", "id": id_, "result": r}
    except Exception as e:
        return {"jsonrpc": "2.0", "id": id_, "error": {"code": -32603, "message": str(e)}}


def servir(entrada=sys.stdin, saida=sys.stdout):
    for linha in entrada:
        linha = linha.strip()
        if not linha:
            continue
        try:
            msg = json.loads(linha)
        except ValueError:
            resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "JSON inválido"}}
        else:
            resp = responder(msg)
        if resp is not None:
            saida.write(json.dumps(resp, ensure_ascii=False) + "\n")
            saida.flush()
