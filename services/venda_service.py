from models.venda import Venda, VendaSemItensError
from models.item_venda import ItemVenda
from repositories.venda_repository import VendaRepository
from repositories.produto_repository import ProdutoRepository


class VendaService:
    def __init__(self):
        self.__venda_repo = VendaRepository()
        self.__produto_repo = ProdutoRepository()

    def iniciar_venda(self, id_cliente: int, id_vendedor: int, id_receita: int = None) -> Venda:
        return Venda(id_cliente=id_cliente, id_vendedor=id_vendedor, id_receita=id_receita)

    def adicionar_item(self, venda: Venda, id_produto: int, quantidade: int):
        produto = self.__produto_repo.buscar_por_id(id_produto)
        if not produto:
            raise ValueError(f"Produto #{id_produto} não encontrado.")

        # Reaproveita a regra de negócio já escrita em Produto.atualizar_estoque():
        # ela lança ValueError se a baixa deixaria o estoque negativo.
        # Aqui só simulamos a checagem (sem persistir ainda), pois a baixa real
        # é feita pela trigger trg_item_venda_after no momento do INSERT.
        produto.atualizar_estoque(-quantidade)

        item = ItemVenda(id_produto=produto.id_produto, quantidade=quantidade,
                          valor_unitario=produto.preco_venda, descricao_produto=produto.descricao)
        venda.adicionar_item(item)

    def finalizar_venda(self, venda: Venda) -> Venda:
        venda.validar_para_fechamento()  # regra: não fecha venda sem itens
        # A trigger do banco soma valor_total e baixa o estoque a cada
        # item inserido — não duplicamos essa lógica aqui em Python.
        self.__venda_repo.inserir(venda)
        return venda

    def listar(self) -> list[Venda]:
        return self.__venda_repo.listar_todas()

    def buscar_por_id(self, id_venda: int) -> Venda | None:
        return self.__venda_repo.buscar_por_id(id_venda)

    def buscar_por_cliente(self, id_cliente: int) -> list[Venda]:
        return self.__venda_repo.buscar_por_cliente(id_cliente)

    def trocar_vendedor(self, id_venda: int, novo_id_vendedor: int):
        if not self.__venda_repo.buscar_por_id(id_venda):
            raise ValueError(f"Venda #{id_venda} não encontrada.")
        self.__venda_repo.atualizar_vendedor(id_venda, novo_id_vendedor)

    def excluir(self, id_venda: int):
        if not self.__venda_repo.buscar_por_id(id_venda):
            raise ValueError(f"Venda #{id_venda} não encontrada.")
        self.__venda_repo.excluir(id_venda)
