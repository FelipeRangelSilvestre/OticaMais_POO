class Produto:
    def __init__(self, id_produto: int, descricao: str, preco: float, estoque: int):
        self.__id_produto = id_produto
        self.__descricao = descricao
        self.__preco = preco
        self.__estoque = estoque

    @property
    def descricao(self): return self.__descricao
    
    @property
    def preco(self): return self.__preco
    
    @property
    def estoque(self): return self.__estoque

    def baixar_estoque(self, quantidade: int):
        if quantidade > self.__estoque:
            raise ValueError(f"Estoque insuficiente para {self.__descricao}.")
        self.__estoque -= quantidade

    def __str__(self):
        return f"Produto: {self.__descricao} | R$ {self.__preco:.2f}"