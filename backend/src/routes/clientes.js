const express = require('express');
const router = express.Router();
const pool = require('../db/pool');

// =========================================================================
// ROTA: GET /api/clientes (Listar todos os clientes)
// =========================================================================
router.get('/', async (req, res) => {
    try {
        // Como a sua tabela CLIENTE já contém todas as colunas da PESSOA, 
        // o JOIN não é necessário! Apenas fazemos um SELECT simples.
        const result = await pool.query(`
            SELECT id_cliente, nome, cpf, telefone, email, endereco 
              FROM CLIENTE 
             ORDER BY nome ASC
        `);
        res.json(result.rows);
    } catch (error) {
        console.error("Erro ao listar clientes:", error);
        res.status(500).json({ erro: 'Erro interno no servidor ao buscar clientes.' });
    }
});

// =========================================================================
// ROTA: POST /api/clientes (Cadastrar novo cliente)
// =========================================================================
router.post('/', async (req, res) => {
    const { nome, cpf, telefone, email, endereco } = req.body;

    try {
        // Inserção direta e única na tabela CLIENTE com todos os dados
        const result = await pool.query(`
            INSERT INTO CLIENTE (nome, cpf, telefone, email, endereco) 
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id_cliente
        `, [nome, cpf, telefone, email, endereco]);

        res.status(201).json({ 
            mensagem: 'Cliente cadastrado com sucesso!', 
            id_cliente: result.rows[0].id_cliente 
        });

    } catch (error) {
        console.error("Erro ao cadastrar cliente:", error);
        
        // Mantemos o tratamento elegante para CPF duplicado
        if (error.code === '23505') {
            return res.status(400).json({ erro: 'Este CPF já está cadastrado no sistema.' });
        }
        res.status(500).json({ erro: 'Erro interno ao cadastrar o cliente.' });
    }
});

module.exports = router;