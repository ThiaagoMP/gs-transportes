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
        self.font_label = ("Segoe UI", 14, "bold")
        self.font_button = ("Segoe UI", 12, "bold")
        self.font_title = ("Segoe UI", 28, "bold")
        self.font_tree = ("Segoe UI", 11)

        self.report_rows = []
        self.totals = {"in": 0.0, "out": 0.0}

        self.graphics = ReportGraphics(theme="dark")
        self.figs_generator = GetGraphics(self.graphics)

    def show(self):
        for w in self.parent.winfo_children():
            w.destroy()
        self.parent.configure(bg=self.bg_main)

        frame = tk.Frame(self.parent, bg=self.bg_main)
        frame.pack(fill="both", expand=True, padx=24, pady=20)

        title = tk.Label(frame, text="Relatório Consolidado", font=self.font_title, bg=self.bg_main, fg=self.accent)
        title.pack(anchor="w", pady=(0, 12))

        controls = tk.Frame(frame, bg=self.bg_main)
        controls.pack(fill="x", pady=(0, 12))

        lbl_style = {"bg": self.bg_main, "fg": self.fg_text, "font": self.font_label}
        tk.Label(controls, text="Período - De:", **lbl_style).grid(row=0, column=0, padx=6, pady=6, sticky="w")
        data_30d_ago = (datetime.now() - timedelta(days=30)).strftime("%d/%m/%Y")
        self.start_var = tk.StringVar(value=data_30d_ago)
        self.start_entry = tk.Entry(controls, textvariable=self.start_var, width=14, bg=self.bg_button,
                                    fg=self.fg_text, justify="center")
        self.start_entry.grid(row=0, column=1, padx=6, pady=6, sticky="w")
        self.start_entry.bind("<Button-1>", lambda e: self.open_calendar(self.start_var))

        tk.Label(controls, text="Até:", **lbl_style).grid(row=0, column=2, padx=6, pady=6, sticky="w")
        self.end_var = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        self.end_entry = tk.Entry(controls, textvariable=self.end_var, width=14, bg=self.bg_button,
                                  fg=self.fg_text, justify="center")
        self.end_entry.grid(row=0, column=3, padx=6, pady=6, sticky="w")
        self.end_entry.bind("<Button-1>", lambda e: self.open_calendar(self.end_var))

        btns = tk.Frame(controls, bg=self.bg_main)
        btns.grid(row=0, column=4, padx=12, pady=6, sticky="w")
        ListRoundedButton(btns, text="Gerar Relatório", command=self.generate_report,
                          bg=self.bg_button, fg=self.fg_text, hover_bg=self.accent,
                          width=180, height=44, font=self.font_button).grid(row=0, column=0, padx=6)
        ListRoundedButton(btns, text="Abrir Dashboard (Gráficos)", command=self.open_dashboard_tabs,
                          bg=self.bg_button, fg=self.fg_text, hover_bg=self.accent,
                          width=200, height=44, font=self.font_button).grid(row=0, column=2, padx=6)

        self.result_frame = tk.Frame(frame, bg=self.bg_main)
        self.result_frame.pack(fill="both", expand=True, pady=(12, 0))

    def open_calendar(self, target_var):
        def set_date(d):
            target_var.set(d.strftime("%d/%m/%Y"))

        CustomCalendar(self.parent, callback=set_date)

    def _to_sql_date(self, ddmmyyyy: str) -> str:
        try:
            dt = datetime.strptime(ddmmyyyy, "%d/%m/%Y").date()
            return dt.strftime("%Y-%m-%d")
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
            messagebox.showerror("Erro", f"Erro ao consultar repositório: {e}")
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

        try:
            self.report_rows.sort(key=lambda x: x[0] or "")
        except Exception:
            pass

        cols = ("Data", "Categoria", "Identificador", "Descrição", "Valor (R$)")
        tree = ttk.Treeview(self.result_frame, columns=cols, show="headings", height=16)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#3a3f47", foreground="#ffffff", fieldbackground="#3a3f47",
                        font=self.font_tree)
        style.configure("Treeview.Heading", background="#2a2e34", foreground="#ff7f32", font=self.font_tree)

        for c in cols:
            tree.heading(c, text=c)
        tree.column("Descrição", width=360)
        tree.pack(fill="both", expand=True, pady=(6, 10))

        if not self.report_rows:
            tk.Label(self.result_frame, text="Nenhum registro encontrado no período.", bg=self.bg_main,
                     fg=self.fg_text, font=("Segoe UI", 12)).pack(pady=12)
            return

        for date_s, cat, plate, desc, val, extra in self.report_rows:
            tag = "saida" if val < 0 else "entrada"
            tree.tag_configure("entrada", foreground="#8adf8a")
            tree.tag_configure("saida", foreground="#ff8a8a")

            tree.insert("", "end", values=(date_s or "", cat, plate or "", desc or "", f"{val:.2f}"), tags=(tag,))

        total_in = self.totals["in"]
        total_out = self.totals["out"]
        net = total_in - total_out

        summary = tk.Frame(self.result_frame, bg=self.bg_main)
        summary.pack(fill="x", pady=(8, 0))
        tk.Label(summary, text=f"Total Entradas: R$ {total_in:.2f}", bg=self.bg_main, fg="#8adf8a",
                 font=("Segoe UI", 12, "bold")).pack(side="left", padx=8)
        tk.Label(summary, text=f"Total Saídas: R$ {total_out:.2f}", bg=self.bg_main, fg="#ff8a8a",
                 font=("Segoe UI", 12, "bold")).pack(side="left", padx=8)
        tk.Label(summary, text=f"Lucro Líquido: R$ {net:.2f}", bg=self.bg_main, fg=self.accent,
                 font=("Segoe UI", 12, "bold")).pack(side="left", padx=8)

    def open_dashboard_tabs(self):
        if not MATPLOTLIB_AVAILABLE:
            messagebox.showwarning("Biblioteca ausente",
                                   "Instale 'matplotlib' (`pip install matplotlib`) para gráficos.")
            return
        if not self.report_rows:
            messagebox.showinfo("Sem dados", "Gere o relatório antes de abrir o dashboard.")
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
                vehicle_name = veiculos_map[plate]
                lucro_por_veiculo[vehicle_name] += val

                if val < 0 and cat in ["Manutenção", "Abastecimento"]:
                    gastos_por_veiculo[vehicle_name] += -val

            if cat and "pagamento aluno" in cat.lower():
                aluno = (desc or "").strip()
                if aluno:
                    recebimentos_por_aluno[aluno] += val

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
            messagebox.showerror("Erro de Repositório", f"Falha ao obter dados mensais/rota: {e}")
            return

        figs, descriptions = self.figs_generator.get_figs(
            despesa_por_categoria,
            despesas_por_mes,
            extras_linha_mes,
            gastos_por_veiculo,
            lucro_por_veiculo,
            lucros_por_mes,
            pagamentos_alunos_mes,
            recebimentos_por_aluno,
            receita_por_linha
        )

        win = tk.Toplevel(self.parent)
        win.title("Dashboard de Gráficos")
        win.configure(bg=self.bg_main)
        win.geometry("1100x700")

        top_bar = tk.Frame(win, bg=self.bg_main)
        top_bar.pack(fill="x", padx=8, pady=6)
        tk.Button(top_bar, text="Salvar todos PNG", bg=self.bg_button, fg=self.fg_text,
                  command=lambda: self._save_all_png(figs)).pack(side="right", padx=6)
        tk.Button(top_bar, text="Exportar todos para PDF", bg=self.bg_button, fg=self.fg_text,
                  command=lambda: self._export_all_pdf(figs, descriptions)).pack(side="right", padx=6)

        style = ttk.Style()

        if "dark_notebook" not in style.theme_names():
            style.theme_create("dark_notebook", parent="alt", settings={
                "TNotebook": {"configure": {"background": self.bg_main, "bordercolor": self.bg_button}},
                "TNotebook.Tab": {
                    "configure": {"background": self.bg_button, "foreground": self.fg_text, "padding": [10, 5],
                                  "font": self.font_button},
                    "map": {"background": [("selected", self.accent)],
                            "foreground": [("selected", self.bg_main)]}}
            })

        style.theme_use("dark_notebook")

        notebook = ttk.Notebook(win)
        notebook.pack(fill="both", expand=True, padx=8, pady=8)

        for i, fig in enumerate(figs):
            frame = tk.Frame(notebook, bg=self.bg_main)
            notebook.add(frame, text=f"Gráfico {i + 1}")
            try:
                canvas = FigureCanvasTkAgg(fig, master=frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True)
            except Exception as e:
                tk.Label(frame, text=f"Erro ao renderizar gráfico: {e}", bg=self.bg_main, fg="red").pack(fill="both",
                                                                                                         expand=True)

    def _save_all_png(self, figs):
        if not figs:
            messagebox.showinfo("Sem gráficos", "Não há gráficos para salvar.")
            return
        d = filedialog.askdirectory(title="Escolha a pasta para salvar PNGs")
        if not d:
            return
        try:
            for idx, fig in enumerate(figs, start=1):
                fname = os.path.join(d, f"grafico_{idx}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png")
                fig.savefig(fname, bbox_inches='tight', dpi=150)
            messagebox.showinfo("OK", "PNG(s) salvos com sucesso.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar PNGs: {e}")

    def _export_all_pdf(self, figs, descriptions):
        if not REPORTLAB_AVAILABLE:
            messagebox.showwarning(
                "Biblioteca ausente",
                "Instale reportlab (`pip install reportlab`) para exportar PDF."
            )
            return

        if not figs:
            messagebox.showinfo("Sem gráficos", "Não há gráficos para exportar.")
            return

        fpath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        if not fpath:
            return

        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.utils import ImageReader
            from reportlab.platypus import Paragraph
            from reportlab.lib.styles import getSampleStyleSheet

            c = pdfcanvas.Canvas(fpath, pagesize=A4)
            width, height = A4

            styles = getSampleStyleSheet()

            tmp_files = []

            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(width / 2, height - 100, "Relatório Financeiro")

            c.setFont("Helvetica", 11)
            c.drawCentredString(
                width / 2,
                height - 130,
                f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            )

            c.line(80, height - 145, width - 80, height - 145)

            intro_text = (
                "Este relatório apresenta gráficos e análises financeiras geradas "
                "automaticamente pelo sistema. O objetivo é auxiliar na tomada de "
                "decisões, oferecendo uma visão clara do desempenho financeiro, "
                "custos operacionais, consumo e lucratividade."
            )

            intro_style = styles["Normal"]
            intro_style.fontName = "Helvetica"
            intro_style.fontSize = 11
            intro_style.leading = 14

            intro_paragraph = Paragraph(intro_text, intro_style)

            max_width = width - 160
            p_width, p_height = intro_paragraph.wrap(max_width, height)

            intro_paragraph.drawOn(
                c,
                80,
                height - 165 - p_height
            )

            c.showPage()

            for fig, desc in zip(figs, descriptions):
                tmp = f"_tmp_{datetime.now().timestamp()}.png"
                fig.savefig(tmp, bbox_inches="tight", dpi=150)
                tmp_files.append(tmp)

                c.setFont("Helvetica-Bold", 12)
                c.drawString(40, height - 60, "Descrição do gráfico")

                desc_style = styles["Normal"]
                desc_style.fontName = "Helvetica"
                desc_style.fontSize = 10
                desc_style.leading = 13

                desc_paragraph = Paragraph(desc, desc_style)

                desc_width = width - 80
                d_width, d_height = desc_paragraph.wrap(desc_width, height)

                desc_paragraph.drawOn(
                    c,
                    40,
                    height - 80 - d_height
                )

                img = ImageReader(tmp)

                img_width = width - 80
                img_height = height - 200 - d_height

                c.drawImage(
                    img,
                    40,
                    60,
                    width=img_width,
                    height=img_height,
                    preserveAspectRatio=True
                )

                c.showPage()

            c.save()

            for t in tmp_files:
                try:
                    os.remove(t)
                except Exception:
                    pass

            messagebox.showinfo("OK", f"PDF salvo em {fpath}")

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao exportar PDF: {e}")

