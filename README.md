# Ótica Mais — Sistema de Gestão (POO + PostgreSQL)

## Integrantes
- Felipe Rangel
- Iasmim Braga

## Descrição do sistema

Sistema de gestão para uma ótica, desenvolvido em **Python** com **Programação
Orientada a Objetos** e persistência em **PostgreSQL** (via `psycopg2`).

O domínio reaproveita o modelo de dados da disciplina de Banco de Dados, já
convertido para PostgreSQL (`database/schema.sql`), agora modelado também
como classes Python.

### Conceitos de POO aplicados

| Conceito | Onde está |
|---|---|
| Classes e objetos | `Cliente`, `Medico`, `Vendedor`, `Armacao`, `Lente`, `Receita`, `Venda`, `ItemVenda` |
| Encapsulamento | Atributos privados (`__atributo`) com `@property` em `Pessoa`, `Cliente`, `Produto`, `Venda` |
| Herança | `Pessoa` → `Cliente`, `Medico`, `Vendedor` &nbsp;&nbsp;e&nbsp;&nbsp; `Produto` → `Armacao`, `Lente` |
| Polimorfismo | `apresentar()` (Pessoa) e `detalhar_produto()` (Produto): mesmo método, comportamento diferente por subclasse. `Produto.__str__()` chama `detalhar_produto()` polimorficamente, sem saber se é Armação ou Lente |
| Classe abstrata (ABC) | `Pessoa` e `Produto`, ambas com `@abstractmethod` |
| `__str__` | implementado em todas as classes principais |
| Tratamento de exceções | `VendaSemItensError`, `CpfDuplicadoError`, além de `ValueError` nas validações (CPF, preço negativo, estoque insuficiente) |

### Entidade com CRUD completo
**Venda** (junto com `ItemVenda`) possui Create, Read, Update e Delete completos:
- **Create:** registra venda com itens; valida que não há venda sem itens
  (`VendaSemItensError`) e que não há venda com estoque insuficiente
  (`ValueError` vindo de `Produto.atualizar_estoque`);
- **Read:** lista todas, busca por ID, busca por cliente;
- **Update:** permite trocar o vendedor ou a receita associada à venda;
- **Delete:** exclui a venda e devolve o estoque dos produtos automaticamente.

> **Nota sobre a trigger do banco:** o `schema.sql` contém a trigger
> `trg_item_venda_after`, que atualiza `valor_total` da venda e baixa o
> estoque automaticamente a cada `INSERT` em `item_venda`. Por isso, o
> `VendaService` e o `VendaRepository` **não duplicam** essa baixa de
> estoque em Python no momento de salvar — eles confiam na trigger. A
> validação de estoque insuficiente acontece **antes** de gravar, simulando
> a operação em memória com `Produto.atualizar_estoque()`.

## Organização do projeto

```
otica_mais/
│
├── main.py
├── requirements.txt
├── models/          → Pessoa (ABC) → Cliente, Medico, Vendedor
│                      Produto (ABC) → Armacao, Lente
│                      Receita, Venda, ItemVenda
├── repositories/    → acesso ao banco (SQL puro via psycopg2)
├── services/        → regras de negócio
├── ui/              → menu textual no terminal
└── database/        → db_connection.py (conexão) + schema.sql (estrutura)
```

## Banco de dados

`database/schema.sql` já está em PostgreSQL e cria todas as tabelas,
índices, a função PL/pgSQL e a trigger de atualização automática.

## Como executar

1. Crie um banco PostgreSQL vazio chamado `otica_mais` (ou ajuste o nome em
   `database/db_connection.py`).
2. Edite `database/db_connection.py` e informe sua senha do PostgreSQL.
3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
4. Execute o sistema (na primeira vez, ele cria as tabelas automaticamente
   a partir do `schema.sql`):
   ```
   python main.py
   ```

## Restrições atendidas
- Modelagem orientada a objetos real (não apenas funções);
- Código dividido em múltiplos arquivos/pacotes;
- Persistência completa em banco relacional (PostgreSQL).
