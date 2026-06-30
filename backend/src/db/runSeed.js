// src/db/runSeed.js
// Roda o seed.sql contra o banco configurado no .env.
// Uso: npm run seed
const fs = require('fs');
const path = require('path');
const pool = require('./pool');

async function main() {
  const seedPath = path.join(__dirname, '..', '..', 'seed.sql');
  const sql = fs.readFileSync(seedPath, 'utf8');
  try {
    await pool.query(sql);
    console.log('Seed executado com sucesso.');
  } catch (err) {
    console.error('Erro ao executar o seed:', err.message);
    process.exitCode = 1;
  } finally {
    await pool.end();
  }
}

main();
