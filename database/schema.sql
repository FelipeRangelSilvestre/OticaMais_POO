-- ============================================================
-- PROJETO: ÓTICA MAIS -- Sistema de Gestão de Ótica
-- SGBD: PostgreSQL
-- ARQUITETURA: Heranças Físicas e Entidade Serviço / Pessoa
-- ============================================================

-- ============================================================
-- 1. SUPERCLASSE: PESSOA
-- ============================================================
CREATE TABLE PESSOA (
    id_pessoa   INTEGER GENERATED ALWAYS AS IDENTITY,
    nome        VARCHAR(100) NOT NULL,
    cpf         CHAR(11)     NOT NULL,
    telefone    VARCHAR(15),
    email       VARCHAR(100),
    CONSTRAINT pk_pessoa PRIMARY KEY (id_pessoa),
    CONSTRAINT uq_pessoa_cpf UNIQUE (cpf),
    CONSTRAINT ck_pessoa_cpf CHECK (cpf ~ '^[0-9]{11}$')
);

-- ============================================================
-- 2. SUBCLASSES DE PESSOA (CLIENTE, MEDICO, VENDEDOR)
-- ============================================================
CREATE TABLE CLIENTE (
    id_cliente  INTEGER GENERATED ALWAYS AS IDENTITY,
    id_pessoa   INTEGER      NOT NULL,
    endereco    VARCHAR(200),
    CONSTRAINT pk_cliente PRIMARY KEY (id_cliente),
    CONSTRAINT uq_cli_pessoa UNIQUE (id_pessoa), -- Garante a relação 1:1 com PESSOA
    CONSTRAINT fk_cli_pessoa FOREIGN KEY (id_pessoa) REFERENCES PESSOA (id_pessoa) ON DELETE CASCADE
);

CREATE TABLE MEDICO (
    id_medico     INTEGER GENERATED ALWAYS AS IDENTITY,
    id_pessoa     INTEGER      NOT NULL,
    crm           VARCHAR(15)  NOT NULL,
    especialidade VARCHAR(80)  NOT NULL,
    CONSTRAINT pk_medico PRIMARY KEY (id_medico),
    CONSTRAINT uq_med_pessoa UNIQUE (id_pessoa), -- 1:1
    CONSTRAINT uq_med_crm UNIQUE (crm),
    CONSTRAINT fk_med_pessoa FOREIGN KEY (id_pessoa) REFERENCES PESSOA (id_pessoa) ON DELETE CASCADE
);

CREATE TABLE VENDEDOR (
    id_vendedor INTEGER GENERATED ALWAYS AS IDENTITY,
    id_pessoa   INTEGER NOT NULL,
    CONSTRAINT pk_vendedor PRIMARY KEY (id_vendedor),
    CONSTRAINT uq_ven_pessoa UNIQUE (id_pessoa), -- 1:1
    CONSTRAINT fk_ven_pessoa FOREIGN KEY (id_pessoa) REFERENCES PESSOA (id_pessoa) ON DELETE CASCADE
);

-- ============================================================
-- 3. DEPENDENTE (COMPOSIÇÃO COM CLIENTE)
-- ============================================================
CREATE TABLE DEPENDENTE (
    id_dependente   INTEGER GENERATED ALWAYS AS IDENTITY,
    id_cliente      INTEGER      NOT NULL,
    nome            VARCHAR(100) NOT NULL,
    parentesco      VARCHAR(50),
    data_nascimento DATE,
    CONSTRAINT pk_dependente PRIMARY KEY (id_dependente),
    CONSTRAINT fk_dep_cliente FOREIGN KEY (id_cliente) REFERENCES CLIENTE (id_cliente) ON DELETE CASCADE
);

-- ============================================================
-- 4. SUPERCLASSE: SERVIÇO
-- ============================================================
CREATE TABLE SERVICO (
    id_servico   INTEGER GENERATED ALWAYS AS IDENTITY,
    id_cliente   INTEGER NOT NULL,
    data_servico DATE    DEFAULT CURRENT_DATE NOT NULL,
    tipo_servico VARCHAR(20) NOT NULL,
    CONSTRAINT pk_servico PRIMARY KEY (id_servico),
    CONSTRAINT fk_srv_cliente FOREIGN KEY (id_cliente) REFERENCES CLIENTE (id_cliente),
    CONSTRAINT ck_srv_tipo CHECK (tipo_servico IN ('RECEITA', 'VENDA'))
);

-- ============================================================
-- 5. SUBCLASSES DE SERVIÇO (RECEITA E VENDA)
-- ============================================================
CREATE TABLE RECEITA (
    id_receita    INTEGER GENERATED ALWAYS AS IDENTITY,
    id_servico    INTEGER NOT NULL,
    id_medico     INTEGER NOT NULL,
    data_emissao  DATE    NOT NULL,
    validade      DATE    NOT NULL,
    od_esferico   NUMERIC(4,2) NOT NULL,
    od_cilindrico NUMERIC(4,2),
    od_eixo       INTEGER,
    oe_esferico   NUMERIC(4,2) NOT NULL,
    oe_cilindrico NUMERIC(4,2),
    oe_eixo       INTEGER,
    CONSTRAINT pk_receita PRIMARY KEY (id_receita),
    CONSTRAINT uq_rec_servico UNIQUE (id_servico), -- Relação 1:1 com SERVICO
    CONSTRAINT fk_rec_servico FOREIGN KEY (id_servico) REFERENCES SERVICO (id_servico) ON DELETE CASCADE,
    CONSTRAINT fk_rec_medico FOREIGN KEY (id_medico) REFERENCES MEDICO (id_medico),
    CONSTRAINT ck_rec_eixo_od CHECK (od_eixo BETWEEN 0 AND 180),
    CONSTRAINT ck_rec_eixo_oe CHECK (oe_eixo BETWEEN 0 AND 180),
    CONSTRAINT ck_rec_valid CHECK (validade > data_emissao)
);

CREATE TABLE VENDA (
    id_venda    INTEGER GENERATED ALWAYS AS IDENTITY,
    id_servico  INTEGER NOT NULL,
    id_vendedor INTEGER NOT NULL,
    id_receita  INTEGER,
    valor_total NUMERIC(10,2) DEFAULT 0 NOT NULL,
    CONSTRAINT pk_venda PRIMARY KEY (id_venda),
    CONSTRAINT uq_ven_servico UNIQUE (id_servico), -- Relação 1:1 com SERVICO
    CONSTRAINT fk_ven_servico FOREIGN KEY (id_servico) REFERENCES SERVICO (id_servico) ON DELETE CASCADE,
    CONSTRAINT fk_ven_vendedor FOREIGN KEY (id_vendedor) REFERENCES VENDEDOR (id_vendedor),
    CONSTRAINT fk_ven_receita FOREIGN KEY (id_receita) REFERENCES RECEITA (id_receita),
    CONSTRAINT ck_ven_total CHECK (valor_total >= 0)
);

-- ============================================================
-- 6. PRODUTOS (SUPER E SUBCLASSES)
-- ============================================================
CREATE TABLE PRODUTO (
    id_produto   INTEGER GENERATED ALWAYS AS IDENTITY,
    tipo         CHAR(7)       NOT NULL,
    descricao    VARCHAR(200),
    preco_venda  NUMERIC(10,2) NOT NULL,
    qtd_estoque  INTEGER       DEFAULT 0 NOT NULL,
    qtd_minima   INTEGER       DEFAULT 5 NOT NULL,
    CONSTRAINT pk_produto PRIMARY KEY (id_produto),
    CONSTRAINT ck_prod_tipo CHECK (tipo IN ('ARMACAO','LENTE')),
    CONSTRAINT ck_prod_preco CHECK (preco_venda >= 0),
    CONSTRAINT ck_prod_estq CHECK (qtd_estoque >= 0)
);

CREATE TABLE ARMACAO (
    id_produto INTEGER NOT NULL,
    marca      VARCHAR(80) NOT NULL,
    modelo     VARCHAR(80),
    cor        VARCHAR(40),
    material   VARCHAR(60),
    CONSTRAINT pk_armacao PRIMARY KEY (id_produto),
    CONSTRAINT fk_arm_prod FOREIGN KEY (id_produto) REFERENCES PRODUTO (id_produto) ON DELETE CASCADE
);

CREATE TABLE LENTE (
    id_produto INTEGER NOT NULL,
    material   VARCHAR(60) NOT NULL,
    tipo_foco  VARCHAR(40) NOT NULL,
    indice     NUMERIC(4,2),
    CONSTRAINT pk_lente PRIMARY KEY (id_produto),
    CONSTRAINT fk_len_prod FOREIGN KEY (id_produto) REFERENCES PRODUTO (id_produto) ON DELETE CASCADE,
    CONSTRAINT ck_len_foco CHECK (tipo_foco IN ('MONOFOCAL','BIFOCAL','PROGRESSIVA','OCUPACIONAL'))
);

-- ============================================================
-- 7. ITENS DA VENDA
-- ============================================================
CREATE TABLE ITEM_VENDA (
    id_venda       INTEGER NOT NULL,
    id_produto     INTEGER NOT NULL,
    quantidade     INTEGER NOT NULL,
    valor_unitario NUMERIC(10,2) NOT NULL,
    CONSTRAINT pk_item PRIMARY KEY (id_venda, id_produto),
    CONSTRAINT fk_item_ven FOREIGN KEY (id_venda) REFERENCES VENDA (id_venda) ON DELETE CASCADE,
    CONSTRAINT fk_item_prod FOREIGN KEY (id_produto) REFERENCES PRODUTO (id_produto),
    CONSTRAINT ck_item_qtd CHECK (quantidade > 0),
    CONSTRAINT ck_item_val CHECK (valor_unitario >= 0)
);

-- ============================================================
-- 8. FUNÇÕES E TRIGGERS
-- ============================================================
CREATE INDEX idx_servico_cliente ON SERVICO (id_cliente);
CREATE INDEX idx_item_produto ON ITEM_VENDA (id_produto);

CREATE OR REPLACE FUNCTION fn_atualizar_venda_e_estoque()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE VENDA
       SET valor_total = valor_total + (NEW.quantidade * NEW.valor_unitario)
     WHERE id_venda = NEW.id_venda;

    UPDATE PRODUTO
       SET qtd_estoque = qtd_estoque - NEW.quantidade
     WHERE id_produto = NEW.id_produto;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_item_venda_after
AFTER INSERT ON ITEM_VENDA
FOR EACH ROW
EXECUTE FUNCTION fn_atualizar_venda_e_estoque();