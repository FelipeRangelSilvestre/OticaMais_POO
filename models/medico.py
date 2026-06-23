from models.pessoa import Pessoa


class Medico(Pessoa):
    def __init__(self, crm: str, nome: str, especialidade: str, telefone: str = ""):
        super().__init__(nome, telefone)
        self.crm = crm
        self.especialidade = especialidade

    def apresentar(self) -> str:
        return f"Dr(a). {self.nome} - {self.especialidade} (CRM {self.crm})"

    def __str__(self):
        return f"CRM {self.crm} | {self.nome} | {self.especialidade} | Tel: {self.telefone or '-'}"
