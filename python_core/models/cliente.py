from models.pessoa import Pessoa

class Cliente(Pessoa):
    def __init__(self, id_pessoa: int, nome: str, cpf: str, endereco: str):
        # Herança: a invocar o construtor da superclasse
        super().__init__(id_pessoa, nome, cpf)
        self.__endereco = endereco

    @property
    def endereco(self): return self.__endereco

    def exibir_resumo(self) -> str:
        # Polimorfismo: O Cliente formata o resumo com a sua morada
        return f"[Cliente VIP] {self.nome} | Morada: {self.endereco}"