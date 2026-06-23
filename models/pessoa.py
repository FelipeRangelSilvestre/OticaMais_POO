from abc import ABC, abstractmethod


class Pessoa(ABC):
    def __init__(self, nome: str, telefone: str = ""):
        self.__nome = nome
        self.__telefone = telefone

    @property
    def nome(self):
        return self.__nome

    @nome.setter
    def nome(self, novo_nome: str):
        if not novo_nome or not novo_nome.strip():
            raise ValueError("Nome não pode ser vazio.")
        self.__nome = novo_nome.strip()

    @property
    def telefone(self):
        return self.__telefone

    @telefone.setter
    def telefone(self, novo_telefone: str):
        self.__telefone = novo_telefone

    @abstractmethod
    def apresentar(self) -> str:
        """Método polimórfico obrigatório para as classes filhas"""
        pass

    def __str__(self):
        return self.apresentar()
