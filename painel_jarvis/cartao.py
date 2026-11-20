"""O formato único de um quadro do painel. Todo coletor devolve um Cartao; web, MCP e plugin só leem isto."""
from dataclasses import asdict, dataclass, field

ESTADOS = ("ok", "aviso", "erro", "sem")  # "sem" = não deu para ler
PESO = {"erro": 3, "aviso": 2, "sem": 1, "ok": 0}


@dataclass
class Linha:
    rotulo: str
    valor: str
    estado: str = ""  # "", "ok", "aviso" ou "erro": pinta só o valor


@dataclass
class Cartao:
    id: str
    titulo: str
    estado: str = "ok"
    frase: str = ""  # a frase grande do quadro: o que importa agora
    linhas: list = field(default_factory=list)  # cabe no cartão
    detalhe: list = field(default_factory=list)  # aparece ao abrir o cartão
    alertas: list = field(default_factory=list)  # textos curtos do que está errado

    def linha(self, rotulo, valor, estado=""):
        self.linhas.append(Linha(str(rotulo), str(valor), estado))
        return self

    def mais(self, rotulo, valor, estado=""):
        self.detalhe.append(Linha(str(rotulo), str(valor), estado))
        return self

    def piora(self, estado, alerta=None):
        """Sobe o estado do cartão (nunca melhora) e guarda o motivo."""
        if PESO.get(estado, 0) > PESO.get(self.estado, 0):
            self.estado = estado
        if alerta and estado in ("aviso", "erro"):
            self.alertas.append(alerta)
        return self

    def dict(self):
        return asdict(self)


def falhou(id, titulo, erro):
    """Cartão de coletor que quebrou: o painel continua de pé e mostra o porquê."""
    c = Cartao(id, titulo, "sem", "sem leitura")
    c.linha("erro", str(erro)[:160], "erro")
    return c
