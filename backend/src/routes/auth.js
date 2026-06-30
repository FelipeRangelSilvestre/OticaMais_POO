// src/routes/auth.js
const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const pool = require('../db/pool');

const router = express.Router();

// POST /api/auth/login  { login, senha }
router.post('/login', async (req, res) => {
  const { login, senha } = req.body;
  if (!login || !senha) return res.status(400).json({ erro: 'Login e senha são obrigatórios.' });

  try {
    const { rows } = await pool.query('SELECT * FROM USUARIO WHERE login = $1', [login]);
    if (!rows.length) return res.status(401).json({ erro: 'Login ou senha inválidos.' });

    const usuario = rows[0];
    const senhaOk = await bcrypt.compare(senha, usuario.senha_hash);
    if (!senhaOk) return res.status(401).json({ erro: 'Login ou senha inválidos.' });

    const token = jwt.sign(
      { id_usuario: usuario.id_usuario, login: usuario.login, papel: usuario.papel, id_vendedor: usuario.id_vendedor },
      process.env.JWT_SECRET,
      { expiresIn: '8h' }
    );

    res.json({ token, usuario: { login: usuario.login, papel: usuario.papel } });
  } catch (err) {
    console.error(err);
    res.status(500).json({ erro: 'Erro ao autenticar.' });
  }
});

// POST /api/auth/cadastro  { login, senha, papel, id_vendedor }
// Em produção, restrinja essa rota a admins autenticados.
router.post('/cadastro', async (req, res) => {
  const { login, senha, papel, id_vendedor } = req.body;
  if (!login || !senha || senha.length < 6) {
    return res.status(400).json({ erro: 'Login e senha (mínimo 6 caracteres) são obrigatórios.' });
  }
  try {
    const hash = await bcrypt.hash(senha, 10);
    const { rows } = await pool.query(
      `INSERT INTO USUARIO (login, senha_hash, papel, id_vendedor) VALUES ($1,$2,$3,$4)
       RETURNING id_usuario, login, papel`,
      [login, hash, papel || 'VENDEDOR', id_vendedor || null]
    );
    res.status(201).json(rows[0]);
  } catch (err) {
    if (err.code === '23505') return res.status(409).json({ erro: 'Login já existe.' });
    console.error(err);
    res.status(500).json({ erro: 'Erro ao cadastrar usuário.' });
  }
});

module.exports = router;
