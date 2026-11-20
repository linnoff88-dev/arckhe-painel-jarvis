"""As ferramentas que qualquer Jarvis chama (intelecto, MCP, ou o seu): só leitura, respostas em texto curto.

FERRAMENTAS = [{nome, descricao, parametros (JSON Schema), funcao(args) -> str}]
"""
from . import nucleo

SIMB = {"ok": "✓", "aviso": "!", "erro": "✕", "sem": "?"}


def _linhas(itens):
    return "\n".join(f"  {i['rotulo']}: {i['valor']}" for i in itens)


def resumo(args=None, coletar=nucleo.coletar):
    d = coletar()
    topo = f"{d['titulo']}: " + ("tudo em ordem" if d["estado"] == "ok" else f"{len(d['alertas'])} ponto(s) de atenção")
    return topo + "\n" + "\n".join(f"{SIMB.get(c['estado'], '?')} {c['titulo']}: {c['frase']}" for c in d["cartoes"])


def falhas(args=None, coletar=nucleo.coletar):
    d = coletar()
    if not d["alertas"]:
        return "Nada falhando agora: todos os quadros em ordem."
    return "O que precisa de atenção:\n" + "\n".join(f"- {a}" for a in d["alertas"])


def cartao(args=None, coletar=nucleo.coletar):
    qual = str((args or {}).get("quadro", "")).strip().lower()
    d = coletar()
    for c in d["cartoes"]:
        if qual in (c["id"].lower(), c["titulo"].lower()):
            return f"{c['titulo']} ({c['estado']}): {c['frase']}\n{_linhas(c['linhas'] + c['detalhe'])}"
    return f"Não achei o quadro '{qual}'. Quadros: " + ", ".join(c["id"] for c in d["cartoes"])


FERRAMENTAS = [
    {"nome": "painel_resumo", "descricao": "Como está tudo agora: uma linha por quadro do painel (máquina, serviços, rotinas, sites, projetos, uso).",
     "parametros": {"type": "object", "properties": {}}, "funcao": resumo},
    {"nome": "painel_falhas", "descricao": "Só o que está falhando ou pede atenção agora (serviço parado, rotina com erro, site fora, disco cheio).",
     "parametros": {"type": "object", "properties": {}}, "funcao": falhas},
    {"nome": "painel_quadro", "descricao": "Detalhe de um quadro do painel pelo id ou título (ex.: maquina, servicos, sites, rotinas, git).",
     "parametros": {"type": "object", "properties": {"quadro": {"type": "string", "description": "id ou título do quadro"}}, "required": ["quadro"]},
     "funcao": cartao},
]


def chamar(nome, args=None):
    for f in FERRAMENTAS:
        if f["nome"] == nome:
            return f["funcao"](args or {})
    raise KeyError(nome)
