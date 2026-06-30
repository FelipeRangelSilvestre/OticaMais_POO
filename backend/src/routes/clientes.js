// src/routes/clientes.js
const express = require('express');
const pool = require('../db/pool');

const router = express.Router();

// GET /api/clientes?busca=texto
router.get('/', async (req, res) => {
  const { busca } = req.query;
  try {
    const where = busca ? `WHERE c.nome ILIKE $1 OR c.cpf ILIKE $1` : '';
    const params = busca ? [`%${busca}%`] : [];
    const sql = `
      SELECT c.*, COUNT(r.id_receita)::int AS receitas_count
        FROM CLIENTE c
        LEFT JOIN RECEITA r ON r.id_cliente = c.id_cliente
        ${where}
       GROUP BY c.id_cliente
       ORDER BY c.nome`;
    const { rows } = await pool.query(sql, params);
    res.json(rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ erro: 'Erro ao buscar clientes.' });
  }
});

// GET /api/clientes/:id
router.get('/:id', async (req, res) => {
  try {
    const { rows } = await pool.query('SELECT * FROM CLIENTE WHERE id_cliente = $1', [req.params.id]);
    if (!rows.length) return res.status(404).json({ erro: 'Cliente não encontrado.' });
    res.json(rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ erro: 'Erro ao buscar cliente.' });
  }
});

// POST /api/clientes
router.post('/', async (req, res) => {
  const { nome, cpf, telefone, email, endereco } = req.body;

  if (!nome || !cpf || !/^\d{11}$/.test(cpf)) {
    return res.status(400).json({ erro: 'Nome e CPF (11 dígitos numéricos) são obrigatórios.' });
  }

  try {
    const { rows } = await pool.query(
      `INSERT INTO CLIENTE (nome, cpf, telefone, email, endereco)
       VALUES ($1, $2, $3, $4, $5) RETURNING *`,
      [nome, cpf, telefone || null, email || null, endereco || null]
    );
    res.status(201).json(rows[0]);
  } catch (err) {
    if (err.code === '23505') { // unique_violation (cpf duplicado)
      return res.status(409).json({ erro: 'CPF já cadastrado.' });
    }
    console.error(err);
    res.status(500).json({ erro: 'Erro ao cadastrar cliente.' });
  }
});

// PUT /api/clientes/:id
router.put('/:id', async (req, res) => {
  const { nome, telefone, email, endereco } = req.body;
  try {
    const { rows } = await pool.query(
      `UPDATE CLIENTE SET nome = COALESCE($1, nome), telefone = $2, email = $3, endereco = $4
       WHERE id_cliente = $5 RETURNING *`,
      [nome, telefone || null, email || null, endereco || null, req.params.id]
    );
    if (!rows.length) return res.status(404).json({ erro: 'Cliente não encontrado.' });
    res.json(rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ erro: 'Erro ao atualizar cliente.' });
  }
});

// DELETE /api/clientes/:id
router.delete('/:id', async (req, res) => {
  try {
    const { rowCount } = await pool.query('DELETE FROM CLIENTE WHERE id_cliente = $1', [req.params.id]);
    if (!rowCount) return res.status(404).json({ erro: 'Cliente não encontrado.' });
    res.status(204).send();
  } catch (err) {
    if (err.code === '23503') { // foreign_key_violation
      return res.status(409).json({ erro: 'Cliente possui vendas ou receitas vinculadas e não pode ser excluído.' });
    }
    console.error(err);
    res.status(500).json({ erro: 'Erro ao excluir cliente.' });
  }
});

module.exports = router;
