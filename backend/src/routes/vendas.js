// src/routes/vendas.js
const express = require('express');
const pool = require('../db/pool');

const router = express.Router();

const SQL_LISTAR = `
  SELECT v.*, c.nome AS nome_cliente, ve.nome AS nome_vendedor,
         (SELECT COUNT(*) FROM ITEM_VENDA iv WHERE iv.id_venda = v.id_venda)::int AS qtd_itens
    FROM VENDA v
    JOIN CLIENTE c   ON c.id_cliente = v.id_cliente
    JOIN VENDEDOR ve ON ve.id_vendedor = v.id_vendedor
`;

router.get('/', async (req, res) => {
  try {
    const { rows } = await pool.query(SQL_LISTAR + ' ORDER BY v.data_venda DESC, v.id_venda DESC');
    res.json(rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ erro: 'Erro ao buscar vendas.' });
  }
});

router.get('/:id', async (req, res) => {
  try {
    const { rows } = await pool.query(SQL_LISTAR + ' WHERE v.id_venda = $1', [req.params.id]);
    if (!rows.length) return res.status(404).json({ erro: 'Venda não encontrada.' });

    const itens = await pool.query(
      `SELECT iv.*, p.descricao FROM ITEM_VENDA iv JOIN PRODUTO p ON p.id_produto = iv.id_produto WHERE iv.id_venda = $1`,
      [req.params.id]
    );
    res.json({ ...rows[0], itens: itens.rows });
  } catch (err) {
    console.error(err);
    res.status(500).json({ erro: 'Erro ao buscar venda.' });
  }
});

// POST /api/vendas
// Body: { id_cliente, id_vendedor, id_receita, itens: [{ id_produto, quantidade, valor_unitario }] }
// As triggers do banco descontam o estoque e calculam o valor_total — o backend não calcula isso.
router.post('/', async (req, res) => {
  const { id_cliente, id_vendedor, id_receita, itens } = req.body;

  if (!id_cliente || !id_vendedor) {
    return res.status(400).json({ erro: 'Cliente e vendedor são obrigatórios.' });
  }
  if (!Array.isArray(itens) || itens.length === 0) {
    return res.status(400).json({ erro: 'Adicione ao menos um item à venda.' });
  }
  for (const item of itens) {
    if (!item.id_produto || !item.quantidade || item.quantidade <= 0) {
      return res.status(400).json({ erro: 'Cada item precisa de id_produto e quantidade > 0.' });
    }
  }

  const client = await pool.connect();
  try {
    await client.query('BEGIN');

    const { rows } = await client.query(
      `INSERT INTO VENDA (id_cliente, id_vendedor, id_receita) VALUES ($1,$2,$3) RETURNING *`,
      [id_cliente, id_vendedor, id_receita || null]
    );
    const venda = rows[0];

    for (const item of itens) {
      // A trigger fn_estoque_e_total_venda valida o estoque aqui;
      // se faltar estoque, ela lança exceção e cai no catch -> ROLLBACK.
      await client.query(
        `INSERT INTO ITEM_VENDA (id_venda, id_produto, quantidade, valor_unitario) VALUES ($1,$2,$3,$4)`,
        [venda.id_venda, item.id_produto, item.quantidade, item.valor_unitario]
      );
    }

    await client.query('COMMIT');

    const { rows: vendaFinal } = await pool.query(SQL_LISTAR + ' WHERE v.id_venda = $1', [venda.id_venda]);
    res.status(201).json(vendaFinal[0]);
  } catch (err) {
    await client.query('ROLLBACK');
    if (err.message && err.message.includes('Estoque insuficiente')) {
      return res.status(409).json({ erro: err.message });
    }
    console.error(err);
    res.status(500).json({ erro: 'Erro ao registrar venda.' });
  } finally {
    client.release();
  }
});

// DELETE /api/vendas/:id  -- cancela a venda e devolve o estoque (via trigger de DELETE em ITEM_VENDA)
router.delete('/:id', async (req, res) => {
  try {
    const { rowCount } = await pool.query('DELETE FROM VENDA WHERE id_venda = $1', [req.params.id]);
    if (!rowCount) return res.status(404).json({ erro: 'Venda não encontrada.' });
    res.status(204).send();
  } catch (err) {
    console.error(err);
    res.status(500).json({ erro: 'Erro ao cancelar venda.' });
  }
});

module.exports = router;
