-- ============================================================
-- PROJETO: ÓTICA MAIS -- Sistema de Gestão de Ótica
-- SGBD: PostgreSQL
-- Versão corrigida (v2) — base para a API Node.js/Express
-- ============================================================

-- Permite rodar o script de novo sem erro (apaga tudo na ordem certa)
DROP TABLE IF EXISTS ITEM_VENDA CASCADE;
DROP TABLE IF EXISTS VENDA CASCADE;
DROP TABLE IF EXISTS LENTE CASCADE;
DROP TABLE IF EXISTS ARMACAO CASCADE;
DROP TABLE IF EXISTS PRODUTO CASCADE;
DROP TABLE IF EXISTS RECEITA CASCADE;
DROP TABLE IF EXISTS VENDEDOR CASCADE;
DROP TABLE IF EXISTS MEDICO CASCADE;
DROP TABLE IF EXISTS CLIENTE CASCADE;
DROP TABLE IF EXISTS USUARIO CASCADE;

-- ============================================================
-- TABELA: USUARIO (login do sistema — não existia antes)
-- ============================================================
-- Cada vendedor que acessa o sistema precisa de um login.
-- id_vendedor é opcional: existem casos de usuário admin que não vende.
CREATE TABLE USUARIO (
    id_usuario   INTEGER GENERATED ALWAYS AS IDENTITY,
    login        VARCHAR(50)  NOT NULL,
    senha_hash   VARCHAR(255) NOT NULL,
    papel        VARCHAR(20)  NOT NULL DEFAULT 'VENDEDOR',
    id_vendedor  INTEGER,
    CONSTRAINT pk_usuario    PRIMARY KEY (id_usuario),
    CONSTRAINT uq_usu_login  UNIQUE (login),
    CONSTRAINT ck_usu_papel  CHECK (papel IN ('ADMIN','VENDEDOR'))
);

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
    CONSTRAINT fk_rec_med    FOREIGN KEY (crm_medico) REFERENCES MEDICO (crm) ON UPDATE CASCADE,
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

-- agora que VENDEDOR existe, liga o FK pendente de USUARIO
ALTER TABLE USUARIO
    ADD CONSTRAINT fk_usu_vend FOREIGN KEY (id_vendedor) REFERENCES VENDEDOR (id_vendedor);

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
CREATE INDEX idx_cliente_nome    ON CLIENTE    (nome);

-- ============================================================
-- TRIGGER 1: garante que toda linha de PRODUTO tem a subclasse
-- correta criada (ARMACAO ou LENTE) e nenhuma das duas erradas.
-- Isso é checado DEFERRED, no fim da transação, porque a aplicação
-- faz: INSERT em PRODUTO, depois INSERT em ARMACAO/LENTE.
-- ============================================================
CREATE OR REPLACE FUNCTION fn_checar_subclasse_produto()
RETURNS TRIGGER AS $$
DECLARE
    v_tipo   CHAR(7);
    v_em_arm BOOLEAN;
    v_em_len BOOLEAN;
BEGIN
    SELECT tipo INTO v_tipo FROM PRODUTO WHERE id_produto = NEW.id_produto;

    v_em_arm := EXISTS (SELECT 1 FROM ARMACAO WHERE id_produto = NEW.id_produto);
    v_em_len := EXISTS (SELECT 1 FROM LENTE   WHERE id_produto = NEW.id_produto);

    IF v_tipo = 'ARMACAO' AND NOT v_em_arm THEN
        RAISE EXCEPTION 'Produto % marcado como ARMACAO mas sem linha em ARMACAO.', NEW.id_produto;
    END IF;
    IF v_tipo = 'LENTE' AND NOT v_em_len THEN
        RAISE EXCEPTION 'Produto % marcado como LENTE mas sem linha em LENTE.', NEW.id_produto;
    END IF;
    IF v_em_arm AND v_em_len THEN
        RAISE EXCEPTION 'Produto % não pode estar em ARMACAO e LENTE ao mesmo tempo.', NEW.id_produto;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Dispara ao final da transação (depois do INSERT em PRODUTO e em ARMACAO/LENTE)
CREATE CONSTRAINT TRIGGER trg_checar_subclasse_armacao
AFTER INSERT ON ARMACAO
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION fn_checar_subclasse_produto();

CREATE CONSTRAINT TRIGGER trg_checar_subclasse_lente
AFTER INSERT ON LENTE
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION fn_checar_subclasse_produto();

-- ============================================================
-- TRIGGER 2 (única): valida e baixa/devolve estoque, e em
-- seguida recalcula VENDA.valor_total a partir da soma real dos
-- itens (recalcular, em vez de acumular, evita duplicação em
-- updates ou reexecuções). Tudo numa função só, para não depender
-- da ordem de execução entre triggers diferentes na mesma tabela.
-- ============================================================
CREATE OR REPLACE FUNCTION fn_estoque_e_total_venda()
RETURNS TRIGGER AS $$
DECLARE
    v_estoque_atual INTEGER;
    v_id_venda      INTEGER;
BEGIN
    -- 1) Estoque
    IF TG_OP = 'INSERT' THEN
        SELECT qtd_estoque INTO v_estoque_atual FROM PRODUTO WHERE id_produto = NEW.id_produto FOR UPDATE;

        IF v_estoque_atual IS NULL THEN
            RAISE EXCEPTION 'Produto % não encontrado.', NEW.id_produto;
        END IF;
        IF v_estoque_atual < NEW.quantidade THEN
            RAISE EXCEPTION 'Estoque insuficiente para o produto % (disponível: %, solicitado: %).',
                NEW.id_produto, v_estoque_atual, NEW.quantidade;
        END IF;

        UPDATE PRODUTO SET qtd_estoque = qtd_estoque - NEW.quantidade WHERE id_produto = NEW.id_produto;

    ELSIF TG_OP = 'DELETE' THEN
        UPDATE PRODUTO SET qtd_estoque = qtd_estoque + OLD.quantidade WHERE id_produto = OLD.id_produto;

    ELSIF TG_OP = 'UPDATE' THEN
        SELECT qtd_estoque INTO v_estoque_atual FROM PRODUTO WHERE id_produto = NEW.id_produto FOR UPDATE;
        IF v_estoque_atual + OLD.quantidade < NEW.quantidade THEN
            RAISE EXCEPTION 'Estoque insuficiente para alterar o item do produto % para quantidade %.',
                NEW.id_produto, NEW.quantidade;
        END IF;
        UPDATE PRODUTO
           SET qtd_estoque = qtd_estoque + OLD.quantidade - NEW.quantidade
         WHERE id_produto = NEW.id_produto;
    END IF;

    -- 2) Recalcula o total da venda com base nos itens atuais
    v_id_venda := COALESCE(NEW.id_venda, OLD.id_venda);
    UPDATE VENDA
       SET valor_total = (
            SELECT COALESCE(SUM(quantidade * valor_unitario), 0)
              FROM ITEM_VENDA
             WHERE id_venda = v_id_venda
           )
     WHERE id_venda = v_id_venda;

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_estoque_e_total_venda
AFTER INSERT OR UPDATE OR DELETE ON ITEM_VENDA
FOR EACH ROW
EXECUTE FUNCTION fn_estoque_e_total_venda();

-- ============================================================
-- FIM DO SCHEMA
-- ============================================================
