import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

from app.components.list_rounded_button import ListRoundedButton
from app.repositories.maintenance_repository import MaintenanceRepository

class InterfaceMaintenance:
    def __init__(self, parent, db_path, vehicle_id, vehicle_name):
        self.parent = parent
        self.db_path = db_path
        self.vehicle_id = vehicle_id
        self.vehicle_name = vehicle_name
        self.maintenance_repo = MaintenanceRepository(self.db_path)

        self.bg_main = "#1c1c1e"
        self.bg_button = "#3a3f47"
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        self.parent.configure(bg=self.bg_main)

        header_frame = tk.Frame(self.parent, bg=self.bg_main)
        header_frame.pack(fill="x", padx=25, pady=(20, 10))

        tk.Label(
            header_frame,
            text=f"Manutenções: {self.vehicle_name.title()}",
            font=("Segoe UI", 22, "bold"),
            bg=self.bg_main,
            fg=self.accent
        ).pack(side="left")

        main_frame = tk.Frame(self.parent, bg=self.bg_main)
        main_frame.pack(padx=20, pady=5, fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        font=("Segoe UI", 11),
                        background="#2c2c2e",
                        fieldbackground="#2c2c2e",
                        foreground=self.fg_text,
                        rowheight=30,
                        borderwidth=0)
        style.configure("Treeview.Heading",
                        font=("Segoe UI", 11, "bold"),
                        background=self.accent,
                        foreground="#ffffff",
                        borderwidth=0)
        style.map("Treeview",
                  background=[("selected", self.accent)],
                  foreground=[("selected", "#ffffff")])

        tree_container = tk.Frame(main_frame, bg=self.bg_main)
        tree_container.pack(fill="both", expand=True, padx=10, pady=5)

        x_scroll = ttk.Scrollbar(tree_container, orient="horizontal")
        y_scroll = ttk.Scrollbar(tree_container, orient="vertical")

        self.tree = ttk.Treeview(
            tree_container,
            columns=("Data Início", "Data Fim", "Valor", "Preventiva", "Quilometragem", "Descrição"),
            show="headings",
            xscrollcommand=x_scroll.set,
            yscrollcommand=y_scroll.set
        )

        x_scroll.config(command=self.tree.xview)
        y_scroll.config(command=self.tree.yview)

        y_scroll.pack(side="right", fill="y")
        x_scroll.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)

        cols = [
            ("Data Início", 110), ("Data Fim", 110), ("Valor", 100),
            ("Preventiva", 100), ("Quilometragem", 120), ("Descrição", 250)
        ]

        for col, width in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")

        button_frame = tk.Frame(main_frame, bg=self.bg_main)
        button_frame.pack(pady=20)

        actions = [
            ("Nova manutenção", self.adicionar_manutencao),
            ("Baixar comprovante", self.baixar_comprovante),
            ("Excluir", self.excluir_manutencao),
            ("Voltar", self.back)
        ]

        for text, cmd in actions:
            color = "#b00020" if text == "Excluir" else self.bg_button
            ListRoundedButton(
                button_frame,
                text=text,
                command=cmd,
                width=160,
                height=40,
                bg=color,
                fg=self.fg_text,
                font=("Segoe UI", 10, "bold")
            ).pack(side="left", padx=5)

        self.load_maintenances()

    def load_maintenances(self):
        self.tree.delete(*self.tree.get_children())
        try:
            all_maints = self.maintenance_repo.get_all()
            vehicle_maints = [m for m in all_maints if int(m.vehicle_id) == int(self.vehicle_id)]
            vehicle_maints.sort(key=lambda m: str(m.start_date), reverse=True)

            for m in vehicle_maints:
                self.tree.insert("", "end", iid=str(m.maintenance_id), values=(
                    self.format_date(m.start_date),
                    self.format_date(m.end_date),
                    f"R$ {float(m.amount):.2f}",
                    "Sim" if m.preventive else "Não",
                    f"{m.mileage_at_service} km",
                    (m.description or "").capitalize()
                ))
        except Exception:
            pass

    def format_date(self, date_val):
        if not date_val: return "-"
        try:
            if isinstance(date_val, str) and "-" in date_val:
                return datetime.strptime(date_val, '%Y-%m-%d').strftime('%d/%m/%Y')
            return date_val.strftime('%d/%m/%Y') if hasattr(date_val, 'strftime') else str(date_val)
        except:
            return str(date_val)

    def adicionar_manutencao(self):
        try:
            from app.interface.vehicle.interface_cadastrar_manutencao import InterfaceAddMaintence
            interface = InterfaceAddMaintence(self.parent, self.db_path, self.vehicle_id)
            interface.show()
        except Exception as e:
            messagebox.showerror("Erro de sistema",
                "Não foi possível abrir a tela.\n\n"
                f"Erro técnico: {str(e)}")

    def excluir_manutencao(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma manutenção.")
            return

        if messagebox.askyesno("Confirmar", "Deseja excluir este registro?"):
            if self.maintenance_repo.delete(int(selected[0])):
                self.load_maintenances()

    def baixar_comprovante(self):
        selected = self.tree.selection()
        if not selected: return

        m = self.maintenance_repo.get_by_id(int(selected[0]))
        if not m or not m.receipt:
            messagebox.showinfo("Informação", "Sem comprovante anexado.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=f"Comprovante_Manutencao_{selected[0]}",
            title="Salvar comprovante"
        )

        if path:
            with open(path, "wb") as f:
                f.write(m.receipt)
            messagebox.showinfo("Sucesso", "Arquivo salvo com sucesso!")

    def back(self):
        from app.interface.vehicle.interface_veiculo import InterfaceListVehicles
        InterfaceListVehicles(self.parent, self.db_path).show()