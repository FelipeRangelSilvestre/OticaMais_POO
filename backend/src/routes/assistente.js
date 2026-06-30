// src/routes/assistente.js
// Proxy seguro para a API da Anthropic: a chave fica só aqui no servidor,
// nunca é enviada ao navegador (resolve o problema de segurança do front original).
const express = require('express');
const pool = require('../db/pool');

const router = express.Router();

async function montarContexto() {
  const [clientes, produtos, vendas, receitas, vendedores] = await Promise.all([
    pool.query('SELECT nome FROM CLIENTE ORDER BY nome'),
    pool.query('SELECT descricao, tipo, preco_venda, qtd_estoque, qtd_minima FROM PRODUTO ORDER BY id_produto'),
    pool.query(`
      SELECT v.id_venda, v.data_venda, v.valor_total, c.nome AS cliente, ve.nome AS vendedor,
             (SELECT COUNT(*) FROM ITEM_VENDA iv WHERE iv.id_venda = v.id_venda)::int AS qtd_itens
        FROM VENDA v JOIN CLIENTE c ON c.id_cliente = v.id_cliente JOIN VENDEDOR ve ON ve.id_vendedor = v.id_vendedor
       ORDER BY v.id_venda`),
    pool.query(`
      SELECT r.id_receita, c.nome AS cliente, m.nome AS medico, r.validade, r.od_esferico, r.oe_esferico
        FROM RECEITA r JOIN CLIENTE c ON c.id_cliente = r.id_cliente JOIN MEDICO m ON m.crm = r.crm_medico
       ORDER BY r.id_receita`),
    pool.query('SELECT nome FROM VENDEDOR ORDER BY nome'),
  ]);

  return `Você é o assistente de análise do sistema Ótica Mais, uma ótica em Itacoatiara-AM.
Responda sempre em português, de forma concisa, clara e útil para os gestores da loja.
Aqui está o estado atual do banco de dados:

CLIENTES (${clientes.rows.length}): ${clientes.rows.map((c) => c.nome).join(', ')}

PRODUTOS: ${produtos.rows.map((p) => `${p.descricao} | Tipo:${p.tipo} | Preço:R$${Number(p.preco_venda).toFixed(2)} | Estoque:${p.qtd_estoque} | Mínimo:${p.qtd_minima}`).join('\n')}

VENDAS (${vendas.rows.length}): ${vendas.rows.map((v) => `Venda#${v.id_venda} em ${v.data_venda.toISOString().split('T')[0]} | Cliente:${v.cliente} | Vendedor:${v.vendedor} | Total:R$${Number(v.valor_total).toFixed(2)} | Itens:${v.qtd_itens}`).join('\n')}

RECEITAS (${receitas.rows.length}): ${receitas.rows.map((r) => `Receita#${r.id_receita} | Cliente:${r.cliente} | Médico:${r.medico} | Válida até:${r.validade.toISOString().split('T')[0]} | OD:${r.od_esferico} OE:${r.oe_esferico}`).join('\n')}

VENDEDORES: ${vendedores.rows.map((v) => v.nome).join(', ')}`;
}

// POST /api/assistente/chat
// Body: { mensagens: [{ role: "user"|"assistant", content: "..." }] }
router.post('/chat', async (req, res) => {
  const { mensagens } = req.body;

  if (!Array.isArray(mensagens) || !mensagens.length) {
    return res.status(400).json({ erro: 'Envie ao menos uma mensagem.' });
  }
  if (!process.env.ANTHROPIC_API_KEY) {
    return res.status(500).json({ erro: 'ANTHROPIC_API_KEY não configurada no servidor.' });
  }

  try {
    const system = await montarContexto();

    const resposta = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': process.env.ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-6',
        max_tokens: 1000,
        system,
        messages: mensagens.slice(-10),
      }),
    });

    if (!resposta.ok) {
      const texto = await resposta.text();
      console.error('Erro da API Anthropic:', resposta.status, texto);
      return res.status(502).json({ erro: 'Erro ao consultar o assistente de IA.' });
    }

    const data = await resposta.json();
    const texto = data.content?.find((c) => c.type === 'text')?.text || 'Não foi possível obter resposta.';
    res.json({ resposta: texto });
  } catch (err) {
    console.error(err);
    res.status(500).json({ erro: 'Erro ao conectar com o assistente.' });
  }
});

module.exports = router;
