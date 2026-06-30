// src/server.js
require('dotenv').config();
const express = require('express');
const cors = require('cors');

const authRoutes = require('./routes/auth');
const clientesRoutes = require('./routes/clientes');
const medicosRoutes = require('./routes/medicos');
const produtosRoutes = require('./routes/produtos');
const vendedoresRoutes = require('./routes/vendedores');
const receitasRoutes = require('./routes/receitas');
const vendasRoutes = require('./routes/vendas');
const dashboardRoutes = require('./routes/dashboard');
const assistenteRoutes = require('./routes/assistente');

const app = express();

app.use(cors());
app.use(express.json());

// Rotas públicas
app.use('/api/auth', authRoutes);

// Rotas da aplicação
// Obs: para exigir login, adicione o middleware exigirLogin antes de cada router,
// ex: app.use('/api/vendas', exigirLogin, vendasRoutes);
app.use('/api/clientes', clientesRoutes);
app.use('/api/medicos', medicosRoutes);
app.use('/api/produtos', produtosRoutes);
app.use('/api/vendedores', vendedoresRoutes);
app.use('/api/receitas', receitasRoutes);
app.use('/api/vendas', vendasRoutes);
app.use('/api/dashboard', dashboardRoutes);
app.use('/api/assistente', assistenteRoutes);

app.get('/api/health', (req, res) => res.json({ status: 'ok' }));

// Tratamento de rota não encontrada
app.use((req, res) => res.status(404).json({ erro: 'Rota não encontrada.' }));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`API Ótica Mais rodando em http://localhost:${PORT}`);
});
