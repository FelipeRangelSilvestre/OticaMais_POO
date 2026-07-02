from abc import ABC, abstractmethod

class Pessoa(ABC):
    def __init__(self, id_pessoa: int, nome: str, cpf: str):
        # Encapsulamento: atributos privados
        self.__id_pessoa = id_pessoa
        self.__nome = nome
        self.__cpf = cpf

    # Getters para acesso seguro
    @property
    def id_pessoa(self): return self.__id_pessoa
    
    @property
    def nome(self): return self.__nome

    @property
    def cpf(self): return self.__cpf

    def __str__(self):
        # Exigência do guião: Método mágico __str__
        return f"{self.__nome} (CPF: {self.__cpf})"

    @abstractmethod
    def exibir_resumo(self) -> str:
        """Contrato Abstrato: Toda a subclasse deve implementar este método."""
        pass