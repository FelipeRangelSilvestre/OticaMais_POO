from models.cliente import Cliente
from models.produto import Produto
from models.venda import Venda
from repositories.cliente_repository import ClienteRepository

def menu():
    repo = ClienteRepository()
    
    while True:
        print("\n" + "="*65)
        print("👓 ÓTICA MAIS — SISTEMA CORE EM PYTHON (AVALIAÇÃO POO) 👓")
        print("="*65)
        print("1. Cadastrar Novo Cliente (INSERT)")
        print("2. Listar Clientes (SELECT + Polimorfismo da Classe Abstrata)")
        print("3. Atualizar endereço do Cliente (UPDATE)")
        print("4. Excluir Cliente (DELETE)")
        print("5. Demonstrar Regra de Negócio")
        print("0. Sair do Sistema")
        
        opcao = input("\nSelecione uma operação: ")

        if opcao == '1':
            nome = input("Nome do Cliente: ")
            cpf = input("CPF (11 dígitos): ")
            endereco = input("Endereço: ")
            novo_cliente = Cliente(id_pessoa=0, nome=nome, cpf=cpf, endereco=endereco)
            repo.inserir(novo_cliente)

        elif opcao == '2':
            clientes = repo.listar_todos()
            print("\n--- REGISTOS NA BASE DE DADOS ---")
            for c in clientes:
                # O Python invoca o método mágico __str__ automaticamente ao fazer print(c)
                # O exibir_resumo() demonstra o contrato da classe abstrata Pessoa
                print(f"ID: {c.id_pessoa} | {c} -> {c.exibir_resumo()}")

        elif opcao == '3':
            id_cli = int(input("Insira o ID do Cliente a atualizar: "))
            novo_end = input("Escreva o novo endereço: ")
            repo.atualizar_endereco(id_cli, novo_end)

        elif opcao == '4':
            id_cli = int(input("Insira o ID do Cliente a excluir: "))
            repo.excluir(id_cli)

        elif opcao == '5':
            print("\n--- TESTE DE INTEGRIDADE: REGRA DE NEGÓCIO E EXCEÇÕES ---")
            try:
                # Instanciação de objetos em memória para demonstrar o domínio
                cliente_teste = Cliente(id_pessoa=99, nome="Prof. Avaliador", cpf="00000000000", endereco="UFAM")
                lente = Produto(id_produto=1, descricao="Lente de Contacto Oasys", preco=250.00, estoque=10)
                nova_venda = Venda(id_venda=1001, cliente=cliente_teste)
                
                print("[Engine] Objeto Venda instanciado. O carrinho encontra-se vazio.")
                print("[Engine] A tentar invocar finalizar_venda() sem itens...")
                
                # Esta chamada viola a regra de negócio e vai disparar o Raise Exception
                nova_venda.finalizar_venda()
                
            except Exception as erro:
                print(f"❌ Exceção Capturada pelo Sistema: {erro}")
                print("[Engine] A aplicar fluxo de correção: a injetar Produto no carrinho...")
                
                # Corrige o fluxo e finaliza
                nova_venda.adicionar_item(lente)
                total = nova_venda.finalizar_venda()
                print(f"✅ Transação Finalizada com Sucesso! Valor Total da Nota: R$ {total:.2f}")

        elif opcao == '0':
            print("\nA encerrar o pool de ligações com o PostgreSQL... Até logo!")
            break
        else:
            print("\nOpção inválida. Verifique a entrada e tente novamente.")

if __name__ == "__main__":
    menu()