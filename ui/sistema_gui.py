import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime

# Importação dos modelos e serviços existentes
from models.venda import Venda
from models.item_venda import ItemVenda
from services.cliente_service import ClienteService, CpfDuplicadoError
from services.produto_service import ProdutoService
from services.venda_service import VendaService

class OticaMaisGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Inicialização das Camadas de Serviço da Arquitetura
        self.cliente_service = ClienteService()
        self.produto_service = ProdutoService()
        self.venda_service = VendaService()
        
        # Carrinho de compras temporário para a estrutura de Vendas
        self.carrinho_atual = []
        
        # Configurações da Janela Principal (GUI)
        self.title("Ótica Mais — Sistema de Gestão")
        self.geometry("1200x750")
        self.configure(bg="#f5f5f5")
        
        # Estilização Moderna utilizando os componentes nativos TTK
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Painel Central de Abas (Notebook)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_clientes = ttk.Frame(self.notebook)
        self.tab_produtos = ttk.Frame(self.notebook)
        self.tab_receitas = ttk.Frame(self.notebook)  # Nova Aba Arquitetural
        self.tab_vendas = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_clientes, text="Gerenciar Clientes")
        self.notebook.add(self.tab_produtos, text="Gerenciar Produtos")
        self.notebook.add(self.tab_receitas, text="Consultas & Receitas")
        self.notebook.add(self.tab_vendas, text="Gerenciar Vendas")
        
        # Renderização dos componentes visuais
        self._configurar_aba_clientes()
        self._configurar_aba_produtos()
        self._configurar_aba_receitas()
        self._configurar_aba_vendas()

    # =========================================================================
    # COMPONENTE: GERENCIAMENTO DE CLIENTES
    # =========================================================================
    def _configurar_aba_clientes(self):
        form_frame = ttk.LabelFrame(self.tab_clientes, text=" Cadastro de Cliente ", padding=10)
        form_frame.pack(side="left", fill="y", padx=10, pady=10)
        
        ttk.Label(form_frame, text="Nome:").pack(anchor="w", pady=2)
        self.ent_cli_nome = ttk.Entry(form_frame, width=30)
        self.ent_cli_nome.pack(fill="x", pady=2)
        
        ttk.Label(form_frame, text="CPF (Apenas números):").pack(anchor="w", pady=2)
        self.ent_cli_cpf = ttk.Entry(form_frame, width=30)
        self.ent_cli_cpf.pack(fill="x", pady=2)
        
        ttk.Label(form_frame, text="Telefone:").pack(anchor="w", pady=2)
        self.ent_cli_tel = ttk.Entry(form_frame, width=30)
        self.ent_cli_tel.pack(fill="x", pady=2)
        
        ttk.Label(form_frame, text="Email:").pack(anchor="w", pady=2)
        self.ent_cli_email = ttk.Entry(form_frame, width=30)
        self.ent_cli_email.pack(fill="x", pady=2)
        
        ttk.Label(form_frame, text="Endereço:").pack(anchor="w", pady=2)
        self.ent_cli_end = ttk.Entry(form_frame, width=30)
        self.ent_cli_end.pack(fill="x", pady=2)
        
        ttk.Button(form_frame, text="Cadastrar Cliente", command=self._cadastrar_cliente_gui).pack(fill="x", pady=15)
        
        view_frame = ttk.LabelFrame(self.tab_clientes, text=" Clientes Cadastrados ", padding=10)
        view_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        self.tree_clientes = ttk.Treeview(view_frame, columns=("ID", "Nome", "CPF", "Telefone"), show="headings")
        self.tree_clientes.heading("ID", text="ID")
        self.tree_clientes.heading("Nome", text="Nome")
        self.tree_clientes.heading("CPF", text="CPF")
        self.tree_clientes.heading("Telefone", text="Telefone")
        self.tree_clientes.column("ID", width=50, anchor="center")
        self.tree_clientes.column("Nome", width=200)
        self.tree_clientes.column("CPF", width=110, anchor="center")
        self.tree_clientes.column("Telefone", width=110, anchor="center")
        self.tree_clientes.pack(fill="both", expand=True, pady=5)
        
        btn_bar = ttk.Frame(view_frame)
        btn_bar.pack(fill="x", pady=5)
        ttk.Button(btn_bar, text="Atualizar Lista", command=self._atualizar_tabela_clientes).pack(side="left", padx=5)
        ttk.Button(btn_bar, text="Remover Selecionado", command=self._excluir_cliente_gui).pack(side="right", padx=5)
        self._atualizar_tabela_clientes()

    def _cadastrar_cliente_gui(self):
        try:
            cliente = self.cliente_service.cadastrar(
                self.ent_cli_nome.get(), self.ent_cli_cpf.get(),
                self.ent_cli_tel.get(), self.ent_cli_email.get(), self.ent_cli_end.get()
            )
            messagebox.showinfo("Sucesso", f"Cliente {cliente.nome} cadastrado com sucesso!")
            for entry in (self.ent_cli_nome, self.ent_cli_cpf, self.ent_cli_tel, self.ent_cli_email, self.ent_cli_end):
                entry.delete(0, tk.END)
            self._atualizar_tabela_clientes()
        except (CpfDuplicadoError, ValueError) as erro:
            messagebox.showerror("Erro de Validação", str(erro))

    def _atualizar_tabela_clientes(self):
        for row in self.tree_clientes.get_children():
            self.tree_clientes.delete(row)
        for c in self.cliente_service.listar():
            self.tree_clientes.insert("", tk.END, values=(c.id_cliente, c.nome, c.cpf, c.telefone))

    def _excluir_cliente_gui(self):
        sel = self.tree_clientes.selection()
        if not sel: return
        valores = self.tree_clientes.item(sel, "values")
        if messagebox.askyesno("Confirmar", f"Excluir o cliente '{valores[1]}'?"):
            self.cliente_service.excluir(int(valores[0]))
            self._atualizar_tabela_clientes()

    # =========================================================================
    # COMPONENTE: CATALOGO DE PRODUTOS
    # =========================================================================
    def _configurar_aba_produtos(self):
        form_frame = ttk.LabelFrame(self.tab_produtos, text=" Cadastro de Produto (Herança Física) ", padding=10)
        form_frame.pack(side="left", fill="y", padx=10, pady=10)
        
        ttk.Label(form_frame, text="Tipo de Produto:").pack(anchor="w")
        self.cb_prod_tipo = ttk.Combobox(form_frame, values=["ARMACAO", "LENTE"], state="readonly")
        self.cb_prod_tipo.pack(fill="x", pady=2)
        self.cb_prod_tipo.set("ARMACAO")
        self.cb_prod_tipo.bind("<<ComboboxSelected>>", lambda e: self._alternar_campos_produto())
        
        ttk.Label(form_frame, text="Descrição Genérica:").pack(anchor="w")
        self.ent_prod_desc = ttk.Entry(form_frame, width=30)
        self.ent_prod_desc.pack(fill="x", pady=2)
        
        ttk.Label(form_frame, text="Preço de Venda (R$):").pack(anchor="w")
        self.ent_prod_preco = ttk.Entry(form_frame, width=30)
        self.ent_prod_preco.pack(fill="x", pady=2)
        
        ...
        ttk.Label(form_frame, text="Quantidade em Estoque:").pack(anchor="w")
        self.ent_prod_estq = ttk.Entry(form_frame, width=30)
        self.ent_prod_estq.pack(fill="x", pady=2)
        
        self.frame_especifico = ttk.Frame(form_frame)
        self.frame_especifico.pack(fill="x", pady=5)
        self._alternar_campos_produto()
        
        ttk.Button(form_frame, text="Salvar no Catálogo", command=self._cadastrar_produto_gui).pack(fill="x", pady=15)
        
        view_frame = ttk.LabelFrame(self.tab_produtos, text=" Estoque Atual ", padding=10)
        view_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        self.tree_produtos = ttk.Treeview(view_frame, columns=("ID", "Tipo", "Descrição", "Preço", "Estoque", "Status"), show="headings")
        self.tree_produtos.heading("ID", text="ID")
        self.tree_produtos.heading("Tipo", text="Tipo")
        self.tree_produtos.heading("Descrição", text="Descrição")
        self.tree_produtos.heading("Preço", text="Preço")
        self.tree_produtos.heading("Estoque", text="Qtd")
        self.tree_produtos.heading("Status", text="Status")
        
        self.tree_produtos.column("ID", width=40, anchor="center")
        self.tree_produtos.column("Tipo", width=80, anchor="center")
        self.tree_produtos.column("Descrição", width=220)
        self.tree_produtos.column("Preço", width=90, anchor="e")
        self.tree_produtos.column("Estoque", width=60, anchor="center")
        self.tree_produtos.column("Status", width=80, anchor="center")
        self.tree_produtos.pack(fill="both", expand=True, pady=5)
        
        ttk.Button(view_frame, text="Atualizar Catálogo", command=self._atualizar_tabela_produtos).pack(anchor="w")
        self._atualizar_tabela_produtos()

    def _alternar_campos_produto(self):
        for widget in self.frame_especifico.winfo_children():
            widget.destroy()
        tipo = self.cb_prod_tipo.get()
        if tipo == "ARMACAO":
            ttk.Label(self.frame_especifico, text="Marca da Armação:").pack(anchor="w")
            self.ent_arm_marca = ttk.Entry(self.frame_especifico)
            self.ent_arm_marca.pack(fill="x", pady=2)
            ttk.Label(self.frame_especifico, text="Modelo/Referência:").pack(anchor="w")
            self.ent_arm_modelo = ttk.Entry(self.frame_especifico)
            self.ent_arm_modelo.pack(fill="x", pady=2)
        else:
            ttk.Label(self.frame_especifico, text="Material da Lente:").pack(anchor="w")
            self.ent_len_mat = ttk.Entry(self.frame_especifico)
            self.ent_len_mat.pack(fill="x", pady=2)
            ttk.Label(self.frame_especifico, text="Tipo de Foco:").pack(anchor="w")
            self.cb_len_foco = ttk.Combobox(self.frame_especifico, values=["MONOFOCAL", "BIFOCAL", "PROGRESSIVA", "OCUPACIONAL"], state="readonly")
            self.cb_len_foco.pack(fill="x", pady=2)
            self.cb_len_foco.set("MONOFOCAL")

    def _cadastrar_produto_gui(self):
        try:
            tipo = self.cb_prod_tipo.get()
            desc = self.ent_prod_desc.get()
            preco = float(self.ent_prod_preco.get())
            estq = int(self.ent_prod_estq.get())
            if tipo == "ARMACAO":
                self.produto_service.cadastrar_armacao(desc, preco, estq, self.ent_arm_marca.get(), self.ent_arm_modelo.get())
            else:
                self.produto_service.cadastrar_lente(desc, preco, estq, self.ent_len_mat.get(), self.cb_len_foco.get())
            messagebox.showinfo("Sucesso", "Produto inserido e catalogado no SGBD!")
            self.ent_prod_desc.delete(0, tk.END)
            self.ent_prod_preco.delete(0, tk.END)
            self.ent_prod_estq.delete(0, tk.END)
            self._atualizar_tabela_produtos()
        except ValueError as e:
            messagebox.showerror("Erro", f"Verifique os campos numéricos. Detalhes: {e}")

    def _atualizar_tabela_produtos(self):
        for row in self.tree_produtos.get_children():
            self.tree_produtos.delete(row)
        for p in self.produto_service.listar():
            alerta = "⚠️ BAIXO" if p.estoque_critico else "✅ OK"
            self.tree_produtos.insert("", tk.END, values=(p.id_produto, p.tipo, p.descricao, f"R$ {p.preco_venda:.2f}", p.qtd_estoque, alerta))

    # =========================================================================
    # NOVA ABA: CONSULTAS & EMISSÃO DE RECEITAS (MÓDULO CLÍNICO)
    # =========================================================================
    def _configurar_aba_receitas(self):
        form_frame = ttk.LabelFrame(self.tab_receitas, text=" Sistema de Atendimento Médico ", padding=10)
        form_frame.pack(side="left", fill="y", padx=10, pady=10)
        
        ttk.Label(form_frame, text="ID Cliente Paciente:").pack(anchor="w")
        self.ent_rec_cliente = ttk.Entry(form_frame)
        self.ent_rec_cliente.pack(fill="x", pady=2)
        
        ttk.Label(form_frame, text="ID Médico Optometrista:").pack(anchor="w")
        self.ent_rec_medico = ttk.Entry(form_frame)
        self.ent_rec_medico.pack(fill="x", pady=2)
        
        ttk.Label(form_frame, text="Validade da Receita (Dias):").pack(anchor="w")
        self.ent_rec_val = ttk.Entry(form_frame)
        self.ent_rec_val.pack(fill="x", pady=2)
        self.ent_rec_val.insert(0, "365")
        
        # Grid interno para Graus do Olho Direito (OD) e Esquerdo (OE)
        grau_frame = ttk.LabelFrame(form_frame, text=" Medição Refrativa (Graus) ", padding=5)
        grau_frame.pack(fill="x", pady=8)
        
        ttk.Label(grau_frame, text="OD Esférico:").grid(row=0, column=0, sticky="w")
        self.ent_od_esf = ttk.Entry(grau_frame, width=8)
        self.ent_od_esf.grid(row=0, column=1, pady=2, padx=2)
        self.ent_od_esf.insert(0, "0.00")
        
        ttk.Label(grau_frame, text="OE Esférico:").grid(row=0, column=2, sticky="w")
        self.ent_oe_esf = ttk.Entry(grau_frame, width=8)
        self.ent_oe_esf.grid(row=0, column=3, pady=2, padx=2)
        self.ent_oe_esf.insert(0, "0.00")
        
        ttk.Label(grau_frame, text="OD Cilíndrico:").grid(row=1, column=0, sticky="w")
        self.ent_od_cil = ttk.Entry(grau_frame, width=8)
        self.ent_od_cil.grid(row=1, column=1, pady=2, padx=2)
        self.ent_od_cil.insert(0, "0.00")
        
        ttk.Label(grau_frame, text="OE Cilíndrico:").grid(row=1, column=2, sticky="w")
        self.ent_oe_cil = ttk.Entry(grau_frame, width=8)
        self.grid_rowconfigure(0, weight=1)
        self.ent_oe_cil.grid(row=1, column=3, pady=2, padx=2)
        self.ent_oe_cil.insert(0, "0.00")
        
        ttk.Label(grau_frame, text="OD Eixo (º):").grid(row=2, column=0, sticky="w")
        self.ent_od_eixo = ttk.Entry(grau_frame, width=8)
        self.ent_od_eixo.grid(row=2, column=1, pady=2, padx=2)
        self.ent_od_eixo.insert(0, "0")
        
        ttk.Label(grau_frame, text="OE Eixo (º):").grid(row=2, column=2, sticky="w")
        self.ent_oe_eixo = ttk.Entry(grau_frame, width=8)
        self.ent_oe_eixo.grid(row=2, column=3, pady=2, padx=2)
        self.ent_oe_eixo.insert(0, "0")
        
        ttk.Button(form_frame, text="Emitir Receita Clínica", command=self._emitir_receita_gui).pack(fill="x", pady=10)
        
        # Visualizador de Receitas Ativas (Direita)
        view_frame = ttk.LabelFrame(self.tab_receitas, text=" Histórico de Receitas Emitidas no Sistema ", padding=10)
        view_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        self.tree_receitas = ttk.Treeview(view_frame, columns=("ID Rec", "ID Cli", "ID Med", "OD", "OE", "Status"), show="headings")
        self.tree_receitas.heading("ID Rec", text="ID Rec")
        self.tree_receitas.heading("ID Cli", text="ID Paciente")
        self.tree_receitas.heading("ID Med", text="ID Médico")
        self.tree_receitas.heading("OD", text="Grau OD")
        self.tree_receitas.heading("OE", text="Grau OE")
        self.tree_receitas.heading("Status", text="Validade")
        
        self.tree_receitas.column("ID Rec", width=60, anchor="center")
        self.tree_receitas.column("ID Cli", width=80, anchor="center")
        self.tree_receitas.column("ID Med", width=80, anchor="center")
        self.tree_receitas.column("OD", width=120, anchor="center")
        self.tree_receitas.column("OE", width=120, anchor="center")
        self.tree_receitas.column("Status", width=90, anchor="center")
        self.tree_receitas.pack(fill="both", expand=True, pady=5)
        
        ttk.Button(view_frame, text="Sincronizar Receitas", command=self._atualizar_tabela_receitas).pack(anchor="w")
        self._atualizar_tabela_receitas()

    def _emitir_receita_gui(self):
        # Mapeamento do Insert Duplo (SERVICO + RECEITA) direto na base através de conexão transacional
        try:
            id_cli = int(self.ent_rec_cliente.get())
            id_med = int(self.ent_rec_medico.get())
            validade_dias = int(self.ent_rec_val.get())
            
            conexao = self.venda_service._VendaService__venda_repo._VendaRepository__db.obter_conexao()
            with conexao.cursor() as cursor:
                # 1. Cria a instância base na superclasse SERVICO
                cursor.execute("""
                    INSERT INTO SERVICO (id_cliente, data_servico, tipo_servico)
                    VALUES (%s, CURRENT_DATE, 'RECEITA') RETURNING id_servico
                """, (id_cli,))
                id_servico = cursor.fetchone()[0]
                
                # 2. Popula a subclasse RECEITA vinculando a chave primária de Serviço
                cursor.execute("""
                    INSERT INTO RECEITA (id_servico, id_medico, data_emissao, validade, 
                                         od_esferico, od_cilindrico, od_eixo, oe_esferico, oe_cilindrico, oe_eixo)
                    VALUES (%s, %s, CURRENT_DATE, CURRENT_DATE + %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id_receita
                """, (id_servico, id_med, validade_dias,
                      float(self.ent_od_esf.get()), float(self.ent_od_cil.get()), int(self.ent_od_eixo.get()),
                      float(self.ent_oe_esf.get()), float(self.ent_oe_cil.get()), int(self.ent_oe_eixo.get())))
                id_receita = cursor.fetchone()[0]
                conexao.commit()
                
            messagebox.showinfo("Sucesso", f"Atendimento concluído! Receita Clínica gerada sob o ID: {id_receita}")
            self.ent_rec_cliente.delete(0, tk.END)
            self._atualizar_tabela_receitas()
        except Exception as e:
            messagebox.showerror("Erro de Integridade", f"Não foi possível salvar a consulta médica. Verifique os IDs. Detalhes: {e}")

    def _atualizar_tabela_receitas(self):
        for row in self.tree_receitas.get_children():
            self.tree_receitas.delete(row)
        try:
            conexao = self.venda_service._VendaService__venda_repo._VendaRepository__db.obter_conexao()
            with conexao.cursor() as cursor:
                cursor.execute("""
                    SELECT r.id_receita, s.id_cliente, r.id_medico, r.od_esferico, r.od_cilindrico, r.oe_esferico, r.oe_cilindrico, r.validade
                      FROM RECEITA r JOIN SERVICO s ON r.id_servico = s.id_servico ORDER BY r.id_receita DESC
                """)
                for reg in cursor.fetchall():
                    od_str = f"E:{reg[3]} C:{reg[4]}"
                    oe_str = f"E:{reg[5]} C:{reg[6]}"
                    status = "✅ Ativa" if reg[7] >= date.today() else "❌ Expirada"
                    self.tree_receitas.insert("", tk.END, values=(reg[0], reg[1], reg[2], od_str, oe_str, status))
        except Exception:
            pass

    # =========================================================================
    # COMPONENTE: PONTO DE VENDA (CAIXA PDV)
    # =========================================================================
    def _configurar_aba_vendas(self):
        form_frame = ttk.LabelFrame(self.tab_vendas, text=" Ponto de Venda (Terminal PDV) ", padding=10)
        form_frame.pack(side="left", fill="y", padx=10, pady=10)
        
        ttk.Label(form_frame, text="ID Cliente Titular:").pack(anchor="w")
        self.ent_ven_cliente = ttk.Entry(form_frame, width=30)
        self.ent_ven_cliente.pack(fill="x", pady=2)
        
        ttk.Label(form_frame, text="ID Vendedor Responsável:").pack(anchor="w")
        self.ent_ven_vendedor = ttk.Entry(form_frame, width=30)
        self.ent_ven_vendedor.pack(fill="x", pady=2)
        
        ttk.Label(form_frame, text="ID Receita Vinculada (Deixe em branco se não houver):").pack(anchor="w")
        self.ent_ven_receita = ttk.Entry(form_frame, width=30)
        self.ent_ven_receita.pack(fill="x", pady=2)
        
        item_frame = ttk.LabelFrame(form_frame, text=" Inserir Item ao Carrinho ", padding=5)
        item_frame.pack(fill="x", pady=10)
        
        ttk.Label(item_frame, text="ID Produto:").pack(anchor="w")
        self.ent_item_prod = ttk.Entry(item_frame)
        self.ent_item_prod.pack(fill="x", pady=2)
        
        ttk.Label(item_frame, text="Quantidade:").pack(anchor="w")
        self.ent_item_qtd = ttk.Entry(item_frame)
        self.ent_item_qtd.pack(fill="x", pady=2)
        
        ttk.Button(item_frame, text="Adicionar Item", command=self._adicionar_item_carrinho).pack(fill="x", pady=5)
        
        ttk.Label(form_frame, text="Itens no Carrinho Virtual:").pack(anchor="w", pady=2)
        self.txt_carrinho = tk.Text(form_frame, height=6, width=28, state="disabled", bg="#fdfdfd")
        self.txt_carrinho.pack(fill="x", pady=2)
        
        ttk.Button(form_frame, text="Concluir e Fechar Venda", command=self._concluir_venda_gui).pack(fill="x", pady=10)
        
        view_frame = ttk.LabelFrame(self.tab_vendas, text=" Histórico de Transações Relacionais ", padding=10)
        view_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        self.tree_vendas = ttk.Treeview(view_frame, columns=("ID Venda", "Data", "ID Cliente", "Total"), show="headings")
        self.tree_vendas.heading("ID Venda", text="ID Venda")
        self.tree_vendas.heading("Data", text="Data da Operação")
        self.tree_vendas.heading("ID Cliente", text="ID Cliente")
        self.tree_vendas.heading("Total", text="Valor Total Nota")
        
        self.tree_vendas.column("ID Venda", width=80, anchor="center")
        self.tree_vendas.column("Data", width=130, anchor="center")
        self.tree_vendas.column("ID Cliente", width=110, anchor="center")
        self.tree_vendas.column("Total", width=130, anchor="e")
        self.tree_vendas.pack(fill="both", expand=True, pady=5)
        
        ttk.Button(view_frame, text="Atualizar Histórico", command=self._atualizar_tabela_vendas).pack(anchor="w")
        self._atualizar_tabela_vendas()

    def _adicionar_item_carrinho(self):
        try:
            id_prod = int(self.ent_item_prod.get())
            qtd = int(self.ent_item_qtd.get())
            prod_obj = self.produto_service.buscar_por_id(id_prod)
            if not prod_obj:
                messagebox.showerror("Erro", "Produto não encontrado no banco relacional!")
                return
            item = ItemVenda(id_produto=id_prod, quantidade=qtd, valor_unitario=prod_obj.preco_venda, descricao_produto=prod_obj.descricao)
            self.carrinho_atual.append(item)
            
            self.txt_carrinho.configure(state="normal")
            self.txt_carrinho.insert(tk.END, f"ID {id_prod} | Qtd: {qtd} | R$ {prod_obj.preco_venda * qtd:.2f}\n")
            self.txt_carrinho.configure(state="disabled")
            self.ent_item_prod.delete(0, tk.END)
            self.ent_item_qtd.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Erro", "Insira valores numéricos inteiros!")

    def _concluir_venda_gui(self):
        if not self.carrinho_atual:
            messagebox.showwarning("Aviso", "O carrinho está vazio!")
            return
        try:
            id_cli = int(self.ent_ven_cliente.get())
            id_ven = int(self.ent_ven_vendedor.get())
            rec_raw = self.ent_ven_receita.get().strip()
            id_rec = int(rec_raw) if rec_raw else None
            
            nova_venda = Venda(id_cliente=id_cli, id_vendedor=id_ven, id_receita=id_rec)
            for item in self.carrinho_atual:
                nova_venda.adicionar_item(item)
                
            self.venda_service.finalizar_venda(nova_venda)
            messagebox.showinfo("Sucesso", "Venda finalizada! Baixa de estoque e totalização efetuadas.")
            
            self.carrinho_atual = []
            self.txt_carrinho.configure(state="normal")
            self.txt_carrinho.delete("1.0", tk.END)
            self.txt_carrinho.configure(state="disabled")
            self.ent_ven_cliente.delete(0, tk.END)
            self.ent_ven_vendedor.delete(0, tk.END)
            self.ent_ven_receita.delete(0, tk.END)
            self._atualizar_tabela_vendas()
            self._atualizar_tabela_produtos()
        except ValueError:
            messagebox.showerror("Erro", "Verifique as chaves e IDs numéricos digitados.")
        except Exception as e:
            messagebox.showerror("Erro de Regra de Negócio", str(e))

    def _atualizar_tabela_vendas(self):
        for row in self.tree_vendas.get_children():
            self.tree_vendas.delete(row)
        for v in self.venda_service.listar():
            self.tree_vendas.insert("", tk.END, values=(v.id_venda, v.data_venda, v.id_cliente, f"R$ {v.valor_total:.2f}"))