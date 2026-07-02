// src/db/pool.js
const { Pool } = require('pg');
require('dotenv').config(); // Carrega as variáveis do ficheiro .env

// Configuração do Pool de conexões utilizando variáveis de ambiente
const pool = new Pool({
    user: process.env.DB_USER || 'postgres',
    host: process.env.DB_HOST || 'localhost',
    database: process.env.DB_NAME || 'otica_mais',
    // Substitui temporariamente a variável pela tua password real em formato de texto:
    password: 'POO2026', 
    port: process.env.DB_PORT || 5432,
    max: 10,
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 2000,
});

// Eventos de monitorização do ciclo de vida das ligações (Excelente para Debug)
pool.on('connect', () => {
    console.log('⚡ Ligação estável estabelecida com o pool do PostgreSQL!');
});

pool.on('error', (err) => {
    console.error('❌ Erro inesperado no pool de conexões do PostgreSQL:', err.message);
});

module.exports = pool;