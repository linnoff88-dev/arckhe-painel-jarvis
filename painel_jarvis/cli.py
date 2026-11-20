"""painel-jarvis <comando>

  cartoes            mostra os quadros no terminal (um por linha)
  falhas             só o que pede atenção
  web [--porta N] [--bind IP]   painel no navegador / celular (padrão 127.0.0.1:8790)
  mcp                servidor MCP por stdio (para Claude Code, Codex, qualquer Jarvis)
  senha              define a senha do painel web (pede no terminal)
  exemplo            imprime um painel.toml de exemplo
"""
import getpass
import os
import sys

from . import VERSAO


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    cmd = a.pop(0) if a else "cartoes"
    if cmd in ("-h", "--help", "ajuda") or "-h" in a or "--help" in a:
        print(__doc__.strip())
        return 0
    if cmd in ("-v", "--version", "versao"):
        print(VERSAO)
        return 0
    if cmd == "cartoes":
        from .ferramentas import resumo
        print(resumo())
        return 0
    if cmd == "falhas":
        from .ferramentas import falhas
        print(falhas())
        return 0
    if cmd == "mcp":
        from .mcp import servir
        servir()
        return 0
    if cmd == "web":
        from .web.servidor import servir
        porta = int(a[a.index("--porta") + 1]) if "--porta" in a else 8790
        bind = a[a.index("--bind") + 1] if "--bind" in a else None
        servir(porta, bind)
        return 0
    if cmd == "senha":
        from .web import senha
        s = getpass.getpass("nova senha do painel (12+ caracteres): ")
        if s != getpass.getpass("repita: "):
            print("as duas não batem")
            return 1
        try:
            senha.definir(s)
        except ValueError as e:
            print(e)
            return 1
        from . import config
        print(f"senha gravada em {os.path.join(config.PASTA, 'senha.json')}")
        return 0
    if cmd == "exemplo":
        with open(os.path.join(os.path.dirname(__file__), "painel.exemplo.toml"), encoding="utf-8") as f:
            print(f.read())
        return 0
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    sys.exit(main())
