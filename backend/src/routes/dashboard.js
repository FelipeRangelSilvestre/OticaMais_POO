// src/routes/dashboard.js
const express = require('express');
const pool = require('../db/pool');

const router = express.Router();

router.get('/', async (req, res) => {
  try {
    const [clientes, vendas, receitaTotal, criticos, vendasRecentes, estoqueCritico, maisVendidos] = await Promise.all([
      pool.query('SELECT COUNT(*)::int AS total FROM CLIENTE'),
      pool.query('SELECT COUNT(*)::int AS total FROM VENDA'),
      pool.query('SELECT COALESCE(SUM(valor_total),0) AS total FROM VENDA'),
      pool.query('SELECT COUNT(*)::int AS total FROM PRODUTO WHERE qtd_estoque <= qtd_minima'),
      pool.query(`
        SELECT v.id_venda, v.data_venda, v.valor_total, c.nome AS nome_cliente
          FROM VENDA v JOIN CLIENTE c ON c.id_cliente = v.id_cliente
         ORDER BY v.data_venda DESC, v.id_venda DESC LIMIT 5`),
      pool.query(`
        SELECT id_produto, descricao, qtd_estoque, qtd_minima
          FROM PRODUTO WHERE qtd_estoque <= qtd_minima
         ORDER BY qtd_estoque ASC`),
      pool.query(`
        SELECT p.id_produto, p.descricao, SUM(iv.quantidade)::int AS qtd_vendida
          FROM ITEM_VENDA iv JOIN PRODUTO p ON p.id_produto = iv.id_produto
         GROUP BY p.id_produto, p.descricao
         ORDER BY qtd_vendida DESC LIMIT 5`),
    ]);

    res.json({
      total_clientes: clientes.rows[0].total,
      total_vendas: vendas.rows[0].total,
      receita_total: receitaTotal.rows[0].total,
      estoque_critico_qtd: criticos.rows[0].total,
      vendas_recentes: vendasRecentes.rows,
      estoque_critico: estoqueCritico.rows,
      produtos_mais_vendidos: maisVendidos.rows,
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ erro: 'Erro ao montar dashboard.' });
  }
});

module.exports = router;
