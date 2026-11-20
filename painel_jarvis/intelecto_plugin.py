"""Plugin do INTELECTO v2: as ferramentas do painel viram ferramentas do agente.

O intelecto acha este plugin pelo entry point `intelecto.plugins` (nome "painel") e só o carrega se o dono ligar:
  INTELECTO_PLUGINS=painel   (ou plugins = ["painel"] na config do intelecto)
Todas são só leitura: não passam pela trava de comandos porque não executam nada que o agente escolha.
"""
import asyncio

from .ferramentas import FERRAMENTAS


def ferramentas(pecas=None):
    """Chamado pelo intelecto na montagem; devolve instâncias de Ferramenta."""
    from intelecto.ferramentas.base import Ferramenta, Resultado  # só existe com o intelecto instalado

    def fabricar(spec):
        class F(Ferramenta):
            nome = spec["nome"]
            descricao = spec["descricao"]
            parametros = spec["parametros"]

            async def executar(self, **args):
                try:  # a coleta lê disco, systemd e rede: fora do loop do agente
                    return Resultado(True, await asyncio.to_thread(spec["funcao"], args))
                except Exception as e:
                    return Resultado(False, f"painel: {e}")

        F.__name__ = "Painel_" + spec["nome"]
        return F()

    return [fabricar(s) for s in FERRAMENTAS]
