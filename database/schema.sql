-- ============================================================
-- PROJETO: ÓTICA MAIS -- Sistema de Gestão de Ótica
-- SGBD: PostgreSQL
-- ============================================================

-- TABELA: CLIENTE
CREATE TABLE CLIENTE (
    id_cliente  INTEGER GENERATED ALWAYS AS IDENTITY,
    nome        VARCHAR(100) NOT NULL,
    cpf         CHAR(11)      NOT NULL,
    telefone    VARCHAR(15),
    email       VARCHAR(100),
    endereco    VARCHAR(200),
    CONSTRAINT pk_cliente  PRIMARY KEY (id_cliente),
    CONSTRAINT uq_cli_cpf  UNIQUE (cpf),
    CONSTRAINT ck_cli_cpf  CHECK (cpf ~ '^[0-9]{11}$')
);

-- TABELA: MEDICO
CREATE TABLE MEDICO (
    crm           VARCHAR(15)  NOT NULL,
    nome          VARCHAR(100) NOT NULL,
    especialidade VARCHAR(80) NOT NULL,
    telefone      VARCHAR(15),
    CONSTRAINT pk_medico PRIMARY KEY (crm)
);

-- TABELA: RECEITA
CREATE TABLE RECEITA (
    id_receita    INTEGER GENERATED ALWAYS AS IDENTITY,
    data_emissao  DATE          NOT NULL,
    validade      DATE          NOT NULL,
    od_esferico   NUMERIC(4,2)  NOT NULL,
    od_cilindrico NUMERIC(4,2),
    od_eixo       INTEGER,
    oe_esferico   NUMERIC(4,2)  NOT NULL,
    oe_cilindrico NUMERIC(4,2),
    oe_eixo       INTEGER,
    id_cliente    INTEGER        NOT NULL,
    crm_medico    VARCHAR(15)  NOT NULL,
    CONSTRAINT pk_receita    PRIMARY KEY (id_receita),
    CONSTRAINT fk_rec_cli    FOREIGN KEY (id_cliente) REFERENCES CLIENTE (id_cliente),
    CONSTRAINT fk_rec_med    FOREIGN KEY (crm_medico) REFERENCES MEDICO (crm),
    CONSTRAINT ck_rec_eixo_od CHECK (od_eixo BETWEEN 0 AND 180),
    CONSTRAINT ck_rec_eixo_oe CHECK (oe_eixo BETWEEN 0 AND 180),
    CONSTRAINT ck_rec_valid   CHECK (validade > data_emissao)
);

-- TABELA: PRODUTO (superclasse)
CREATE TABLE PRODUTO (
    id_produto   INTEGER GENERATED ALWAYS AS IDENTITY,
    tipo         CHAR(7)       NOT NULL,
    descricao    VARCHAR(200),
    preco_venda  NUMERIC(10,2) NOT NULL,
    qtd_estoque  INTEGER        DEFAULT 0 NOT NULL,
    qtd_minima   INTEGER        DEFAULT 5 NOT NULL,
    CONSTRAINT pk_produto      PRIMARY KEY (id_produto),
    CONSTRAINT ck_prod_tipo    CHECK (tipo IN ('ARMACAO','LENTE')),
    CONSTRAINT ck_prod_preco   CHECK (preco_venda >= 0),
    CONSTRAINT ck_prod_estq    CHECK (qtd_estoque >= 0)
);

-- TABELA: ARMACAO (especialização de PRODUTO)
CREATE TABLE ARMACAO (
    id_produto  INTEGER        NOT NULL,
    marca       VARCHAR(80)  NOT NULL,
    modelo      VARCHAR(80),
    cor         VARCHAR(40),
    material    VARCHAR(60),
    CONSTRAINT pk_armacao   PRIMARY KEY (id_produto),
    CONSTRAINT fk_arm_prod  FOREIGN KEY (id_produto) REFERENCES PRODUTO (id_produto) ON DELETE CASCADE
);

-- TABELA: LENTE (especialização de PRODUTO)
CREATE TABLE LENTE (
    id_produto  INTEGER        NOT NULL,
    material    VARCHAR(60)  NOT NULL,
    tipo_foco   VARCHAR(40)  NOT NULL,
    indice      NUMERIC(4,2),
    CONSTRAINT pk_lente     PRIMARY KEY (id_produto),
    CONSTRAINT fk_len_prod  FOREIGN KEY (id_produto) REFERENCES PRODUTO (id_produto) ON DELETE CASCADE,
    CONSTRAINT ck_len_foco  CHECK (tipo_foco IN ('MONOFOCAL','BIFOCAL','PROGRESSIVA','OCUPACIONAL'))
);

-- TABELA: VENDEDOR
CREATE TABLE VENDEDOR (
    id_vendedor  INTEGER GENERATED ALWAYS AS IDENTITY,
    nome         VARCHAR(100) NOT NULL,
    cpf          CHAR(11)      NOT NULL,
    telefone     VARCHAR(15),
    email        VARCHAR(100),
    CONSTRAINT pk_vendedor   PRIMARY KEY (id_vendedor),
    CONSTRAINT uq_vend_cpf   UNIQUE (cpf),
    CONSTRAINT ck_vend_cpf   CHECK (cpf ~ '^[0-9]{11}$')
);

-- TABELA: VENDA
CREATE TABLE VENDA (
    id_venda     INTEGER GENERATED ALWAYS AS IDENTITY,
    data_venda   DATE          DEFAULT CURRENT_DATE NOT NULL,
    valor_total  NUMERIC(10,2) DEFAULT 0       NOT NULL,
    id_cliente   INTEGER        NOT NULL,
    id_vendedor  INTEGER        NOT NULL,
    id_receita   INTEGER,
    CONSTRAINT pk_venda      PRIMARY KEY (id_venda),
    CONSTRAINT fk_ven_cli    FOREIGN KEY (id_cliente) REFERENCES CLIENTE (id_cliente),
    CONSTRAINT fk_ven_vend   FOREIGN KEY (id_vendedor) REFERENCES VENDEDOR (id_vendedor),
    CONSTRAINT fk_ven_rec    FOREIGN KEY (id_receita) REFERENCES RECEITA (id_receita),
    CONSTRAINT ck_ven_total  CHECK (valor_total >= 0)
);

-- TABELA: ITEM_VENDA
CREATE TABLE ITEM_VENDA (
    id_venda       INTEGER        NOT NULL,
    id_produto     INTEGER        NOT NULL,
    quantidade     INTEGER        NOT NULL,
    valor_unitario NUMERIC(10,2)  NOT NULL,
    CONSTRAINT pk_item       PRIMARY KEY (id_venda, id_produto),
    CONSTRAINT fk_item_ven   FOREIGN KEY (id_venda) REFERENCES VENDA (id_venda) ON DELETE CASCADE,
    CONSTRAINT fk_item_prod  FOREIGN KEY (id_produto) REFERENCES PRODUTO (id_produto),
    CONSTRAINT ck_item_qtd   CHECK (quantidade > 0),
    CONSTRAINT ck_item_val   CHECK (valor_unitario >= 0)
);

-- ÍNDICES ADICIONAIS
CREATE INDEX idx_receita_cliente ON RECEITA    (id_cliente);
CREATE INDEX idx_venda_cliente   ON VENDA      (id_cliente);
CREATE INDEX idx_venda_data      ON VENDA      (data_venda);
CREATE INDEX idx_item_produto    ON ITEM_VENDA (id_produto);

-- FUNÇÃO PL/pgSQL QUE SERÁ EXECUTADA PELA TRIGGER
CREATE OR REPLACE FUNCTION fn_atualizar_venda_e_estoque()
RETURNS TRIGGER AS $$
BEGIN
    -- Atualiza o valor total da venda acumulada
    UPDATE VENDA
       SET valor_total = valor_total + (NEW.quantidade * NEW.valor_unitario)
     WHERE id_venda = NEW.id_venda;

    -- Realiza a baixa do estoque físico do produto vendido
    UPDATE PRODUTO
       SET qtd_estoque = qtd_estoque - NEW.quantidade
     WHERE id_produto = NEW.id_produto;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- DECLARAÇÃO DA TRIGGER ASSOCIAÇÃO DO EVENTO
CREATE TRIGGER trg_item_venda_after
AFTER INSERT ON ITEM_VENDA
FOR EACH ROW
EXECUTE FUNCTION fn_atualizar_venda_e_estoque();