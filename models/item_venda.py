class ItemVenda:
    def __init__(self, id_produto: int, quantidade: int, valor_unitario: float,
                 descricao_produto: str = ""):
        if quantidade <= 0:
            raise ValueError("Quantidade do item deve ser maior que zero.")
        if valor_unitario < 0:
            raise ValueError("Valor unitário não pode ser negativo.")
        self.id_produto = id_produto
        self.quantidade = quantidade
        self.valor_unitario = valor_unitario
        self.descricao_produto = descricao_produto  # apenas para exibição

    @property
    def subtotal(self) -> float:
        return round(self.quantidade * self.valor_unitario, 2)

    def __str__(self):
        nome = self.descricao_produto or f"Produto #{self.id_produto}"
        return f"{nome} x{self.quantidade} = R$ {self.subtotal:.2f}"
