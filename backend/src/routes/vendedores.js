// src/routes/vendedores.js
const express = require('express');
const pool = require('../db/pool');

const router = express.Router();

router.get('/', async (req, res) => {
  try {
    const { rows } = await pool.query(`
      SELECT v.*,
             COUNT(ve.id_venda)::int AS vendas_realizadas,
             COALESCE(SUM(ve.valor_total), 0) AS total_vendido
        FROM VENDEDOR v
        LEFT JOIN VENDA ve ON ve.id_vendedor = v.id_vendedor
       GROUP BY v.id_vendedor
       ORDER BY v.nome`);
    res.json(rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ erro: 'Erro ao buscar vendedores.' });
  }
});

router.post('/', async (req, res) => {
  const { nome, cpf, telefone, email } = req.body;
  if (!nome || !cpf || !/^\d{11}$/.test(cpf)) {
    return res.status(400).json({ erro: 'Nome e CPF (11 dígitos numéricos) são obrigatórios.' });
  }
  try {
    const { rows } = await pool.query(
      `INSERT INTO VENDEDOR (nome, cpf, telefone, email) VALUES ($1,$2,$3,$4) RETURNING *`,
      [nome, cpf, telefone || null, email || null]
    );
    res.status(201).json(rows[0]);
  } catch (err) {
    if (err.code === '23505') return res.status(409).json({ erro: 'CPF já cadastrado.' });
    console.error(err);
    res.status(500).json({ erro: 'Erro ao cadastrar vendedor.' });
  }
});

module.exports = router;
