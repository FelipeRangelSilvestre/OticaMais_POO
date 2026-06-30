// src/routes/produtos.js
const express = require('express');
const pool = require('../db/pool');

const router = express.Router();

// Junta PRODUTO com ARMACAO ou LENTE (a depender do tipo) em uma só linha de resultado
const SQL_LISTAR = `
  SELECT p.*,
         a.marca, a.modelo, a.cor, a.material AS material_armacao,
         l.material AS material_lente, l.tipo_foco, l.indice
    FROM PRODUTO p
    LEFT JOIN ARMACAO a ON a.id_produto = p.id_produto
    LEFT JOIN LENTE   l ON l.id_produto = p.id_produto
`;

// GET /api/produtos?tipo=ARMACAO&busca=texto
router.get('/', async (req, res) => {
  const { tipo, busca } = req.query;
  const where = [];
  const params = [];

  if (tipo) { params.push(tipo); where.push(`p.tipo = $${params.length}`); }
  if (busca) { params.push(`%${busca}%`); where.push(`p.descricao ILIKE $${params.length}`); }

  const sql = SQL_LISTAR + (where.length ? ` WHERE ${where.join(' AND ')}` : '') + ' ORDER BY p.id_produto';

  try {
    const { rows } = await pool.query(sql, params);
    res.json(rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ erro: 'Erro ao buscar produtos.' });
  }
});

router.get('/:id', async (req, res) => {
  try {
    const { rows } = await pool.query(SQL_LISTAR + ' WHERE p.id_produto = $1', [req.params.id]);
    if (!rows.length) return res.status(404).json({ erro: 'Produto não encontrado.' });
    res.json(rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ erro: 'Erro ao buscar produto.' });
  }
});

// POST /api/produtos
// Body esperado:
// { tipo: "ARMACAO", descricao, preco_venda, qtd_estoque, qtd_minima,
//   marca, modelo, cor, material }                      <- se ARMACAO
// { tipo: "LENTE", descricao, preco_venda, qtd_estoque, qtd_minima,
//   material, tipo_foco, indice }                        <- se LENTE
router.post('/', async (req, res) => {
  const { tipo, descricao, preco_venda, qtd_estoque, qtd_minima } = req.body;

  if (!tipo || !['ARMACAO', 'LENTE'].includes(tipo)) {
    return res.status(400).json({ erro: 'Tipo deve ser ARMACAO ou LENTE.' });
  }
  if (preco_venda === undefined || preco_venda < 0) {
    return res.status(400).json({ erro: 'Preço de venda inválido.' });
  }
  if (tipo === 'ARMACAO' && !req.body.marca) {
    return res.status(400).json({ erro: 'Marca é obrigatória para armações.' });
  }
  if (tipo === 'LENTE' && (!req.body.material || !req.body.tipo_foco)) {
    return res.status(400).json({ erro: 'Material e tipo de foco são obrigatórios para lentes.' });
  }

  const client = await pool.connect();
  try {
    await client.query('BEGIN');

    const { rows } = await client.query(
      `INSERT INTO PRODUTO (tipo, descricao, preco_venda, qtd_estoque, qtd_minima)
       VALUES ($1,$2,$3,$4,$5) RETURNING *`,
      [tipo, descricao || null, preco_venda, qtd_estoque || 0, qtd_minima ?? 5]
    );
    const produto = rows[0];

    if (tipo === 'ARMACAO') {
      const { marca, modelo, cor, material } = req.body;
      await client.query(
        `INSERT INTO ARMACAO (id_produto, marca, modelo, cor, material) VALUES ($1,$2,$3,$4,$5)`,
        [produto.id_produto, marca, modelo || null, cor || null, material || null]
      );
    } else {
      const { material, tipo_foco, indice } = req.body;
      await client.query(
        `INSERT INTO LENTE (id_produto, material, tipo_foco, indice) VALUES ($1,$2,$3,$4)`,
        [produto.id_produto, material, tipo_foco, indice || null]
      );
    }

    await client.query('COMMIT'); // dispara a trigger deferred de checagem da subclasse
    res.status(201).json(produto);
  } catch (err) {
    await client.query('ROLLBACK');
    console.error(err);
    res.status(500).json({ erro: 'Erro ao cadastrar produto.', detalhe: err.message });
  } finally {
    client.release();
  }
});

// PATCH /api/produtos/:id/estoque  { delta: 5 }  -- ajuste manual de estoque (ex: reposição)
router.patch('/:id/estoque', async (req, res) => {
  const { delta } = req.body;
  if (typeof delta !== 'number') return res.status(400).json({ erro: 'delta deve ser um número.' });
  try {
    const { rows } = await pool.query(
      `UPDATE PRODUTO SET qtd_estoque = qtd_estoque + $1 WHERE id_produto = $2 RETURNING *`,
      [delta, req.params.id]
    );
    if (!rows.length) return res.status(404).json({ erro: 'Produto não encontrado.' });
    res.json(rows[0]);
  } catch (err) {
    if (err.code === '23514') return res.status(409).json({ erro: 'Ajuste deixaria o estoque negativo.' });
    console.error(err);
    res.status(500).json({ erro: 'Erro ao ajustar estoque.' });
  }
});

router.delete('/:id', async (req, res) => {
  try {
    const { rowCount } = await pool.query('DELETE FROM PRODUTO WHERE id_produto = $1', [req.params.id]);
    if (!rowCount) return res.status(404).json({ erro: 'Produto não encontrado.' });
    res.status(204).send();
  } catch (err) {
    if (err.code === '23503') return res.status(409).json({ erro: 'Produto já possui vendas vinculadas e não pode ser excluído.' });
    console.error(err);
    res.status(500).json({ erro: 'Erro ao excluir produto.' });
  }
});

module.exports = router;
