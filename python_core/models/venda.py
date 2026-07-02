from models.cliente import Cliente
from models.produto import Produto

class Venda:
    def __init__(self, id_venda: int, cliente: Cliente):
        self.id_venda = id_venda
        self.cliente = cliente
        self.itens = []  # Lista de produtos
        self.status = "ABERTA"

    def adicionar_item(self, produto: Produto):
        self.itens.append(produto)

    def finalizar_venda(self):
        """
        Regra de Negócio: Não permitir pedido sem itens.
        Isto cumpre o requisito da página 11 do edital.
        """
        if len(self.itens) == 0:
            raise Exception("Regra de Negócio Violada: Não é possível finalizar uma venda sem itens no carrinho.")
        
        self.status = "FINALIZADA"
        return sum(produto.preco for produto in self.itens)