# Ótica Mais — Backend (Node.js + Express + PostgreSQL)

API REST que conecta o front-end (`otica_mais.html`) a um banco PostgreSQL real.

## 1. Pré-requisitos
- Node.js 18+ instalado
- PostgreSQL instalado (ou via Docker)

## 2. Subir o PostgreSQL (se for via Docker)
```bash
docker run --name otica-postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:16
```
Se já tem o PostgreSQL instalado localmente, só crie o banco:
```bash
createdb otica_mais
```

## 3. Configurar o backend
```bash
cd otica-backend
npm install
cp .env.example .env
```
Abra o `.env` e confira/ajuste `PGUSER`, `PGPASSWORD`, `PGDATABASE` conforme sua instalação.
Coloque sua chave da Anthropic em `ANTHROPIC_API_KEY` (só é necessária para o chat de IA).

## 4. Criar as tabelas
```bash
psql -h localhost -U postgres -d otica_mais -f schema.sql
```
(vai pedir a senha do Postgres — a mesma que você colocou no `.env`)

## 5. Popular com dados de exemplo (iguais aos do front mockado)
```bash
npm run seed
```
Isso cria os mesmos clientes, produtos, vendas e receitas que já estavam no `otica_mais.html`,
mais 3 usuários de login:
- `admin` / `admin123` (papel ADMIN)
- `felipe` / `vendedor123`
- `iasmim` / `vendedor123`

**Troque essas senhas antes de usar em produção.**

## 6. Rodar a API
```bash
npm start
```
A API sobe em `http://localhost:3000`. Teste com:
```bash
curl http://localhost:3000/api/health
```

## Endpoints principais
| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/auth/login` | Login, retorna token JWT |
| GET/POST | `/api/clientes` | Listar/criar clientes |
| GET/POST | `/api/medicos` | Listar/criar médicos |
| GET/POST | `/api/produtos` | Listar/criar produtos (armação ou lente) |
| PATCH | `/api/produtos/:id/estoque` | Ajustar estoque manualmente |
| GET/POST | `/api/vendedores` | Listar/criar vendedores |
| GET/POST | `/api/receitas` | Listar/criar receitas |
| GET/POST | `/api/vendas` | Listar/criar vendas (desconta estoque automaticamente) |
| DELETE | `/api/vendas/:id` | Cancelar venda (devolve estoque) |
| GET | `/api/dashboard` | Métricas para a tela inicial |
| POST | `/api/assistente/chat` | Chat com IA (a chave fica só no servidor) |

## O que mudou em relação à versão anterior do schema.sql
- **Trigger de estoque/total unificada**: agora valida se há estoque suficiente antes de
  vender (antes não validava) e recalcula o total da venda em vez de só acumular
  (evita duplicação se um item for editado).
- **Trigger de consistência ARMACAO/LENTE**: garante que todo produto tem a linha de
  detalhe correta e nunca as duas ao mesmo tempo.
- **Tabela USUARIO**: login do sistema, vinculado opcionalmente a um vendedor.
- Pequenos ajustes de índice e `ON UPDATE CASCADE`.

## Como ligar ao front-end (`otica_mais.html`)
O arquivo `otica_mais.html` já foi adaptado para consumir esta API em vez de usar
dados mockados. Para rodar tudo junto:

1. Suba o backend (passos 1 a 6 acima) — ele fica em `http://localhost:3000`.
2. Abra o `otica_mais.html` direto no navegador (duplo clique no arquivo, ou
   `npx serve` na pasta dele, ou qualquer servidor estático). Não precisa
   rodar na mesma porta do backend — o front já está configurado para chamar
   `http://localhost:3000/api/...` via `fetch`, e o `cors()` no servidor já
   libera isso.
3. Se aparecer um erro de "Não foi possível conectar à API" no dashboard,
   confira se o backend está rodando (`npm start`) e se a porta no `.env`
   bate com a constante `API_URL` no topo do `<script>` do HTML.

### O que mudou no front
- O objeto `DB` fixo virou `let DB = {...}` vazio, populado via `fetch` antes de cada renderização.
- Funções `adaptarProduto`, `adaptarReceita`, `adaptarVenda` traduzem os nomes de
  coluna do banco (`preco_venda`, `qtd_estoque`, `data_venda`...) para os nomes que
  o restante do código já usava (`preco`, `estoque`, `data`...), então a lógica
  visual não precisou ser reescrita.
- `salvarCliente`, `salvarMedico`, `salvarProduto`, `salvarReceita`, `salvarVenda`
  agora enviam `POST` para a API em vez de empurrar para um array local.
- `salvarVenda` não desconta mais o estoque no JavaScript — isso agora é feito
  pela trigger do PostgreSQL, e o front só mostra a mensagem de erro do backend
  se o estoque for insuficiente.
- O chat de IA chama `/api/assistente/chat` (no seu backend) em vez de
  `api.anthropic.com` direto — a chave nunca chega ao navegador.
