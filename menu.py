"""Interface gráfica (GUI) completa do sistema MRP II - Pedal Forte Bicicletas."""

import tkinter as tk
from tkinter import messagebox, ttk

from capacidade import (
    cadastrar_centro,
    cadastrar_roteiro,
    calcular_crp_centro,
    listar_centros,
    listar_roteiros,
)
from custos import calcular_custo_padrao
from estoque import consultar_kardex, listar_saldos, registrar_movimentacao
from estrutura import (
    cadastrar_componente,
    formatar_arvore_bom,
    remover_componente,
)
from graficos import (
    grafico_carga_capacidade,
    grafico_estoque_projetado,
    grafico_ordens_por_semana,
    grafico_posicao_estoque,
)
from itens import alterar_item, cadastrar_item, listar_itens
from mps import atualizar_semana_pa, obter_mps_completo
from mrp import ULTIMO_RESULTADO_MRP, executar_mrp, obter_registro_mrp_item
from ordens import alterar_status_ordem, apontar_producao, listar_ordens
from relatorios import exportar_ordens_csv, exportar_posicao_estoque_csv
from utils import (
    data_hoje_str,
    formatar_moeda,
    validar_float_positivo,
    validar_int_positivo,
)


class AplicacaoMRP2(tk.Tk):
    """Janela principal da aplicação MRP II em Tkinter/ttk."""

    def __init__(self) -> None:
        super().__init__()
        self.title("MRP II - Pedal Forte Bicicletas Ltda. | GPTech Sistemas")
        self.geometry("1220x760")
        self.minsize(1050, 680)
        self.configure(bg="#f1f5f9")

        self._configurar_estilos()
        self._construir_cabecalho()
        self._construir_abas()
        self.atualizar_todas_telas()

    def _configurar_estilos(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")

        azul_escuro = "#1e293b"
        azul_destaque = "#2563eb"
        fundo_claro = "#f1f5f9"

        style.configure("TFrame", background=fundo_claro)
        style.configure("Card.TFrame", background="#ffffff", relief="flat")
        style.configure("TLabel", background=fundo_claro, foreground="#0f172a", font=("Sans", 10))
        style.configure("Card.TLabel", background="#ffffff", foreground="#0f172a", font=("Sans", 10))
        style.configure("Titulo.TLabel", background="#ffffff", foreground=azul_escuro, font=("Sans", 11, "bold"))

        style.configure(
            "Acao.TButton",
            background=azul_destaque,
            foreground="#ffffff",
            font=("Sans", 10, "bold"),
            padding=(12, 6),
        )
        style.map("Acao.TButton", background=[("active", "#1d4ed8")])

        style.configure(
            "Secundario.TButton",
            background="#475569",
            foreground="#ffffff",
            font=("Sans", 9, "bold"),
            padding=(10, 5),
        )
        style.map("Secundario.TButton", background=[("active", "#334155")])

        style.configure("TNotebook", background=fundo_claro, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(14, 8), font=("Sans", 10, "bold"))
        style.map(
            "TNotebook.Tab",
            background=[("selected", "#ffffff"), ("!selected", "#cbd5e1")],
            foreground=[("selected", azul_destaque), ("!selected", "#334155")],
        )

        style.configure("Treeview", rowheight=26, font=("Sans", 9), background="#ffffff", fieldbackground="#ffffff")
        style.configure("Treeview.Heading", font=("Sans", 9, "bold"), background="#e2e8f0", foreground="#0f172a")

    def _construir_cabecalho(self) -> None:
        header = tk.Frame(self, bg="#0f172a", height=58)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="  PEDAL FORTE BICICLETAS  |  Sistema MRP II",
            bg="#0f172a",
            fg="#ffffff",
            font=("Sans", 14, "bold"),
        ).pack(side="left", padx=15)

        tk.Label(
            header,
            text="GPTech Sistemas • Divinópolis-MG  ",
            bg="#0f172a",
            fg="#94a3b8",
            font=("Sans", 10),
        ).pack(side="right", padx=15)

    def _construir_abas(self) -> None:
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=12)

        self.aba_cadastros = ttk.Frame(self.notebook)
        self.aba_estoque = ttk.Frame(self.notebook)
        self.aba_mps = ttk.Frame(self.notebook)
        self.aba_mrp = ttk.Frame(self.notebook)
        self.aba_ordens = ttk.Frame(self.notebook)
        self.aba_crp_custos = ttk.Frame(self.notebook)
        self.aba_relatorios = ttk.Frame(self.notebook)

        self.notebook.add(self.aba_cadastros, text=" 1. Cadastros & BOM ")
        self.notebook.add(self.aba_estoque, text=" 2. Estoque & Kardex ")
        self.notebook.add(self.aba_mps, text=" 3. MPS (8 Semanas) ")
        self.notebook.add(self.aba_mrp, text=" 4. Cálculo MRP ")
        self.notebook.add(self.aba_ordens, text=" 5. Ordens (OP / OC) ")
        self.notebook.add(self.aba_crp_custos, text=" 6. Capacidade & Custos ")
        self.notebook.add(self.aba_relatorios, text=" 7. Relatórios & Gráficos ")

        self._montar_aba_cadastros()
        self._montar_aba_estoque()
        self._montar_aba_mps()
        self._montar_aba_mrp()
        self._montar_aba_ordens()
        self._montar_aba_crp_custos()
        self._montar_aba_relatorios()

    def atualizar_todas_telas(self) -> None:
        """Atualiza tabelas e combos em todas as abas após alterações nos dados."""
        self._carregar_tabela_itens()
        self._atualizar_combos_itens()
        self._carregar_tabela_estoque()
        self._carregar_tabela_mps()
        self._carregar_tabela_ordens()
        self._carregar_centros_e_roteiros()

    def _montar_aba_cadastros(self) -> None:
        sub_nb = ttk.Notebook(self.aba_cadastros)
        sub_nb.pack(fill="both", expand=True, padx=6, pady=6)

        tab_itens = ttk.Frame(sub_nb)
        tab_bom = ttk.Frame(sub_nb)
        tab_ct = ttk.Frame(sub_nb)

        sub_nb.add(tab_itens, text="Itens (PA / SA / MP)")
        sub_nb.add(tab_bom, text="Estrutura de Produto (BOM)")
        sub_nb.add(tab_ct, text="Centros de Trabalho & Roteiros")

        form_item = ttk.Frame(tab_itens, style="Card.TFrame", padding=10)
        form_item.pack(fill="x", padx=6, pady=6)

        ttk.Label(form_item, text="Cadastrar / Alterar Item:", style="Titulo.TLabel").grid(
            row=0, column=0, columnspan=8, sticky="w", pady=(0, 8)
        )

        campos = [
            ("Código (ex: MP-400):", "ent_item_cod", 12),
            ("Descrição:", "ent_item_desc", 28),
            ("Unid:", "ent_item_un", 6),
            ("Custo Un (R$):", "ent_item_custo", 10),
            ("Lead Time (sem):", "ent_item_lt", 8),
            ("Est. Seg:", "ent_item_es", 8),
            ("Lote Mín:", "ent_item_lote", 8),
        ]
        self.entradas_item: dict[str, ttk.Entry] = {}
        for idx, (rotulo, chave, largura) in enumerate(campos):
            ttk.Label(form_item, text=rotulo, style="Card.TLabel").grid(row=1, column=idx, sticky="w", padx=4)
            ent = ttk.Entry(form_item, width=largura)
            ent.grid(row=2, column=idx, padx=4, pady=2)
            self.entradas_item[chave] = ent

        btns_item = ttk.Frame(form_item, style="Card.TFrame")
        btns_item.grid(row=2, column=len(campos), padx=8)
        ttk.Button(btns_item, text="Cadastrar", style="Acao.TButton", command=self._acao_cadastrar_item).pack(
            side="left", padx=3
        )
        ttk.Button(btns_item, text="Salvar Alteração", style="Secundario.TButton", command=self._acao_alterar_item).pack(
            side="left", padx=3
        )

        cols = ("codigo", "tipo", "descricao", "unidade", "custo", "lt", "es", "lote")
        self.tree_itens = ttk.Treeview(tab_itens, columns=cols, show="headings", height=16)
        cabecalhos = [
            ("codigo", "Código", 90),
            ("tipo", "Tipo", 60),
            ("descricao", "Descrição", 280),
            ("unidade", "Unid.", 60),
            ("custo", "Custo Unit.", 110),
            ("lt", "Lead Time", 90),
            ("es", "Est. Segurança", 110),
            ("lote", "Lote Mínimo", 110),
        ]
        for col_id, texto, larg in cabecalhos:
            self.tree_itens.heading(col_id, text=texto)
            self.tree_itens.column(col_id, width=larg, anchor="center" if col_id != "descricao" else "w")
        self.tree_itens.pack(fill="both", expand=True, padx=6, pady=6)
        self.tree_itens.bind("<<TreeviewSelect>>", self._ao_selecionar_item_tabela)

        topo_bom = ttk.Frame(tab_bom, style="Card.TFrame", padding=10)
        topo_bom.pack(fill="x", padx=6, pady=6)

        ttk.Label(topo_bom, text="Item Pai (PA ou SA):", style="Card.TLabel").pack(side="left", padx=5)
        self.cb_bom_pai = ttk.Combobox(topo_bom, width=18, state="readonly")
        self.cb_bom_pai.pack(side="left", padx=5)
        self.cb_bom_pai.bind("<<ComboboxSelected>>", lambda _: self._exibir_arvore_bom())

        ttk.Label(topo_bom, text="Componente:", style="Card.TLabel").pack(side="left", padx=(15, 5))
        self.cb_bom_comp = ttk.Combobox(topo_bom, width=18, state="readonly")
        self.cb_bom_comp.pack(side="left", padx=5)

        ttk.Label(topo_bom, text="Qtde por un:", style="Card.TLabel").pack(side="left", padx=(10, 5))
        self.ent_bom_qtd = ttk.Entry(topo_bom, width=10)
        self.ent_bom_qtd.pack(side="left", padx=5)

        ttk.Button(topo_bom, text="Adicionar/Atualizar", style="Acao.TButton", command=self._acao_add_bom).pack(
            side="left", padx=6
        )
        ttk.Button(topo_bom, text="Remover Comp.", style="Secundario.TButton", command=self._acao_rem_bom).pack(
            side="left", padx=4
        )

        self.txt_bom = tk.Text(tab_bom, font=("Courier New", 11), bg="#ffffff", fg="#0f172a", padx=15, pady=15)
        self.txt_bom.pack(fill="both", expand=True, padx=6, pady=6)

        # --- Sub-aba Centros & Roteiros ---
        frame_ct = ttk.Frame(tab_ct, style="Card.TFrame", padding=10)
        frame_ct.pack(fill="x", padx=6, pady=6)
        ttk.Label(frame_ct, text="Centro de Trabalho (ex: CT-04):", style="Card.TLabel").grid(row=0, column=0, padx=4)
        self.ent_ct_cod = ttk.Entry(frame_ct, width=10)
        self.ent_ct_cod.grid(row=1, column=0, padx=4)

        ttk.Label(frame_ct, text="Nome do Centro:", style="Card.TLabel").grid(row=0, column=1, padx=4)
        self.ent_ct_nome = ttk.Entry(frame_ct, width=28)
        self.ent_ct_nome.grid(row=1, column=1, padx=4)

        ttk.Label(frame_ct, text="Capacidade (h/sem):", style="Card.TLabel").grid(row=0, column=2, padx=4)
        self.ent_ct_cap = ttk.Entry(frame_ct, width=12)
        self.ent_ct_cap.grid(row=1, column=2, padx=4)

        ttk.Label(frame_ct, text="Custo-Hora (R$):", style="Card.TLabel").grid(row=0, column=3, padx=4)
        self.ent_ct_custo = ttk.Entry(frame_ct, width=12)
        self.ent_ct_custo.grid(row=1, column=3, padx=4)

        ttk.Button(frame_ct, text="Salvar Centro", style="Acao.TButton", command=self._acao_salvar_ct).grid(
            row=1, column=4, padx=8
        )

        # Roteiro
        frame_rot = ttk.Frame(tab_ct, style="Card.TFrame", padding=10)
        frame_rot.pack(fill="x", padx=6, pady=4)
        ttk.Label(frame_rot, text="Vincular Roteiro -> Item Fabricado:", style="Card.TLabel").pack(side="left", padx=4)
        self.cb_rot_item = ttk.Combobox(frame_rot, width=14, state="readonly")
        self.cb_rot_item.pack(side="left", padx=4)

        ttk.Label(frame_rot, text="Centro:", style="Card.TLabel").pack(side="left", padx=4)
        self.cb_rot_ct = ttk.Combobox(frame_rot, width=12, state="readonly")
        self.cb_rot_ct.pack(side="left", padx=4)

        ttk.Label(frame_rot, text="Tempo Unitário (h):", style="Card.TLabel").pack(side="left", padx=4)
        self.ent_rot_tempo = ttk.Entry(frame_rot, width=10)
        self.ent_rot_tempo.pack(side="left", padx=4)

        ttk.Button(frame_rot, text="Salvar Roteiro", style="Secundario.TButton", command=self._acao_salvar_rot).pack(
            side="left", padx=8
        )

        self.txt_ct_rot = tk.Text(tab_ct, font=("Courier New", 10), bg="#ffffff", fg="#0f172a", padx=12, pady=12)
        self.txt_ct_rot.pack(fill="both", expand=True, padx=6, pady=6)

    def _carregar_tabela_itens(self) -> None:
        for row in self.tree_itens.get_children():
            self.tree_itens.delete(row)
        for item in listar_itens():
            self.tree_itens.insert(
                "",
                "end",
                values=(
                    item["codigo"],
                    item["tipo"],
                    item["descricao"],
                    item["unidade"],
                    formatar_moeda(item["custo_unitario"]),
                    f"{item['lead_time']} sem",
                    f"{item['estoque_seguranca']:g}",
                    f"{item['lote_minimo']:g}",
                ),
            )

    def _ao_selecionar_item_tabela(self, _event: object) -> None:
        sel = self.tree_itens.selection()
        if not sel:
            return
        vals = self.tree_itens.item(sel[0], "values")
        custo_limpo = vals[4].replace("R$", "").replace(".", "").replace(",", ".").strip()
        lt_limpo = vals[5].replace("sem", "").strip()

        dados = [vals[0], vals[2], vals[3], custo_limpo, lt_limpo, vals[6], vals[7]]
        chaves = ["ent_item_cod", "ent_item_desc", "ent_item_un", "ent_item_custo", "ent_item_lt", "ent_item_es", "ent_item_lote"]
        for chave, valor in zip(chaves, dados):
            self.entradas_item[chave].delete(0, tk.END)
            self.entradas_item[chave].insert(0, valor)

    def _acao_cadastrar_item(self) -> None:
        try:
            cadastrar_item(
                codigo=self.entradas_item["ent_item_cod"].get(),
                descricao=self.entradas_item["ent_item_desc"].get(),
                unidade=self.entradas_item["ent_item_un"].get(),
                custo_unitario=validar_float_positivo(self.entradas_item["ent_item_custo"].get(), True),
                lead_time=validar_int_positivo(self.entradas_item["ent_item_lt"].get(), True),
                estoque_seguranca=validar_float_positivo(self.entradas_item["ent_item_es"].get(), True),
                lote_minimo=validar_float_positivo(self.entradas_item["ent_item_lote"].get(), False),
            )
            messagebox.showinfo("Sucesso", "Item cadastrado com sucesso!")
            self.atualizar_todas_telas()
        except ValueError as err:
            messagebox.showerror("Erro de Validação", str(err))

    def _acao_alterar_item(self) -> None:
        try:
            alterar_item(
                codigo=self.entradas_item["ent_item_cod"].get(),
                descricao=self.entradas_item["ent_item_desc"].get(),
                unidade=self.entradas_item["ent_item_un"].get(),
                custo_unitario=validar_float_positivo(self.entradas_item["ent_item_custo"].get(), True),
                lead_time=validar_int_positivo(self.entradas_item["ent_item_lt"].get(), True),
                estoque_seguranca=validar_float_positivo(self.entradas_item["ent_item_es"].get(), True),
                lote_minimo=validar_float_positivo(self.entradas_item["ent_item_lote"].get(), False),
            )
            messagebox.showinfo("Sucesso", "Item atualizado com sucesso!")
            self.atualizar_todas_telas()
        except ValueError as err:
            messagebox.showerror("Erro de Validação", str(err))

    def _atualizar_combos_itens(self) -> None:
        todos = listar_itens()
        cods_todos = [i["codigo"] for i in todos]
        cods_fabricados = [i["codigo"] for i in todos if i["tipo"] in ("PA", "SA")]
        cods_pa = [i["codigo"] for i in todos if i["tipo"] == "PA"]

        self.cb_bom_pai["values"] = cods_fabricados
        self.cb_bom_comp["values"] = cods_todos
        self.cb_rot_item["values"] = cods_fabricados
        self.cb_mov_item["values"] = cods_todos
        self.cb_mps_pa["values"] = cods_pa
        self.cb_mrp_item["values"] = cods_todos
        self.cb_custo_item["values"] = cods_fabricados

        if cods_fabricados and not self.cb_bom_pai.get():
            self.cb_bom_pai.set(cods_fabricados[0])
            self._exibir_arvore_bom()
        if cods_pa and not self.cb_mps_pa.get():
            self.cb_mps_pa.set(cods_pa[0])
        if cods_todos and not self.cb_mrp_item.get():
            self.cb_mrp_item.set("SA-020" if "SA-020" in cods_todos else cods_todos[0])
        if cods_fabricados and not self.cb_custo_item.get():
            self.cb_custo_item.set(cods_fabricados[0])

    def _exibir_arvore_bom(self) -> None:
        pai = self.cb_bom_pai.get()
        if not pai:
            return
        self.txt_bom.delete("1.0", tk.END)
        try:
            arvore = formatar_arvore_bom(pai)
            self.txt_bom.insert(tk.END, arvore)
        except ValueError as err:
            self.txt_bom.insert(tk.END, f"Erro: {err}")

    def _acao_add_bom(self) -> None:
        try:
            cadastrar_componente(
                codigo_pai=self.cb_bom_pai.get(),
                codigo_comp=self.cb_bom_comp.get(),
                quantidade=validar_float_positivo(self.ent_bom_qtd.get(), False),
            )
            self._exibir_arvore_bom()
            messagebox.showinfo("BOM", "Componente salvo na estrutura!")
        except ValueError as err:
            messagebox.showerror("Regra de Negócio (RN03)", str(err))

    def _acao_rem_bom(self) -> None:
        if remover_componente(self.cb_bom_pai.get(), self.cb_bom_comp.get()):
            self._exibir_arvore_bom()
            messagebox.showinfo("BOM", "Componente removido da estrutura.")
        else:
            messagebox.showwarning("BOM", "Componente não estava vinculado a este item pai.")

    def _carregar_centros_e_roteiros(self) -> None:
        centros = listar_centros()
        roteiros = listar_roteiros()
        self.cb_rot_ct["values"] = [c["codigo"] for c in centros]
        self.cb_crp_ct["values"] = [c["codigo"] for c in centros]
        if centros and not self.cb_crp_ct.get():
            self.cb_crp_ct.set("CT-03" if any(c["codigo"] == "CT-03" for c in centros) else centros[0]["codigo"])

        self.txt_ct_rot.delete("1.0", tk.END)
        self.txt_ct_rot.insert(tk.END, "=== CENTROS DE TRABALHO ===\n")
        for c in centros:
            self.txt_ct_rot.insert(
                tk.END,
                f"{c['codigo']} - {c['nome']} | Cap: {c['capacidade_semanal']:g} h/sem | Custo: {formatar_moeda(c['custo_hora'])}/h\n",
            )
        self.txt_ct_rot.insert(tk.END, "\n=== ROTEIROS DE FABRICAÇÃO ===\n")
        for item_cod, rot in sorted(roteiros.items()):
            self.txt_ct_rot.insert(
                tk.END, f"{item_cod} -> Centro: {rot['centro']} | Tempo unitário: {rot['tempo_unitario']:g} h/un\n"
            )

    def _acao_salvar_ct(self) -> None:
        try:
            cadastrar_centro(
                codigo=self.ent_ct_cod.get(),
                nome=self.ent_ct_nome.get(),
                capacidade_semanal=validar_float_positivo(self.ent_ct_cap.get(), False),
                custo_hora=validar_float_positivo(self.ent_ct_custo.get(), True),
            )
            self._carregar_centros_e_roteiros()
            messagebox.showinfo("Sucesso", "Centro de trabalho salvo!")
        except ValueError as err:
            messagebox.showerror("Erro", str(err))

    def _acao_salvar_rot(self) -> None:
        try:
            cadastrar_roteiro(
                codigo_item=self.cb_rot_item.get(),
                codigo_centro=self.cb_rot_ct.get(),
                tempo_unitario=validar_float_positivo(self.ent_rot_tempo.get(), False),
            )
            self._carregar_centros_e_roteiros()
            messagebox.showinfo("Sucesso", "Roteiro vinculado com sucesso!")
        except ValueError as err:
            messagebox.showerror("Erro", str(err))

    def _montar_aba_estoque(self) -> None:
        card_mov = ttk.Frame(self.aba_estoque, style="Card.TFrame", padding=10)
        card_mov.pack(fill="x", padx=6, pady=6)

        ttk.Label(card_mov, text="Item:", style="Card.TLabel").pack(side="left", padx=4)
        self.cb_mov_item = ttk.Combobox(card_mov, width=12, state="readonly")
        self.cb_mov_item.pack(side="left", padx=4)
        self.cb_mov_item.bind("<<ComboboxSelected>>", lambda _: self._exibir_kardex())

        ttk.Label(card_mov, text="Tipo:", style="Card.TLabel").pack(side="left", padx=4)
        self.cb_mov_tipo = ttk.Combobox(card_mov, values=["ENTRADA", "SAIDA", "AJUSTE"], width=10, state="readonly")
        self.cb_mov_tipo.set("ENTRADA")
        self.cb_mov_tipo.pack(side="left", padx=4)

        ttk.Label(card_mov, text="Qtde:", style="Card.TLabel").pack(side="left", padx=4)
        self.ent_mov_qtd = ttk.Entry(card_mov, width=10)
        self.ent_mov_qtd.pack(side="left", padx=4)

        ttk.Label(card_mov, text="Documento/Motivo:", style="Card.TLabel").pack(side="left", padx=4)
        self.ent_mov_doc = ttk.Entry(card_mov, width=24)
        self.ent_mov_doc.pack(side="left", padx=4)

        ttk.Label(card_mov, text="Data:", style="Card.TLabel").pack(side="left", padx=4)
        self.ent_mov_data = ttk.Entry(card_mov, width=11)
        self.ent_mov_data.insert(0, data_hoje_str())
        self.ent_mov_data.pack(side="left", padx=4)

        ttk.Button(card_mov, text="Registrar", style="Acao.TButton", command=self._acao_movimentar).pack(
            side="left", padx=8
        )

        paned = ttk.PanedWindow(self.aba_estoque, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=6, pady=6)

        cols = ("cod", "desc", "saldo", "es", "status")
        self.tree_estoque = ttk.Treeview(paned, columns=cols, show="headings")
        for cid, txt, w in [
            ("cod", "Código", 80),
            ("desc", "Descrição", 200),
            ("saldo", "Saldo", 80),
            ("es", "Est. Seg.", 80),
            ("status", "Situação", 130),
        ]:
            self.tree_estoque.heading(cid, text=txt)
            self.tree_estoque.column(cid, width=w, anchor="center" if cid != "desc" else "w")
        self.tree_estoque.tag_configure("alerta", background="#fee2e2", foreground="#991b1b")
        self.tree_estoque.bind("<<TreeviewSelect>>", self._ao_selecionar_estoque)
        paned.add(self.tree_estoque, weight=3)

        self.txt_kardex = tk.Text(paned, font=("Courier New", 10), bg="#ffffff", fg="#0f172a", padx=10, pady=10)
        paned.add(self.txt_kardex, weight=2)

    def _carregar_tabela_estoque(self) -> None:
        for r in self.tree_estoque.get_children():
            self.tree_estoque.delete(r)
        for s in listar_saldos():
            tag = ("alerta",) if s["abaixo_seguranca"] else ()
            situacao = "ABAIXO DO ES!" if s["abaixo_seguranca"] else "Normal"
            self.tree_estoque.insert(
                "",
                "end",
                values=(
                    s["codigo"],
                    s["descricao"],
                    f"{s['saldo']:g} {s['unidade']}",
                    f"{s['estoque_seguranca']:g}",
                    situacao,
                ),
                tags=tag,
            )

    def _ao_selecionar_estoque(self, _event: object) -> None:
        sel = self.tree_estoque.selection()
        if sel:
            cod = self.tree_estoque.item(sel[0], "values")[0]
            self.cb_mov_item.set(cod)
            self._exibir_kardex()

    def _exibir_kardex(self) -> None:
        cod = self.cb_mov_item.get()
        if not cod:
            return
        try:
            k = consultar_kardex(cod)
            self.txt_kardex.delete("1.0", tk.END)
            self.txt_kardex.insert(tk.END, f"KARDEX - {k['codigo']} {k['descricao']} ({k['unidade']})\n")
            self.txt_kardex.insert(tk.END, "-" * 58 + "\n")
            self.txt_kardex.insert(tk.END, f"{'Data':<12}{'Tipo':<10}{'Qtde':>8}{'Saldo':>9}  Documento\n")
            for m in k["movimentos"]:
                sinal = "+" if m["quantidade"] > 0 else ""
                self.txt_kardex.insert(
                    tk.END,
                    f"{m['data']:<12}{m['tipo']:<10}{sinal}{m['quantidade']:>7g}{m['saldo_apos']:>9g}  {m['documento']}\n",
                )
            self.txt_kardex.insert(tk.END, "-" * 58 + "\n")
            if k["abaixo_seguranca"]:
                self.txt_kardex.insert(
                    tk.END,
                    f"ALERTA: saldo ({k['saldo']:g} {k['unidade']}) abaixo do estoque de segurança ({k['estoque_seguranca']:g} {k['unidade']}).\n",
                )
        except ValueError as err:
            messagebox.showerror("Erro", str(err))

    def _acao_movimentar(self) -> None:
        try:
            tipo = self.cb_mov_tipo.get()
            qtd = float(self.ent_mov_qtd.get().replace(",", "."))
            registrar_movimentacao(
                codigo_item=self.cb_mov_item.get(),
                tipo=tipo,
                quantidade=qtd,
                documento=self.ent_mov_doc.get(),
                data=self.ent_mov_data.get(),
            )
            self._carregar_tabela_estoque()
            self._exibir_kardex()
            messagebox.showinfo("Estoque", "Movimentação registrada no Kardex!")
        except ValueError as err:
            messagebox.showerror("Erro de Movimentação (RN02)", str(err))

    def _montar_aba_mps(self) -> None:
        card_mps = ttk.Frame(self.aba_mps, style="Card.TFrame", padding=12)
        card_mps.pack(fill="x", padx=6, pady=6)

        ttk.Label(card_mps, text="Produto Acabado (PA):", style="Card.TLabel").pack(side="left", padx=5)
        self.cb_mps_pa = ttk.Combobox(card_mps, width=14, state="readonly")
        self.cb_mps_pa.pack(side="left", padx=5)

        ttk.Label(card_mps, text="Semana (1 a 8):", style="Card.TLabel").pack(side="left", padx=5)
        self.cb_mps_sem = ttk.Combobox(card_mps, values=[str(i) for i in range(1, 9)], width=6, state="readonly")
        self.cb_mps_sem.set("1")
        self.cb_mps_sem.pack(side="left", padx=5)

        ttk.Label(card_mps, text="Nova Demanda (un):", style="Card.TLabel").pack(side="left", padx=5)
        self.ent_mps_qtd = ttk.Entry(card_mps, width=10)
        self.ent_mps_qtd.pack(side="left", padx=5)

        ttk.Button(card_mps, text="Atualizar Demanda", style="Acao.TButton", command=self._acao_atualizar_mps).pack(
            side="left", padx=10
        )

        cols = ("pa", "s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8")
        self.tree_mps = ttk.Treeview(self.aba_mps, columns=cols, show="headings", height=10)
        self.tree_mps.heading("pa", text="Produto Acabado")
        self.tree_mps.column("pa", width=160, anchor="center")
        for i in range(1, 9):
            self.tree_mps.heading(f"s{i}", text=f"Semana {i}")
            self.tree_mps.column(f"s{i}", width=100, anchor="center")
        self.tree_mps.pack(fill="both", expand=True, padx=6, pady=6)

    def _carregar_tabela_mps(self) -> None:
        for r in self.tree_mps.get_children():
            self.tree_mps.delete(r)
        mps = obter_mps_completo()
        for cod_pa, semanas in mps.items():
            valores = [cod_pa] + [f"{v:g}" for v in semanas]
            self.tree_mps.insert("", "end", values=valores)

    def _acao_atualizar_mps(self) -> None:
        try:
            atualizar_semana_pa(
                codigo_pa=self.cb_mps_pa.get(),
                semana=int(self.cb_mps_sem.get()),
                quantidade=validar_float_positivo(self.ent_mps_qtd.get(), True),
            )
            self._carregar_tabela_mps()
            messagebox.showinfo("MPS", "Plano Mestre de Produção atualizado!")
        except ValueError as err:
            messagebox.showerror("Erro", str(err))

    def _montar_aba_mrp(self) -> None:
        topo_mrp = ttk.Frame(self.aba_mrp, style="Card.TFrame", padding=10)
        topo_mrp.pack(fill="x", padx=6, pady=6)

        ttk.Button(topo_mrp, text="▶ EXECUTAR CÁLCULO MRP COMPLETO", style="Acao.TButton", command=self._acao_rodar_mrp).pack(
            side="left", padx=6
        )

        ttk.Label(topo_mrp, text="Consultar Registro MRP do Item:", style="Card.TLabel").pack(side="left", padx=(20, 5))
        self.cb_mrp_item = ttk.Combobox(topo_mrp, width=14, state="readonly")
        self.cb_mrp_item.pack(side="left", padx=5)
        self.cb_mrp_item.bind("<<ComboboxSelected>>", lambda _: self._exibir_registro_mrp())

        self.txt_mrp = tk.Text(self.aba_mrp, font=("Courier New", 11), bg="#ffffff", fg="#0f172a", padx=15, pady=15)
        self.txt_mrp.pack(fill="both", expand=True, padx=6, pady=6)

    def _acao_rodar_mrp(self) -> None:
        res = executar_mrp()
        self._carregar_tabela_ordens()
        self._exibir_registro_mrp()
        qtd_ordens = len(res["ordens_geradas"])
        qtd_exc = len(res["excecoes"])
        messagebox.showinfo(
            "MRP Executado",
            f"Cálculo MRP concluído com sucesso!\n\n"
            f"• Ordens planejadas geradas: {qtd_ordens}\n"
            f"• Alertas de atraso (liberação < S1): {qtd_exc}",
        )

    def _exibir_registro_mrp(self) -> None:
        cod = self.cb_mrp_item.get()
        if not cod:
            return
        reg = obter_registro_mrp_item(cod)
        self.txt_mrp.delete("1.0", tk.END)
        self.txt_mrp.insert(tk.END, f"REGISTRO MRP - {reg['codigo']} {reg['descricao']}\n")
        self.txt_mrp.insert(
            tk.END,
            f"Lead time: {reg['lead_time']} sem | Est. segurança: {reg['estoque_seguranca']:g} | "
            f"Lote mín.: {reg['lote_minimo']:g} | Estoque inicial: {reg['estoque_inicial']:g}\n",
        )
        self.txt_mrp.insert(tk.END, "=" * 86 + "\n")
        cab_semanas = "".join([f"{'S' + str(i):>8}" for i in range(1, 9)])
        self.txt_mrp.insert(tk.END, f"{'Período / Linha':<24}{cab_semanas}\n")
        self.txt_mrp.insert(tk.END, "-" * 86 + "\n")

        linhas = [
            ("Necessidade bruta", reg["necessidade_bruta"]),
            ("Receb. programados", reg["recebimentos_programados"]),
            ("Estoque projetado", reg["estoque_projetado"]),
            ("Necessidade líquida", reg["necessidade_liquida"]),
            ("Receb. planejados", reg["recebimentos_planejados"]),
            ("Liberação planejada", reg["liberacoes_planejadas"]),
        ]
        for rotulo, vetor in linhas:
            vals = "".join([f"{v:>8g}" for v in vetor])
            self.txt_mrp.insert(tk.END, f"{rotulo:<24}{vals}\n")

        self.txt_mrp.insert(tk.END, "=" * 86 + "\n")
        excecoes = ULTIMO_RESULTADO_MRP.get("excecoes", [])
        if excecoes:
            self.txt_mrp.insert(tk.END, f"\nMENSAGENS DE EXCEÇÃO ({len(excecoes)}):\n")
            for exc in excecoes:
                self.txt_mrp.insert(tk.END, f" • {exc}\n")

    def _montar_aba_ordens(self) -> None:
        barra_ord = ttk.Frame(self.aba_ordens, style="Card.TFrame", padding=10)
        barra_ord.pack(fill="x", padx=6, pady=6)

        ttk.Button(
            barra_ord, text="Firmar Ordem", style="Secundario.TButton", command=lambda: self._acao_status_ordem("FIRME")
        ).pack(side="left", padx=4)
        ttk.Button(
            barra_ord, text="Liberar Ordem", style="Acao.TButton", command=lambda: self._acao_status_ordem("LIBERADA")
        ).pack(side="left", padx=4)
        ttk.Button(
            barra_ord, text="Apontar Produção (OP)", style="Acao.TButton", command=self._acao_apontar_op
        ).pack(side="left", padx=4)
        ttk.Button(
            barra_ord,
            text="Receber Compra (Encerrar OC)",
            style="Secundario.TButton",
            command=lambda: self._acao_status_ordem("ENCERRADA"),
        ).pack(side="left", padx=4)

        cols = ("cod", "tipo", "item", "qtde", "lib", "ent", "status", "prazo")
        self.tree_ordens = ttk.Treeview(self.aba_ordens, columns=cols, show="headings", height=18)
        for cid, txt, w in [
            ("cod", "Ordem", 100),
            ("tipo", "Tipo", 70),
            ("item", "Item", 110),
            ("qtde", "Quantidade", 110),
            ("lib", "Liberar", 90),
            ("ent", "Entregar", 90),
            ("status", "Status", 120),
            ("prazo", "Prazo", 120),
        ]:
            self.tree_ordens.heading(cid, text=txt)
            self.tree_ordens.column(cid, width=w, anchor="center")
        self.tree_ordens.tag_configure("atrasada", background="#fef3c7", foreground="#92400e")
        self.tree_ordens.pack(fill="both", expand=True, padx=6, pady=6)

    def _carregar_tabela_ordens(self) -> None:
        for r in self.tree_ordens.get_children():
            self.tree_ordens.delete(r)
        for o in listar_ordens():
            tag = ("atrasada",) if o.get("atrasada") else ()
            prazo_txt = "ATRASADA" if o.get("atrasada") else "No prazo"
            self.tree_ordens.insert(
                "",
                "end",
                values=(
                    o["codigo"],
                    o["tipo"],
                    o["item"],
                    f"{o['quantidade']:g}",
                    f"S{o['semana_liberacao']}",
                    f"S{o['semana_entrega']}",
                    o["status"],
                    prazo_txt,
                ),
                tags=tag,
            )

    def _obter_ordem_selecionada(self) -> str | None:
        sel = self.tree_ordens.selection()
        if not sel:
            messagebox.showwarning("Seleção", "Selecione uma ordem na tabela primeiro.")
            return None
        return str(self.tree_ordens.item(sel[0], "values")[0])

    def _acao_status_ordem(self, novo_status: str) -> None:
        cod = self._obter_ordem_selecionada()
        if not cod:
            return
        try:
            alterar_status_ordem(cod, novo_status)
            self.atualizar_todas_telas()
            messagebox.showinfo("Ordens", f"Ordem {cod} alterada para {novo_status}!")
        except ValueError as err:
            messagebox.showerror("Erro de Fluxo (RF10)", str(err))

    def _acao_apontar_op(self) -> None:
        cod = self._obter_ordem_selecionada()
        if not cod:
            return
        try:
            apontar_producao(cod)
            self.atualizar_todas_telas()
            messagebox.showinfo(
                "Apontamento Concluído",
                f"Produção da {cod} apontada!\nComponentes baixados do estoque e item produzido creditado.",
            )
        except ValueError as err:
            messagebox.showerror("Apontamento Rejeitado (RF11)", str(err))

    def _montar_aba_crp_custos(self) -> None:
        paned = ttk.PanedWindow(self.aba_crp_custos, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=6, pady=6)

        frame_crp = ttk.Frame(paned, style="Card.TFrame", padding=10)
        paned.add(frame_crp, weight=1)

        topo_crp = ttk.Frame(frame_crp, style="Card.TFrame")
        topo_crp.pack(fill="x", pady=(0, 8))
        ttk.Label(topo_crp, text="Centro:", style="Card.TLabel").pack(side="left", padx=4)
        self.cb_crp_ct = ttk.Combobox(topo_crp, width=10, state="readonly")
        self.cb_crp_ct.pack(side="left", padx=4)

        self.var_crp_apenas_lib = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            topo_crp,
            text="Apenas OPs Liberadas (RN09)",
            variable=self.var_crp_apenas_lib,
        ).pack(side="left", padx=6)

        ttk.Button(topo_crp, text="Calcular CRP", style="Acao.TButton", command=self._exibir_crp).pack(
            side="left", padx=4
        )

        self.txt_crp = tk.Text(frame_crp, font=("Courier New", 10), bg="#ffffff", fg="#0f172a", padx=10, pady=10)
        self.txt_crp.pack(fill="both", expand=True)

        frame_custo = ttk.Frame(paned, style="Card.TFrame", padding=10)
        paned.add(frame_custo, weight=1)

        topo_custo = ttk.Frame(frame_custo, style="Card.TFrame")
        topo_custo.pack(fill="x", pady=(0, 8))
        ttk.Label(topo_custo, text="Produto (PA/SA):", style="Card.TLabel").pack(side="left", padx=4)
        self.cb_custo_item = ttk.Combobox(topo_custo, width=12, state="readonly")
        self.cb_custo_item.pack(side="left", padx=4)
        ttk.Button(topo_custo, text="Calcular Custo Padrão", style="Acao.TButton", command=self._exibir_custo).pack(
            side="left", padx=6
        )

        self.txt_custo = tk.Text(frame_custo, font=("Courier New", 10), bg="#ffffff", fg="#0f172a", padx=10, pady=10)
        self.txt_custo.pack(fill="both", expand=True)

    def _exibir_crp(self) -> None:
        cod_ct = self.cb_crp_ct.get()
        if not cod_ct:
            return
        crp = calcular_crp_centro(cod_ct, apenas_liberadas=self.var_crp_apenas_lib.get())
        self.txt_crp.delete("1.0", tk.END)
        self.txt_crp.insert(
            tk.END, f"CARGA x CAPACIDADE - {crp['codigo']} {crp['nome']} ({crp['capacidade_semanal']:g} h/sem)\n"
        )
        self.txt_crp.insert(tk.END, "-" * 56 + "\n")
        self.txt_crp.insert(tk.END, f"{'Sem':<6}{'Carga(h)':>10}{'Uso(%)':>10}  Gráfico / Status\n")
        for s in crp["semanas"]:
            barras = "#" * min(20, int(s["uso_percentual"] // 10))
            alerta = " SOBRECARGA!" if s["sobrecarga"] else ""
            self.txt_crp.insert(
                tk.END, f"{s['semana']:<6}{s['carga_horas']:>10.1f}{s['uso_percentual']:>9.0f}%  {barras}{alerta}\n"
            )
        if crp["semanas_sobrecarga"]:
            sems = ", ".join(str(x) for x in crp["semanas_sobrecarga"])
            self.txt_crp.insert(tk.END, f"\nSugestão: antecipar OPs ou programar hora extra nas semanas {sems}.\n")

    def _exibir_custo(self) -> None:
        cod = self.cb_custo_item.get()
        if not cod:
            return
        res = calcular_custo_padrao(cod)
        self.txt_custo.delete("1.0", tk.END)
        self.txt_custo.insert(tk.END, f"CUSTO PADRÃO - {res['codigo']} {res['descricao']}\n")
        self.txt_custo.insert(tk.END, "-" * 64 + "\n")
        self.txt_custo.insert(tk.END, f"{'Item':<10}{'Descrição':<26}{'Qtde':>7}{'Custo Un.':>11}{'Total':>10}\n")
        for lin in res["linhas"]:
            qtd_txt = f"{lin['quantidade']:g} {lin['unidade']}"
            self.txt_custo.insert(
                tk.END,
                f"{lin['codigo']:<10}{lin['descricao'][:25]:<26}{qtd_txt:>7}"
                f"{lin['custo_unitario']:>11.2f}{lin['total']:>10.2f}\n",
            )
        self.txt_custo.insert(tk.END, "-" * 64 + "\n")
        self.txt_custo.insert(tk.END, f"CUSTO PADRÃO TOTAL: {formatar_moeda(res['custo_total'])}\n")

    def _montar_aba_relatorios(self) -> None:
        container = ttk.Frame(self.aba_relatorios, style="Card.TFrame", padding=20)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(container, text="Exportação de Relatórios Gerenciais (CSV - RF14)", style="Titulo.TLabel").pack(
            anchor="w", pady=(0, 8)
        )
        frame_csv = ttk.Frame(container, style="Card.TFrame")
        frame_csv.pack(fill="x", pady=(0, 20))

        ttk.Button(
            frame_csv,
            text="Exportar Posição de Estoque (CSV)",
            style="Secundario.TButton",
            command=self._acao_csv_estoque,
        ).pack(side="left", padx=6)
        ttk.Button(
            frame_csv,
            text="Exportar Lista de Ordens (CSV)",
            style="Secundario.TButton",
            command=self._acao_csv_ordens,
        ).pack(side="left", padx=6)

        ttk.Separator(container, orient="horizontal").pack(fill="x", pady=12)

        ttk.Label(
            container, text="Gráficos de Gestão e Acompanhamento (Matplotlib / PNG em docs/ - RF16)", style="Titulo.TLabel"
        ).pack(anchor="w", pady=(0, 10))

        grid_graf = ttk.Frame(container, style="Card.TFrame")
        grid_graf.pack(fill="x")

        ttk.Button(
            grid_graf,
            text="1. Posição de Estoque (Saldo x ES)",
            style="Acao.TButton",
            command=lambda: self._gerar_graf(grafico_posicao_estoque),
        ).grid(row=0, column=0, padx=6, pady=6, sticky="ew")

        ttk.Button(
            grid_graf,
            text="2. Estoque Projetado (Item da Aba MRP)",
            style="Acao.TButton",
            command=lambda: self._gerar_graf(lambda: grafico_estoque_projetado(self.cb_mrp_item.get())),
        ).grid(row=0, column=1, padx=6, pady=6, sticky="ew")

        ttk.Button(
            grid_graf,
            text="3. Ordens por Semana (OP x OC)",
            style="Acao.TButton",
            command=lambda: self._gerar_graf(grafico_ordens_por_semana),
        ).grid(row=1, column=0, padx=6, pady=6, sticky="ew")

        ttk.Button(
            grid_graf,
            text="4. Carga x Capacidade (Centro da Aba CRP)",
            style="Acao.TButton",
            command=lambda: self._gerar_graf(
                lambda: grafico_carga_capacidade(self.cb_crp_ct.get(), self.var_crp_apenas_lib.get())
            ),
        ).grid(row=1, column=1, padx=6, pady=6, sticky="ew")

    def _acao_csv_estoque(self) -> None:
        arq = exportar_posicao_estoque_csv()
        messagebox.showinfo("CSV Exportado", f"Arquivo salvo com sucesso em:\n{arq}")

    def _acao_csv_ordens(self) -> None:
        arq = exportar_ordens_csv()
        messagebox.showinfo("CSV Exportado", f"Arquivo salvo com sucesso em:\n{arq}")

    def _gerar_graf(self, func_grafico: object) -> None:
        try:
            caminho = func_grafico()
            messagebox.showinfo("Gráfico Gerado", f"Imagem PNG salva em:\n{caminho}")
        except Exception as err:
            messagebox.showerror("Erro ao Gerar Gráfico", str(err))


def iniciar_interface() -> None:
    app = AplicacaoMRP2()
    app.mainloop()