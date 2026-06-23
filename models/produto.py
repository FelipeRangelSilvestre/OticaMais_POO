from abc import ABC, abstractmethod


class Produto(ABC):
    def __init__(self, id_produto: int, tipo: str, descricao: str,
                 preco_venda: float, qtd_estoque: int, qtd_minima: int = 5):
        self.__id_produto = id_produto
        self.__tipo = tipo
        self.__descricao = descricao
        self.__preco_venda = preco_venda
        self.__qtd_estoque = qtd_estoque  # Atributo encapsulado
        self.__qtd_minima = qtd_minima

    @property
    def id_produto(self):
        return self.__id_produto

    @property
    def tipo(self):
        return self.__tipo

    @property
    def descricao(self):
        return self.__descricao

    @property
    def preco_venda(self):
        return self.__preco_venda

    @preco_venda.setter
    def preco_venda(self, novo_preco: float):
        if novo_preco < 0:
            raise ValueError("Preço de venda não pode ser negativo.")
        self.__preco_venda = novo_preco

    @property
    def qtd_estoque(self):
        return self.__qtd_estoque

    @property
    def qtd_minima(self):
        return self.__qtd_minima

    @property
    def estoque_critico(self) -> bool:
        """True quando o estoque está no nível mínimo ou abaixo dele."""
        return self.__qtd_estoque <= self.__qtd_minima

    def atualizar_estoque(self, quantidade: int):
        # Regra de negócio simples no modelo
        if self.__qtd_estoque + quantidade < 0:
            raise ValueError("Estoque insuficiente para esta operação.")
        self.__qtd_estoque += quantidade

    @abstractmethod
    def detalhar_produto(self) -> str:
        """Método polimórfico obrigatório para as classes filhas"""
        pass

    def __str__(self):
        # __str__ fica só aqui na classe-base: cada filha só precisa
        # sobrescrever detalhar_produto() para mudar o que aparece.
        return (f"[{self.id_produto}] {self.detalhar_produto()} - "
                f"R$ {self.preco_venda:.2f} | Estoque: {self.qtd_estoque}")


class Armacao(Produto):
    def __init__(self, id_produto: int, descricao: str, preco_venda: float,
                 qtd_estoque: int, marca: str, cor: str, qtd_minima: int = 5):
        super().__init__(id_produto, "ARMACAO", descricao, preco_venda, qtd_estoque, qtd_minima)
        self.marca = marca
        self.cor = cor

    def detalhar_produto(self) -> str:
        # Polimorfismo em ação
        return f"Armação {self.marca} (Cor: {self.cor})"


class Lente(Produto):
    def __init__(self, id_produto: int, descricao: str, preco_venda: float,
                 qtd_estoque: int, tipo_foco: str, indice: float, qtd_minima: int = 5):
        super().__init__(id_produto, "LENTE", descricao, preco_venda, qtd_estoque, qtd_minima)
        self.tipo_foco = tipo_foco
        self.indice = indice

    def detalhar_produto(self) -> str:
        # Polimorfismo com comportamento diferente
        return f"Lente {self.tipo_foco} (Índice: {self.indice})"
