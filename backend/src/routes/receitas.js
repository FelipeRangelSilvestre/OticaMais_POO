// src/routes/receitas.js
const express = require('express');
const pool = require('../db/pool');

const router = express.Router();

const SQL_LISTAR = `
  SELECT r.*, c.nome AS nome_cliente, m.nome AS nome_medico,
         CASE
           WHEN r.validade < CURRENT_DATE THEN 'VENCIDA'
           WHEN r.validade <= CURRENT_DATE + INTERVAL '30 days' THEN 'VENCE_EM_BREVE'
           ELSE 'VALIDA'
         END AS status
    FROM RECEITA r
    JOIN CLIENTE c ON c.id_cliente = r.id_cliente
    JOIN MEDICO  m ON m.crm = r.crm_medico
`;

router.get('/', async (req, res) => {
  try {
    const { rows } = await pool.query(SQL_LISTAR + ' ORDER BY r.id_receita DESC');
    res.json(rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ erro: 'Erro ao buscar receitas.' });
  }
});

router.post('/', async (req, res) => {
  const {
    id_cliente, crm_medico, data_emissao, validade,
    od_esferico, od_cilindrico, od_eixo,
    oe_esferico, oe_cilindrico, oe_eixo,
  } = req.body;

  if (!id_cliente || !crm_medico || !data_emissao || !validade) {
    return res.status(400).json({ erro: 'Cliente, médico, emissão e validade são obrigatórios.' });
  }
  if (od_esferico === undefined || oe_esferico === undefined) {
    return res.status(400).json({ erro: 'Esférico de OD e OE são obrigatórios.' });
  }
  if (validade <= data_emissao) {
    return res.status(400).json({ erro: 'A validade deve ser posterior à data de emissão.' });
  }
  const eixos = [od_eixo, oe_eixo].filter((e) => e !== undefined && e !== null);
  if (eixos.some((e) => e < 0 || e > 180)) {
    return res.status(400).json({ erro: 'Eixo deve estar entre 0 e 180.' });
  }

  try {
    const { rows } = await pool.query(
      `INSERT INTO RECEITA
         (data_emissao, validade, od_esferico, od_cilindrico, od_eixo,
          oe_esferico, oe_cilindrico, oe_eixo, id_cliente, crm_medico)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10) RETURNING *`,
      [data_emissao, validade, od_esferico, od_cilindrico || 0, od_eixo || 0,
       oe_esferico, oe_cilindrico || 0, oe_eixo || 0, id_cliente, crm_medico]
    );
    res.status(201).json(rows[0]);
  } catch (err) {
    if (err.code === '23503') return res.status(400).json({ erro: 'Cliente ou médico inexistente.' });
    console.error(err);
    res.status(500).json({ erro: 'Erro ao cadastrar receita.' });
  }
});

module.exports = router;
