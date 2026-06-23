from models.pessoa import Pessoa


class Vendedor(Pessoa):
    def __init__(self, nome: str, cpf: str, telefone: str = "",
                 email: str = "", id_vendedor: int = None):
        super().__init__(nome, telefone)
        self.cpf = "".join(filter(str.isdigit, cpf or ""))
        self.email = email
        self.id_vendedor = id_vendedor

    def apresentar(self) -> str:
        return f"Vendedor: {self.nome}"

    def __str__(self):
        return f"[{self.id_vendedor}] {self.nome} | CPF: {self.cpf} | Tel: {self.telefone or '-'}"
