from services.cliente_service import ClienteService, CpfDuplicadoError
from services.produto_service import ProdutoService
from services.venda_service import VendaService
from models.venda import VendaSemItensError


def menu_principal():
    cliente_service = ClienteService()
    produto_service = ProdutoService()
    venda_service = VendaService()

    opcoes = {
        "1": lambda: menu_clientes(cliente_service),
        "2": lambda: menu_produtos(produto_service),
        "3": lambda: menu_vendas(venda_service, cliente_service, produto_service),
    }

    while True:
        print("\n===== ÓTICA MAIS =====")
        print("1 - Gerenciar Clientes")
        print("2 - Gerenciar Produtos")
        print("3 - Gerenciar Vendas (CRUD completo)")
        print("0 - Sair")
        escolha = input("Escolha uma opção: ").strip()

        if escolha == "0":
            print("Saindo do sistema...")
            break

        acao = opcoes.get(escolha)
        if acao:
            acao()
        else:
            print("Opção inválida.")


# =========================================================
# CLIENTES
# =========================================================
def menu_clientes(service: ClienteService):
    while True:
        print("\n--- Clientes ---")
        print("1 - Cadastrar")
        print("2 - Listar todos")
        print("3 - Buscar por nome")
        print("4 - Editar")
        print("5 - Excluir")
        print("0 - Voltar")
        escolha = input("Escolha uma opção: ").strip()

        try:
            if escolha == "1":
                nome = input("Nome: ").strip()
                cpf = input("CPF (somente números): ").strip()
                telefone = input("Telefone: ").strip()
                email = input("Email: ").strip()
                endereco = input("Endereço: ").strip()
                cliente = service.cadastrar(nome, cpf, telefone, email, endereco)
                print(f"Cliente cadastrado com sucesso: {cliente}")

            elif escolha == "2":
                clientes = service.listar()
                if not clientes:
                    print("Nenhum cliente cadastrado.")
                for c in clientes:
                    print(c)

            elif escolha == "3":
                termo = input("Nome (ou parte do nome): ").strip()
                resultados = service.buscar_por_nome(termo)
                if not resultados:
                    print("Nenhum cliente encontrado.")
                for c in resultados:
                    print(c)

            elif escolha == "4":
                id_cliente = int(input("ID do cliente: ").strip())
                print("Deixe em branco para não alterar o campo.")
                nome = input("Novo nome: ").strip() or None
                telefone = input("Novo telefone: ").strip() or None
                email = input("Novo email: ").strip() or None
                endereco = input("Novo endereço: ").strip() or None
                cliente = service.editar(id_cliente, nome, telefone, email, endereco)
                print(f"Cliente atualizado: {cliente}")

            elif escolha == "5":
                id_cliente = int(input("ID do cliente a excluir: ").strip())
                service.excluir(id_cliente)
                print("Cliente excluído com sucesso.")

            elif escolha == "0":
                break

            else:
                print("Opção inválida.")

        except (CpfDuplicadoError, ValueError) as e:
            print(f"Erro: {e}")
        except Exception as e:
            print(f"Erro inesperado: {e}")


# =========================================================
# PRODUTOS
# =========================================================
def menu_produtos(service: ProdutoService):
    while True:
        print("\n--- Produtos ---")
        print("1 - Cadastrar armação")
        print("2 - Cadastrar lente")
        print("3 - Listar todos")
        print("4 - Listar em estoque crítico")
        print("5 - Repor estoque")
        print("6 - Excluir produto")
        print("0 - Voltar")
        escolha = input("Escolha uma opção: ").strip()

        try:
            if escolha == "1":
                descricao = input("Descrição: ").strip()
                preco = float(input("Preço de venda: ").strip())
                marca = input("Marca: ").strip()
                cor = input("Cor: ").strip()
                estoque = int(input("Quantidade em estoque: ").strip() or "0")
                produto = service.cadastrar_armacao(descricao, preco, marca, cor, estoque)
                print(f"Armação cadastrada: {produto}")

            elif escolha == "2":
                descricao = input("Descrição: ").strip()
                preco = float(input("Preço de venda: ").strip())
                tipo_foco = input("Tipo de foco (MONOFOCAL/BIFOCAL/PROGRESSIVA/OCUPACIONAL): ").strip()
                indice_str = input("Índice de refração (ou em branco): ").strip()
                indice = float(indice_str) if indice_str else None
                estoque = int(input("Quantidade em estoque: ").strip() or "0")
                produto = service.cadastrar_lente(descricao, preco, tipo_foco, indice, estoque)
                print(f"Lente cadastrada: {produto}")

            elif escolha == "3":
                # Polimorfismo: cada item chama o mesmo __str__ -> detalhar_produto(),
                # mas o resultado muda conforme o objeto for Armacao ou Lente.
                for p in service.listar():
                    print(p)

            elif escolha == "4":
                criticos = service.listar_em_falta()
                if not criticos:
                    print("Nenhum produto em estoque crítico.")
                for p in criticos:
                    print(p)

            elif escolha == "5":
                id_produto = int(input("ID do produto: ").strip())
                quantidade = int(input("Quantidade a repor: ").strip())
                service.repor_estoque(id_produto, quantidade)
                print("Estoque reposto com sucesso.")

            elif escolha == "6":
                id_produto = int(input("ID do produto a excluir: ").strip())
                service.excluir(id_produto)
                print("Produto excluído com sucesso.")

            elif escolha == "0":
                break

            else:
                print("Opção inválida.")

        except ValueError as e:
            print(f"Erro: {e}")
        except Exception as e:
            print(f"Erro inesperado: {e}")


# =========================================================
# VENDAS (CRUD completo)
# =========================================================
def menu_vendas(venda_service: VendaService, cliente_service: ClienteService,
                produto_service: ProdutoService):
    while True:
        print("\n--- Vendas (CRUD completo) ---")
        print("1 - Registrar nova venda")
        print("2 - Listar todas as vendas")
        print("3 - Buscar venda por ID")
        print("4 - Buscar vendas por cliente")
        print("5 - Editar vendedor de uma venda")
        print("6 - Excluir venda")
        print("0 - Voltar")
        escolha = input("Escolha uma opção: ").strip()

        try:
            if escolha == "1":
                _registrar_venda(venda_service, cliente_service)

            elif escolha == "2":
                vendas = venda_service.listar()
                if not vendas:
                    print("Nenhuma venda registrada.")
                for v in vendas:
                    print(v)
                    for item in v.itens:
                        print(f"    -> {item}")

            elif escolha == "3":
                id_venda = int(input("ID da venda: ").strip())
                venda = venda_service.buscar_por_id(id_venda)
                if not venda:
                    print("Venda não encontrada.")
                else:
                    print(venda)
                    for item in venda.itens:
                        print(f"    -> {item}")

            elif escolha == "4":
                id_cliente = int(input("ID do cliente: ").strip())
                vendas = venda_service.buscar_por_cliente(id_cliente)
                if not vendas:
                    print("Nenhuma venda encontrada para este cliente.")
                for v in vendas:
                    print(v)

            elif escolha == "5":
                id_venda = int(input("ID da venda: ").strip())
                novo_id_vendedor = int(input("Novo ID de vendedor: ").strip())
                venda_service.trocar_vendedor(id_venda, novo_id_vendedor)
                print("Vendedor da venda atualizado com sucesso.")

            elif escolha == "6":
                id_venda = int(input("ID da venda a excluir: ").strip())
                venda_service.excluir(id_venda)
                print("Venda excluída com sucesso (estoque devolvido).")

            elif escolha == "0":
                break

            else:
                print("Opção inválida.")

        except (VendaSemItensError, ValueError) as e:
            print(f"Erro: {e}")
        except Exception as e:
            print(f"Erro inesperado: {e}")


def _registrar_venda(venda_service: VendaService, cliente_service: ClienteService):
    id_cliente = int(input("ID do cliente: ").strip())
    if not cliente_service.buscar_por_id(id_cliente):
        print("Cliente não encontrado.")
        return

    id_vendedor = int(input("ID do vendedor: ").strip())
    receita_str = input("ID da receita (ou em branco se não houver): ").strip()
    id_receita = int(receita_str) if receita_str else None

    venda = venda_service.iniciar_venda(id_cliente, id_vendedor, id_receita)

    while True:
        id_produto_str = input("ID do produto a adicionar (ou ENTER para finalizar): ").strip()
        if not id_produto_str:
            break
        id_produto = int(id_produto_str)
        quantidade = int(input("Quantidade: ").strip())
        venda_service.adicionar_item(venda, id_produto, quantidade)
        print(f"Item adicionado. Total parcial: R$ {venda.valor_total:.2f}")

    venda_service.finalizar_venda(venda)
    print(f"Venda registrada com sucesso! {venda}")
