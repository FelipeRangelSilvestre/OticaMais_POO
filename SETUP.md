# Ótica Mais — Guia de Setup Completo

Este projeto tem **dois componentes**:

| Componente | Tecnologia | O que faz |
|---|---|---|
| `backend/` | Node.js + Express + PostgreSQL | API REST — conecta ao banco e serve os dados |
| `otica_mais.html` | HTML/JS puro | Frontend — abre no navegador e consome a API |

---

## Pré-requisitos

- [Node.js](https://nodejs.org/) v18 ou superior
- [PostgreSQL](https://www.postgresql.org/download/) v14 ou superior (instalado e rodando)
- Um terminal (PowerShell, cmd, bash, etc.)

---

## Passo 1 — Criar o banco de dados no PostgreSQL

Abra o **psql** (ou qualquer cliente como DBeaver / pgAdmin) e execute:

```sql
CREATE DATABASE otica_mais;
```

Depois conecte ao banco e rode o schema:

```bash
# Via terminal (ajuste o usuário se necessário)
psql -U postgres -d otica_mais -f backend/schema.sql
```

Isso cria todas as tabelas, índices e triggers automaticamente.

---

## Passo 2 — Popular o banco com dados iniciais (seed)

```bash
psql -U postgres -d otica_mais -f backend/seed.sql
```

Isso insere clientes, médicos, vendedores, produtos e vendas de exemplo.

**Logins criados pelo seed:**

| Login | Senha | Papel |
|---|---|---|
| `admin` | `admin123` | Administrador |
| `felipe` | `vendedor123` | Vendedor |
| `iasmim` | `vendedor123` | Vendedor |

> ⚠️ Troque as senhas em produção.

---

## Passo 3 — Configurar variáveis de ambiente do backend

Dentro da pasta `backend/`, copie o arquivo de exemplo:

```bash
cd backend
cp .env.example .env
```

Abra o `.env` e ajuste conforme sua instalação do PostgreSQL:

```env
PGHOST=localhost
PGPORT=5432
PGUSER=postgres
PGPASSWORD=sua_senha_aqui
PGDATABASE=otica_mais

PORT=3000

JWT_SECRET=coloque_uma_string_longa_e_aleatoria_aqui

# Opcional — só se quiser usar o Assistente IA
ANTHROPIC_API_KEY=sk-ant-sua-chave-aqui
```

> 💡 Para gerar um JWT_SECRET seguro: `node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"`

---

## Passo 4 — Instalar dependências e iniciar o backend

```bash
cd backend
npm install
npm start
```

Se tudo estiver certo, você verá:

```
API Ótica Mais rodando em http://localhost:3000
```

Para confirmar que a API está funcionando, acesse no navegador:

```
http://localhost:3000/api/health
```

Deve retornar `{"status":"ok"}`.

---

## Passo 5 — Abrir o frontend

Basta abrir o arquivo `otica_mais.html` diretamente no navegador:

- **Windows:** clique duas vezes no arquivo, ou arraste para o Chrome/Firefox
- **Mac/Linux:** `open otica_mais.html` ou `xdg-open otica_mais.html`

> ⚠️ **O backend precisa estar rodando** (`npm start`) antes de abrir o frontend. Caso contrário, todas as telas aparecerão vazias com uma mensagem de erro de conexão.

---

## Estrutura do projeto

```
otica-mais/
├── backend/
│   ├── src/
│   │   ├── db/
│   │   │   ├── pool.js          # Pool de conexões com o PostgreSQL
│   │   │   └── runSeed.js       # Alternativa: rodar seed via npm run seed
│   │   ├── middleware/
│   │   │   └── auth.js          # Middleware de autenticação JWT
│   │   ├── routes/
│   │   │   ├── auth.js          # POST /api/auth/login
│   │   │   ├── clientes.js      # GET/POST/PUT/DELETE /api/clientes
│   │   │   ├── medicos.js       # GET/POST/PUT/DELETE /api/medicos
│   │   │   ├── produtos.js      # GET/POST/PUT/DELETE /api/produtos
│   │   │   ├── vendedores.js    # GET/POST/PUT/DELETE /api/vendedores
│   │   │   ├── receitas.js      # GET/POST /api/receitas
│   │   │   ├── vendas.js        # GET/POST /api/vendas
│   │   │   ├── dashboard.js     # GET /api/dashboard
│   │   │   └── assistente.js    # POST /api/assistente/chat (proxy IA)
│   │   └── server.js            # Entry point do Express
│   ├── schema.sql               # DDL completo do banco (tabelas + triggers)
│   ├── seed.sql                 # Dados iniciais de exemplo
│   ├── .env.example             # Modelo de configuração
│   └── package.json
└── otica_mais.html              # Frontend completo (HTML + CSS + JS)
```

---

## Rotas disponíveis na API

| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/auth/login` | Login — retorna token JWT |
| GET | `/api/clientes` | Listar clientes (aceita `?busca=`) |
| POST | `/api/clientes` | Cadastrar cliente |
| PUT | `/api/clientes/:id` | Editar cliente |
| DELETE | `/api/clientes/:id` | Excluir cliente |
| GET | `/api/medicos` | Listar médicos |
| POST | `/api/medicos` | Cadastrar médico |
| GET | `/api/produtos` | Listar produtos (aceita `?tipo=ARMACAO\|LENTE&busca=`) |
| POST | `/api/produtos` | Cadastrar produto |
| GET | `/api/vendedores` | Listar vendedores |
| POST | `/api/vendedores` | Cadastrar vendedor |
| GET | `/api/receitas` | Listar receitas |
| POST | `/api/receitas` | Cadastrar receita |
| GET | `/api/vendas` | Listar vendas |
| POST | `/api/vendas` | Registrar venda |
| GET | `/api/dashboard` | Métricas do dashboard |
| POST | `/api/assistente/chat` | Enviar mensagem ao Assistente IA |
| GET | `/api/health` | Verificar status da API |

---

## Problemas comuns

**"Não foi possível conectar à API"** no frontend
→ O backend não está rodando. Execute `npm start` dentro de `backend/` e tente novamente.

**"password authentication failed for user postgres"**
→ A senha no `.env` está errada. Verifique `PGPASSWORD` no arquivo `.env`.

**"database otica_mais does not exist"**
→ Execute `CREATE DATABASE otica_mais;` no psql antes de rodar o schema.

**"column X does not exist" ou erro de schema**
→ Rode novamente `psql -U postgres -d otica_mais -f backend/schema.sql`. O script tem `DROP TABLE IF EXISTS` no início, então é seguro reexecutar.

**Frontend abre mas tabelas aparecem vazias (sem erro)**
→ O banco está vazio. Rode o seed: `psql -U postgres -d otica_mais -f backend/seed.sql`

**Porta 3000 já em uso**
→ Altere `PORT=3001` (ou outra) no `.env`, e atualize `API_URL` na linha ~390 do `otica_mais.html` para `http://localhost:3001/api`.
