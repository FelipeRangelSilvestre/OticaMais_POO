// src/routes/medicos.js
const express = require('express');
const pool = require('../db/pool');

const router = express.Router();

router.get('/', async (req, res) => {
  try {
    const { rows } = await pool.query(`
      SELECT m.*, COUNT(r.id_receita)::int AS receitas_emitidas
        FROM MEDICO m
        LEFT JOIN RECEITA r ON r.crm_medico = m.crm
       GROUP BY m.crm
       ORDER BY m.nome`);
    res.json(rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ erro: 'Erro ao buscar médicos.' });
  }
});

router.post('/', async (req, res) => {
  const { crm, nome, especialidade, telefone } = req.body;
  if (!crm || !nome || !especialidade) {
    return res.status(400).json({ erro: 'CRM, nome e especialidade são obrigatórios.' });
  }
  try {
    const { rows } = await pool.query(
      `INSERT INTO MEDICO (crm, nome, especialidade, telefone) VALUES ($1,$2,$3,$4) RETURNING *`,
      [crm, nome, especialidade, telefone || null]
    );
    res.status(201).json(rows[0]);
  } catch (err) {
    if (err.code === '23505') return res.status(409).json({ erro: 'CRM já cadastrado.' });
    console.error(err);
    res.status(500).json({ erro: 'Erro ao cadastrar médico.' });
  }
});

router.put('/:crm', async (req, res) => {
  const { nome, especialidade, telefone } = req.body;
  try {
    const { rows } = await pool.query(
      `UPDATE MEDICO SET nome = COALESCE($1,nome), especialidade = COALESCE($2,especialidade), telefone = $3
       WHERE crm = $4 RETURNING *`,
      [nome, especialidade, telefone || null, req.params.crm]
    );
    if (!rows.length) return res.status(404).json({ erro: 'Médico não encontrado.' });
    res.json(rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ erro: 'Erro ao atualizar médico.' });
  }
});

router.delete('/:crm', async (req, res) => {
  try {
    const { rowCount } = await pool.query('DELETE FROM MEDICO WHERE crm = $1', [req.params.crm]);
    if (!rowCount) return res.status(404).json({ erro: 'Médico não encontrado.' });
    res.status(204).send();
  } catch (err) {
    if (err.code === '23503') return res.status(409).json({ erro: 'Médico possui receitas vinculadas e não pode ser excluído.' });
    console.error(err);
    res.status(500).json({ erro: 'Erro ao excluir médico.' });
  }
});

module.exports = router;
