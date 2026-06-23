from datetime import date
from models.item_venda import ItemVenda


class VendaSemItensError(Exception):
    """Lançada quando se tenta finalizar uma venda sem nenhum item."""
    pass


class Venda:
    def __init__(self, id_cliente: int, id_vendedor: int,
                 id_receita: int = None, data_venda: date = None,
                 id_venda: int = None):
        self.id_venda = id_venda
        self.id_cliente = id_cliente
        self.id_vendedor = id_vendedor
        self.id_receita = id_receita
        self.data_venda = data_venda or date.today()
        self.__itens: list[ItemVenda] = []

    @property
    def itens(self) -> list[ItemVenda]:
        return list(self.__itens)  # cópia defensiva

    def adicionar_item(self, item: ItemVenda):
        self.__itens.append(item)

    def remover_item(self, id_produto: int):
        self.__itens = [i for i in self.__itens if i.id_produto != id_produto]

    def definir_itens(self, itens: list[ItemVenda]):
        """Usado pelo repositório ao reconstruir a venda a partir do banco."""
        self.__itens = list(itens)

    @property
    def valor_total(self) -> float:
        return round(sum(item.subtotal for item in self.__itens), 2)

    def validar_para_fechamento(self):
        """Regra de negócio: não é permitido fechar venda sem itens."""
        if not self.__itens:
            raise VendaSemItensError("Não é possível registrar uma venda sem itens.")

    def __str__(self):
        qtd_itens = len(self.__itens)
        return (f"Venda #{self.id_venda} | Cliente {self.id_cliente} | "
                f"Vendedor {self.id_vendedor} | {qtd_itens} item(ns) | "
                f"Total: R$ {self.valor_total:.2f}")
