import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
from collections import defaultdict
import os

from app.components.list_rounded_button import ListRoundedButton
from app.components.custom_calendar import CustomCalendar
from app.interface.report.generate_graphics import ReportGraphics
from app.interface.report.get_graphics import GetGraphics

from app.repositories.report_repository import (
    get_maintenances, get_refuelings, get_driver_bonuses,
    get_driver_salaries_proportional, get_student_payments,
    get_route_extra_payments, get_route_expense_payments,
    get_trips_profit,
    get_vehicle_plate_map,
    get_route_receipts,
    get_all_receipts_monthly,
    get_all_expenses_monthly,
)

try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure

    MATPLOTLIB_AVAILABLE = True
except Exception:
    MATPLOTLIB_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas as pdfcanvas

    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False


class InterfaceRelatorio:
    def __init__(self, parent, db_path):
        self.parent = parent
        self.db_path = db_path

        self.bg_main = "#1c1c1e"
        self.bg_button = "#3a3f47"
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"
        self.font_label = ("Segoe UI", 12, "bold")
        self.font_button = ("Segoe UI", 11, "bold")
        self.font_title = ("Segoe UI", 24, "bold")
        self.font_tree = ("Segoe UI", 10)

        self.report_rows = []
        self.totals = {"in": 0.0, "out": 0.0}

        self.graphics = ReportGraphics(theme="dark")
        self.figs_generator = GetGraphics(self.graphics)

    def show(self):
        for w in self.parent.winfo_children():
            w.destroy()
        self.parent.configure(bg=self.bg_main)

        frame = tk.Frame(self.parent, bg=self.bg_main)
        frame.pack(fill="both", expand=True, padx=30, pady=20)

        tk.Label(
            frame,
            text="Relatório Consolidado",
            font=self.font_title,
            bg=self.bg_main,
            fg=self.accent
        ).pack(anchor="w", pady=(0, 15))

        controls = tk.Frame(frame, bg=self.bg_main)
        controls.pack(fill="x", pady=(0, 15))

        tk.Label(controls, text="Período - De:", bg=self.bg_main, fg=self.fg_text, font=self.font_label).grid(row=0,
                                                                                                              column=0,
                                                                                                              padx=5,
                                                                                                              sticky="w")

        data_30d_ago = (datetime.now() - timedelta(days=30)).strftime("%d/%m/%Y")
        self.start_var = tk.StringVar(value=data_30d_ago)
        self.start_entry = tk.Entry(controls, textvariable=self.start_var, width=12, bg=self.bg_button,
                                    fg=self.fg_text, justify="center", font=("Segoe UI", 11), borderwidth=0)
        self.start_entry.grid(row=0, column=1, padx=5)
        self.start_entry.bind("<Button-1>", lambda e: self.open_calendar(self.start_var))

        tk.Label(controls, text="Até:", bg=self.bg_main, fg=self.fg_text, font=self.font_label).grid(row=0, column=2,
                                                                                                     padx=5, sticky="w")

        self.end_var = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        self.end_entry = tk.Entry(controls, textvariable=self.end_var, width=12, bg=self.bg_button,
                                  fg=self.fg_text, justify="center", font=("Segoe UI", 11), borderwidth=0)
        self.end_entry.grid(row=0, column=3, padx=5)
        self.end_entry.bind("<Button-1>", lambda e: self.open_calendar(self.end_var))

        btns_inner = tk.Frame(controls, bg=self.bg_main)
        btns_inner.grid(row=0, column=4, padx=20, sticky="w")

        ListRoundedButton(btns_inner, text="Gerar relatório", command=self.generate_report,
                          bg=self.bg_button, fg=self.fg_text, width=160, height=35).pack(side="left", padx=5)

        ListRoundedButton(btns_inner, text="Dashboard (Gráficos)", command=self.open_dashboard_tabs,
                          bg=self.accent, fg=self.fg_text, width=180, height=35).pack(side="left", padx=5)

        self.result_frame = tk.Frame(frame, bg=self.bg_main)
        self.result_frame.pack(fill="both", expand=True)

    def open_calendar(self, target_var):
        def set_date(d):
            target_var.set(d.strftime("%d/%m/%Y"))

        CustomCalendar(self.parent, callback=set_date)

    def _to_sql_date(self, ddmmyyyy: str) -> str:
        try:
            return datetime.strptime(ddmmyyyy, "%d/%m/%Y").strftime("%Y-%m-%d")
        except Exception:
            return datetime.now().strftime("%Y-%m-%d")

    def _to_month_key(self, date_s: str) -> str:
        try:
            return date_s[:7]
        except Exception:
            return "9999-01"

    def generate_report(self):
        for w in self.result_frame.winfo_children():
            w.destroy()

        self.report_rows = []
        self.totals = {"in": 0.0, "out": 0.0}

        start = self._to_sql_date(self.start_var.get())
        end = self._to_sql_date(self.end_var.get())

        try:
            maints = get_maintenances(self.db_path, start, end)
            refuels = get_refuelings(self.db_path, start, end)
            bonuses = get_driver_bonuses(self.db_path, start, end)
            salaries = get_driver_salaries_proportional(self.db_path, start, end)
            stud_pays = get_student_payments(self.db_path, start, end)
            extra_pays = get_route_extra_payments(self.db_path, start, end)
            route_exps = get_route_expense_payments(self.db_path, start, end)
            trips = get_trips_profit(self.db_path, start, end)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro na consulta: {e}")
            return

        for r in maints + refuels + route_exps + salaries + bonuses:
            date_s, cat, plate, desc, amt, extra = r
            val = -abs(float(amt))
            self.report_rows.append((date_s, cat, plate, desc, val, extra))
            self.totals["out"] += abs(float(amt))

        for r in stud_pays + extra_pays + trips:
            date_s, cat, plate, desc, amt, extra = r
            val = float(amt)
            self.report_rows.append((date_s, cat, plate, desc, val, extra))
            self.totals["in"] += float(amt)

        self.report_rows.sort(key=lambda x: x[0] or "")

        cols = ("Data", "Categoria", "Identificador", "Descrição", "Valor (R$)")
        tree_frame = tk.Frame(self.result_frame, bg=self.bg_main)
        tree_frame.pack(fill="both", expand=True)

        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=15)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2c2c2e", foreground="#ffffff", fieldbackground="#2c2c2e",
                        font=self.font_tree, rowheight=25)
        style.configure("Treeview.Heading", background="#3a3f47", foreground=self.accent, font=self.font_tree)

        for c in cols:
            tree.heading(c, text=c)

        tree.column("Data", width=100, anchor="center")
        tree.column("Categoria", width=120, anchor="center")
        tree.column("Identificador", width=120, anchor="center")
        tree.column("Descrição", width=350, anchor="w")
        tree.column("Valor (R$)", width=120, anchor="e")

        tree.pack(side="left", fill="both", expand=True)

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

        if not self.report_rows:
            tk.Label(self.result_frame, text="Nenhum registro encontrado no período.", bg=self.bg_main, fg="#888888",
                     font=("Segoe UI", 11)).pack(pady=20)
            return

        for date_s, cat, plate, desc, val, extra in self.report_rows:
            tag = "saida" if val < 0 else "entrada"
            tree.tag_configure("entrada", foreground="#8adf8a")
            tree.tag_configure("saida", foreground="#ff8a8a")

            d_fmt = datetime.strptime(date_s, "%Y-%m-%d").strftime("%d/%m/%Y") if date_s else ""
            tree.insert("", "end", values=(d_fmt, cat, plate or "", (desc or "").upper(), f"{val:.2f}"), tags=(tag,))

        total_in = self.totals["in"]
        total_out = self.totals["out"]
        net = total_in - total_out

        summary = tk.Frame(self.result_frame, bg=self.bg_main)
        summary.pack(fill="x", pady=(15, 0))

        tk.Label(summary, text=f"Entradas: R$ {total_in:.2f}", bg=self.bg_main, fg="#8adf8a",
                 font=("Segoe UI", 12, "bold")).pack(side="left", padx=15)
        tk.Label(summary, text=f"Saídas: R$ {total_out:.2f}", bg=self.bg_main, fg="#ff8a8a",
                 font=("Segoe UI", 12, "bold")).pack(side="left", padx=15)
        tk.Label(summary, text=f"Saldo Líquido: R$ {net:.2f}", bg=self.bg_main, fg=self.accent,
                 font=("Segoe UI", 13, "bold")).pack(side="left", padx=15)

    def open_dashboard_tabs(self):
        if not MATPLOTLIB_AVAILABLE:
            messagebox.showwarning("Aviso", "A biblioteca Matplotlib não está instalada.")
            return
        if not self.report_rows:
            messagebox.showinfo("Aviso", "Gere um relatório com dados antes de abrir o dashboard.")
            return

        start = self._to_sql_date(self.start_var.get())
        end = self._to_sql_date(self.end_var.get())

        try:
            veiculos_map = get_vehicle_plate_map(self.db_path)
        except Exception:
            veiculos_map = {}

        lucro_por_veiculo = defaultdict(float)
        gastos_por_veiculo = defaultdict(float)
        recebimentos_por_aluno = defaultdict(float)
        despesa_por_categoria = defaultdict(float)
        timeline_monthly = defaultdict(lambda: {"in": 0.0, "out": 0.0, "net": 0.0})

        for date_s, cat, plate, desc, val, extra in self.report_rows:
            month_key = self._to_month_key(date_s)
            if val >= 0:
                timeline_monthly[month_key]["in"] += val
            else:
                timeline_monthly[month_key]["out"] += -val
            timeline_monthly[month_key]["net"] += val

            if plate and plate in veiculos_map:
                v_name = veiculos_map[plate]
                lucro_por_veiculo[v_name] += val
                if val < 0 and cat in ["Manutenção", "Abastecimento"]:
                    gastos_por_veiculo[v_name] += -val

            if cat and "pagamento aluno" in cat.lower():
                aluno = (desc or "").strip()
                if aluno: recebimentos_por_aluno[aluno] += val

            if val < 0:
                despesa_por_categoria[cat or "Outro"] += -val

        try:
            rec_mensal = get_all_receipts_monthly(self.db_path, start, end)
            pagamentos_alunos_mes = rec_mensal.get("student_payments", {})
            extras_linha_mes = rec_mensal.get("route_extras", {})
            despesas_por_mes = get_all_expenses_monthly(self.db_path, start, end)
            lucros_por_mes = {k: v["net"] for k, v in timeline_monthly.items()}
            receita_por_linha = get_route_receipts(self.db_path, start, end)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar dados dos gráficos: {e}")
            return

        figs, descriptions = self.figs_generator.get_figs(
            despesa_por_categoria, despesas_por_mes, extras_linha_mes,
            gastos_por_veiculo, lucro_por_veiculo, lucros_por_mes,
            pagamentos_alunos_mes, recebimentos_por_aluno, receita_por_linha
        )

        win = tk.Toplevel(self.parent)
        win.title("Dashboard de Análise")
        win.configure(bg=self.bg_main)
        win.geometry("1100x750")

        top_bar = tk.Frame(win, bg=self.bg_main)
        top_bar.pack(fill="x", padx=10, pady=10)

        ListRoundedButton(top_bar, text="Exportar PDF", bg=self.bg_button, fg=self.fg_text,
                          command=lambda: self._export_all_pdf(figs, descriptions), width=150, height=35).pack(
            side="right", padx=5)

        ListRoundedButton(top_bar, text="Salvar Imagens", bg=self.bg_button, fg=self.fg_text,
                          command=lambda: self._save_all_png(figs), width=150, height=35).pack(side="right", padx=5)

        notebook = ttk.Notebook(win)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        for i, fig in enumerate(figs):
            f = tk.Frame(notebook, bg=self.bg_main)
            notebook.add(f, text=f"Análise {i + 1}")
            canvas = FigureCanvasTkAgg(fig, master=f)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

    def _save_all_png(self, figs):
        if not figs: return
        path = filedialog.askdirectory(title="Selecionar pasta de destino")
        if not path: return
        try:
            for idx, fig in enumerate(figs, start=1):
                f_name = os.path.join(path, f"grafico_{idx}_{datetime.now().strftime('%Y%m%d')}.png")
                fig.savefig(f_name, bbox_inches='tight', dpi=120)
            messagebox.showinfo("Sucesso", "Imagens salvas com sucesso.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _export_all_pdf(self, figs, descriptions):
        if not REPORTLAB_AVAILABLE:
            messagebox.showwarning("Aviso", "Instale a biblioteca 'reportlab' para exportar em PDF.")
            return

        fpath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not fpath: return

        try:
            from reportlab.lib.utils import ImageReader
            from reportlab.platypus import Paragraph
            from reportlab.lib.styles import getSampleStyleSheet

            c = pdfcanvas.Canvas(fpath, pagesize=A4)
            width, height = A4
            styles = getSampleStyleSheet()
            tmp_files = []

            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(width / 2, height - 50, "Relatório de Gestão Financeira")
            c.setFont("Helvetica", 10)
            c.drawCentredString(width / 2, height - 70, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            c.line(50, height - 80, width - 50, height - 80)

            for idx, (fig, desc) in enumerate(zip(figs, descriptions)):
                tmp = f"temp_plt_{idx}.png"
                fig.savefig(tmp, bbox_inches="tight", dpi=100)
                tmp_files.append(tmp)

                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, height - 110, f"Análise Técnica - Gráfico {idx + 1}")

                p = Paragraph(desc, styles["Normal"])
                p_w, p_h = p.wrap(width - 100, height)
                p.drawOn(c, 50, height - 130 - p_h)

                c.drawImage(ImageReader(tmp), 50, 100, width=width - 100, height=height - 300, preserveAspectRatio=True)
                c.showPage()

            c.save()
            for t in tmp_files:
                if os.path.exists(t):
                    os.remove(t)
            messagebox.showinfo("Sucesso", "Relatório PDF gerado com sucesso.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar PDF: {e}")