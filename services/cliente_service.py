from models.cliente import Cliente
from repositories.cliente_repository import ClienteRepository


class CpfDuplicadoError(Exception):
    """Lançada ao tentar cadastrar um cliente com CPF já existente."""
    pass


class ClienteService:
    def __init__(self):
        self.__repo = ClienteRepository()

    def cadastrar(self, nome: str, cpf: str, telefone: str = "",
                   email: str = "", endereco: str = "") -> Cliente:
        cliente = Cliente(nome=nome, cpf=cpf, telefone=telefone, email=email, endereco=endereco)

        if self.__repo.buscar_por_cpf(cliente.cpf):
            raise CpfDuplicadoError(f"Já existe cliente cadastrado com o CPF {cliente.cpf}.")

        cliente.id_cliente = self.__repo.inserir(cliente)
        return cliente

    def listar(self) -> list[Cliente]:
        return self.__repo.listar_todos()

    def buscar_por_nome(self, termo: str) -> list[Cliente]:
        return self.__repo.buscar_por_nome(termo)

    def buscar_por_id(self, id_cliente: int) -> Cliente | None:
        return self.__repo.buscar_por_id(id_cliente)

    def editar(self, id_cliente: int, nome: str = None, telefone: str = None,
               email: str = None, endereco: str = None) -> Cliente:
        cliente = self.__repo.buscar_por_id(id_cliente)
        if not cliente:
            raise ValueError(f"Cliente #{id_cliente} não encontrado.")

        if nome:
            cliente.nome = nome
        if telefone is not None:
            cliente.telefone = telefone
        if email is not None:
            cliente.email = email
        if endereco is not None:
            cliente.endereco = endereco

        self.__repo.atualizar(cliente)
        return cliente

    def excluir(self, id_cliente: int):
        if not self.__repo.buscar_por_id(id_cliente):
            raise ValueError(f"Cliente #{id_cliente} não encontrado.")
        self.__repo.excluir(id_cliente)
