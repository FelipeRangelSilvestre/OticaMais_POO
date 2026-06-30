-- ============================================================
-- SEED: dados iniciais (espelha o DB mockado do front-end)
-- Rodar depois do schema.sql
-- ============================================================

BEGIN;

-- USUÁRIO ADMIN padrão. Login: admin / Senha: admin123 -- TROQUE em produção!
INSERT INTO USUARIO (login, senha_hash, papel) VALUES
  ('admin', '$2a$10$I2BWvmDebjWToklHV/6cz.2Ulr9Z94OiuU0JPaAcVxAEKD3uM/382', 'ADMIN');

-- CLIENTES
INSERT INTO CLIENTE (nome, cpf, telefone, email, endereco) VALUES
  ('Ana Beatriz Lima',        '12345678901', '(92) 98765-4321', 'ana@email.com',      'Rua das Flores, 12, Centro'),
  ('Carlos Eduardo Mendes',   '23456789012', '(92) 99123-4567', 'carlos@email.com',   'Av. Amazonas, 450, Bairro Novo'),
  ('Fernanda Oliveira',       '34567890123', '(92) 97654-3210', 'fernanda@email.com', 'Rua Paraíba, 88, São Jorge'),
  ('João Pedro Alves',        '45678901234', '(92) 98001-2345', 'joao@email.com',     'Trav. Vitória, 33, Mamoud'),
  ('Mariana Costa Rocha',     '56789012345', '(92) 96543-9876', 'mariana@email.com',  'Rua do Sol, 204, Centro');

-- MÉDICOS
INSERT INTO MEDICO (crm, nome, especialidade, telefone) VALUES
  ('AM-12345', 'Dr. Roberto Faria',        'Oftalmologia',          '(92) 3232-1001'),
  ('AM-67890', 'Dra. Claudia Vasconcelos', 'Oftalmologia',          '(92) 3233-2002'),
  ('AM-11223', 'Dr. Marcos Pinheiro',      'Oftalmologia clínica',  '(92) 3234-3003');

-- VENDEDORES
INSERT INTO VENDEDOR (nome, cpf, telefone, email) VALUES
  ('Felipe Rangel', '98765432100', '(92) 99876-5432', 'felipe@oticamais.com'),
  ('Iasmim Braga',  '87654321099', '(92) 98765-4321', 'iasmim@oticamais.com');

-- USUÁRIOS vinculados aos vendedores. Senha de ambos: vendedor123 -- TROQUE em produção!
INSERT INTO USUARIO (login, senha_hash, papel, id_vendedor) VALUES
  ('felipe', '$2a$10$gJ9vCwUhaysYubmSMFs4mOeKXojdyg.9hs6dhKNmUdfUwhD00/cq6', 'VENDEDOR', 1),
  ('iasmim', '$2a$10$gJ9vCwUhaysYubmSMFs4mOeKXojdyg.9hs6dhKNmUdfUwhD00/cq6', 'VENDEDOR', 2);

-- PRODUTOS (superclasse) -- a ordem de id_produto segue a ordem de inserção (1..7)
INSERT INTO PRODUTO (tipo, descricao, preco_venda, qtd_estoque, qtd_minima) VALUES
  ('ARMACAO', 'Armação acetato Ray-Ban RB5228',        349.90, 12, 5),  -- id 1
  ('LENTE',   'Lente monofocal policarbonato 1.67',    280.00, 3,  8),  -- id 2
  ('ARMACAO', 'Armação metal Oakley OX3179',            520.00, 7,  5),  -- id 3
  ('LENTE',   'Lente progressiva CR39 1.56',            650.00, 2,  6),  -- id 4
  ('ARMACAO', 'Armação acetato Chilli Beans CB001',     189.90, 15, 5),  -- id 5
  ('LENTE',   'Lente bifocal vidro temperado 1.50',     320.00, 4,  5),  -- id 6
  ('LENTE',   'Lente ocupacional policarbonato 1.60',   410.00, 9,  5);  -- id 7

-- ARMACAO (detalhes das armações: ids 1, 3, 5)
INSERT INTO ARMACAO (id_produto, marca, modelo, cor, material) VALUES
  (1, 'Ray-Ban',      'RB5228', 'Preto', 'Acetato'),
  (3, 'Oakley',       'OX3179', 'Prata', 'Metal'),
  (5, 'Chilli Beans', 'CB001',  'Azul',  'Acetato');

-- LENTE (detalhes das lentes: ids 2, 4, 6, 7)
INSERT INTO LENTE (id_produto, material, tipo_foco, indice) VALUES
  (2, 'Policarbonato',     'MONOFOCAL',   1.67),
  (4, 'CR39',               'PROGRESSIVA', 1.56),
  (6, 'Vidro temperado',    'BIFOCAL',     1.50),
  (7, 'Policarbonato',      'OCUPACIONAL', 1.60);

-- RECEITAS
INSERT INTO RECEITA (data_emissao, validade, od_esferico, od_cilindrico, od_eixo, oe_esferico, oe_cilindrico, oe_eixo, id_cliente, crm_medico) VALUES
  ('2026-01-10', '2027-01-10', -2.25, -0.50, 90,  -2.00,  0.00,   0, 1, 'AM-12345'),
  ('2025-11-05', '2026-11-05', -1.50,  0.00,  0,  -1.75, -0.25, 180, 2, 'AM-67890'),
  ('2026-03-22', '2027-03-22', -3.00, -0.75, 45,  -3.25, -0.50, 135, 3, 'AM-12345'),
  ('2025-06-15', '2026-06-15',  1.00,  0.00,  0,   1.25,  0.00,   0, 4, 'AM-11223'),
  ('2026-04-01', '2027-04-01', -0.75, -0.25, 60,  -1.00,  0.00,   0, 5, 'AM-67890');

-- VENDAS (valor_total começa em 0 — as triggers recalculam ao inserir os itens)
INSERT INTO VENDA (data_venda, id_cliente, id_vendedor, id_receita) VALUES
  ('2026-06-01', 1, 1, 1),  -- id_venda 1
  ('2026-06-05', 2, 2, 2),  -- id_venda 2
  ('2026-06-10', 3, 1, NULL), -- id_venda 3
  ('2026-06-12', 5, 2, 5),  -- id_venda 4
  ('2026-06-15', 4, 1, NULL); -- id_venda 5

-- ITENS DE VENDA
-- Atenção: a trigger valida estoque no momento do INSERT, então a
-- ordem/quantidade abaixo respeita o estoque definido acima.
INSERT INTO ITEM_VENDA (id_venda, id_produto, quantidade, valor_unitario) VALUES
  (1, 3, 1, 520.00),
  (1, 2, 2, 280.00),
  (2, 1, 1, 349.90),
  (2, 4, 1, 650.00),
  (3, 5, 1, 189.90),
  (4, 7, 2, 410.00),
  (4, 5, 1, 189.90),
  (5, 6, 1, 320.00);

COMMIT;

-- Confirma que os totais foram calculados pela trigger
SELECT id_venda, valor_total FROM VENDA ORDER BY id_venda;

-- Confirma que o estoque foi descontado corretamente
SELECT id_produto, descricao, qtd_estoque FROM PRODUTO ORDER BY id_produto;
