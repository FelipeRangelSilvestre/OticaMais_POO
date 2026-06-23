from models.produto import Produto, Armacao, Lente
from repositories.produto_repository import ProdutoRepository


class ProdutoService:
    def __init__(self):
        self.__repo = ProdutoRepository()

    def cadastrar_armacao(self, descricao: str, preco_venda: float, marca: str,
                           cor: str = "", qtd_estoque: int = 0, qtd_minima: int = 5) -> Armacao:
        armacao = Armacao(id_produto=None, descricao=descricao, preco_venda=preco_venda,
                           qtd_estoque=qtd_estoque, marca=marca, cor=cor, qtd_minima=qtd_minima)
        novo_id = self.__repo.inserir_armacao(armacao)
        return self.__repo.buscar_por_id(novo_id)

    def cadastrar_lente(self, descricao: str, preco_venda: float, tipo_foco: str,
                         indice: float = None, qtd_estoque: int = 0, qtd_minima: int = 5) -> Lente:
        lente = Lente(id_produto=None, descricao=descricao, preco_venda=preco_venda,
                       qtd_estoque=qtd_estoque, tipo_foco=tipo_foco, indice=indice,
                       qtd_minima=qtd_minima)
        novo_id = self.__repo.inserir_lente(lente)
        return self.__repo.buscar_por_id(novo_id)

    def listar(self) -> list[Produto]:
        return self.__repo.listar_todos()

    def listar_em_falta(self) -> list[Produto]:
        """Demonstra o uso polimórfico: chama produto.estoque_critico em
        Armacao e Lente sem se importar com o tipo concreto."""
        return [p for p in self.__repo.listar_todos() if p.estoque_critico]

    def buscar_por_id(self, id_produto: int) -> Produto | None:
        return self.__repo.buscar_por_id(id_produto)

    def repor_estoque(self, id_produto: int, quantidade: int):
        produto = self.__repo.buscar_por_id(id_produto)
        if not produto:
            raise ValueError(f"Produto #{id_produto} não encontrado.")
        produto.atualizar_estoque(quantidade)  # regra de negócio no próprio model
        self.__repo.atualizar_estoque(id_produto, produto.qtd_estoque)

    def excluir(self, id_produto: int):
        if not self.__repo.buscar_por_id(id_produto):
            raise ValueError(f"Produto #{id_produto} não encontrado.")
        self.__repo.excluir(id_produto)
