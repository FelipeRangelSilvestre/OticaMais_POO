from models.pessoa import Pessoa


class Cliente(Pessoa):
    def __init__(self, nome: str, cpf: str, telefone: str = "",
                 email: str = "", endereco: str = "", id_cliente: int = None):
        super().__init__(nome, telefone)
        self.__cpf = self.__validar_cpf(cpf)
        self.email = email
        self.endereco = endereco
        self.id_cliente = id_cliente

    @staticmethod
    def __validar_cpf(cpf: str) -> str:
        cpf_limpo = "".join(filter(str.isdigit, cpf or ""))
        if len(cpf_limpo) != 11:
            raise ValueError("CPF deve conter 11 dígitos numéricos.")
        return cpf_limpo

    @property
    def cpf(self):
        return self.__cpf

    def apresentar(self) -> str:
        return f"Cliente: {self.nome} (CPF: {self.cpf})"

    def __str__(self):
        return (f"[{self.id_cliente}] {self.nome} | CPF: {self.cpf} | "
                f"Tel: {self.telefone or '-'} | Email: {self.email or '-'}")
