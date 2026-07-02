# Ótica Mais — Sistema de Gestão 👓

**Trabalho Prático - Programação Orientada a Objetos e Banco de Dados**  
**Instituto de Ciências Exatas e Tecnologia (ICET/UFAM)**  
**Disciplina:** Programação Oirentada a Objetos e Bancos de Dados 1 
**Professor:** Alternei Brito e Edson Silva

## Integrantes do Grupo

- Felipe Rangel Silvestre 
- Iasmim Braga Belém

---

# 📌 Sobre o Sistema e Arquitetura Dual

A **Ótica Mais** é um sistema de gestão desenvolvido para otimizar o fluxo de uma ótica, contemplando o gerenciamento de clientes, produtos e vendas.

Para demonstrar proficiência técnica e ir além do escopo da disciplina, o projeto foi dividido em duas frentes arquiteturais:

1. **Python Core (`/python_core`)**
   - Núcleo principal do sistema, desenvolvido em **Python** utilizando **psycopg2**.
   - Esta camada contém **100% dos requisitos de avaliação da disciplina**, incluindo:
     - Programação Orientada a Objetos (POO);
     - Herança;
     - Classes Abstratas;
     - CRUD em terminal.

2. **Web API RESTful (`/backend`)**
   - Implementação complementar desenvolvida em **Node.js/Express**.
   - Possui uma interface Web (HTML/CSS/JavaScript) que consome a API utilizando o mesmo banco de dados PostgreSQL.

---

# 🎯 Mapeamento dos Critérios de Avaliação (Python Core)

Todo o código referente à avaliação encontra-se na pasta:

```text
/python_core
```

---

## 1. Modelagem Orientada a Objetos e Pacotes

O projeto segue a arquitetura em camadas solicitada pela disciplina.

### Estrutura

- `models/`
  - Contém as quatro classes de domínio exigidas:
    - `Pessoa`
    - `Cliente`
    - `Produto`
    - `Venda`
  - Utiliza encapsulamento por meio de atributos privados (`__atributo`) e `@property`.

- `repositories/`
  - Camada responsável pelo acesso ao banco de dados.

- `main.py`
  - Ponto de entrada da aplicação em terminal.

---

## 2. Herança, Abstração e Polimorfismo

### Herança

A classe `Cliente` herda da superclasse `Pessoa`.

### Classe Abstrata

A classe `Pessoa` herda de `ABC (Abstract Base Class)` e define o método abstrato:

```python
@abstractmethod
def exibir_resumo():
```

Dessa forma, não é possível instanciar diretamente uma pessoa genérica.

### Polimorfismo

O método `exibir_resumo()` é implementado pela classe `Cliente`, retornando informações específicas (como a morada) e sendo utilizado de forma polimórfica durante a listagem dos clientes.

### Método Mágico

Foi implementado o método:

```python
__str__()
```

para representar os objetos de forma textual.

---

## 3. Banco de Dados e CRUD

O sistema utiliza PostgreSQL integrado diretamente ao Python por meio da biblioteca **psycopg2**.

### Características

- Integração direta com PostgreSQL.
- Utilização de **Herança Física** no banco de dados:
  - A tabela `CLIENTE` possui chave estrangeira referenciando a tabela `PESSOA`.

### CRUD Completo

A entidade **Cliente** possui todas as operações implementadas:

- ✅ INSERT
- ✅ SELECT
- ✅ UPDATE (Morada)
- ✅ DELETE

---

## 4. Regras de Negócio e Tratamento de Exceções

As regras de negócio são protegidas por tratamento de exceções utilizando:

- `try`
- `except`
- `raise`

### Regras implementadas

- A classe `Venda` impede a finalização de um pedido caso o carrinho esteja vazio.
  - Uma exceção é lançada e tratada no terminal.

- Bloqueio de CPF duplicado.
  - A restrição é garantida pelo PostgreSQL e tratada na aplicação.

---

# ⚙️ Como Executar o Projeto

## Passo 1 — Configuração do Banco de Dados

1. Abra o **pgAdmin**.
2. Crie um banco chamado:

```text
otica_mais
```

3. Execute o arquivo:

```text
schema.sql
```

Responsável por criar:

- tabelas;
- constraints;
- triggers.

4. Em seguida execute:

```text
seed.sql
```

para inserir os dados iniciais.

---

## Passo 2 — Executando o Sistema Principal (Python)

Abra um terminal e navegue até a pasta:

```bash
cd python_core
```

Instale o driver do PostgreSQL:

```bash
pip install psycopg2-binary
```

Execute o sistema:

```bash
python main.py
```

> **Observação:** Atualize a variável `password` localizada em `repositories/cliente_repository.py` com a senha do seu PostgreSQL local.

---

## Passo 3 — Executando a Interface Web 

Abra outro terminal.

Entre na pasta:

```bash
cd backend
```

Instale as dependências:

```bash
npm install
```

Crie um arquivo:

```text
.env
```

com as credenciais do PostgreSQL.

Depois inicie o servidor:

```bash
node src/server.js
```

Por fim, abra o arquivo:

```text
otica_mais.html
```

em seu navegador para utilizar a interface gráfica consumindo a API.

---

# ✅ Considerações Finais

Este documento demonstra o mapeamento entre os requisitos da disciplina e sua implementação no projeto, facilitando a verificação dos critérios de avaliação.

A arquitetura foi organizada de forma que:

- o **Python Core** concentre todos os requisitos obrigatórios da disciplina;
- a **API REST** e a interface Web representem uma expansão do projeto, demonstrando conhecimentos adicionais em desenvolvimento Full Stack sem interferir na avaliação principal.