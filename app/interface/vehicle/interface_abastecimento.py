import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

from app.components.list_rounded_button import ListRoundedButton
from app.repositories.refueling_repository import RefuelingRepository


class InterfaceFueling:
    def __init__(self, parent, db_path, vehicle_id, vehicle_name):
        self.parent = parent
        self.db_path = db_path
        self.vehicle_id = vehicle_id
        self.vehicle_name = vehicle_name
        self.refueling_repo = RefuelingRepository(self.db_path)

        self.bg_main = "#1c1c1e"
        self.bg_secondary = "#2c2c2e"
        self.bg_button = "#3a3f47"
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        self.parent.configure(bg=self.bg_main)

        header_frame = tk.Frame(self.parent, bg=self.bg_main)
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        tk.Label(
            header_frame,
            text=f"Abastecimentos: {self.vehicle_name.title()}",
            font=("Segoe UI", 16, "bold"),
            bg=self.bg_main,
            fg=self.accent
        ).pack(side="left")

        content_frame = tk.Frame(self.parent, bg=self.bg_secondary)
        content_frame.pack(fill="both", expand=True, padx=20, pady=5)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        font=("Segoe UI", 10),
                        rowheight=30,
                        background=self.bg_secondary,
                        fieldbackground=self.bg_secondary,
                        foreground=self.fg_text,
                        borderwidth=0)
        style.configure("Treeview.Heading",
                        font=("Segoe UI", 10, "bold"),
                        background=self.accent,
                        foreground=self.fg_text,
                        borderwidth=1)
        style.map("Treeview",
                  background=[("selected", self.accent)],
                  foreground=[("selected", "#ffffff")])

        tree_container = tk.Frame(content_frame, bg=self.bg_secondary)
        tree_container.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            tree_container,
            columns=("Data", "Total", "Litros", "KM", "Posto", "Tipo", "Desc"),
            show="headings",
            selectmode="browse"
        )

        headers = {
            "Data": ("Data", 90),
            "Total": ("Valor", 90),
            "Litros": ("Litros", 80),
            "KM": ("KM", 90),
            "Posto": ("Posto", 150),
            "Tipo": ("Tipo", 110),
            "Desc": ("Descrição", 180)
        }

        for col, (text, width) in headers.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="center" if col != "Desc" else "w")

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        actions_frame = tk.Frame(self.parent, bg=self.bg_main)
        actions_frame.pack(fill="x", side="bottom", pady=20)

        buttons_container = tk.Frame(actions_frame, bg=self.bg_main)
        buttons_container.pack(expand=True)

        btn_config = [
            ("Novo", self.adicionar_abastecimento, self.accent, 120),
            ("Comprovante", self.baixar_comprovante, self.bg_button, 140),
            ("Excluir", self.excluir_abastecimento, "#b00020", 120),
            ("Voltar", self.back, self.bg_button, 120)
        ]

        for text, cmd, color, width in btn_config:
            ListRoundedButton(
                buttons_container,
                text=text,
                command=cmd,
                width=width,
                height=38,
                bg=color,
                fg=self.fg_text
            ).pack(side="left", padx=10)

        self.load_refuelings()

    def load_refuelings(self):
        self.tree.delete(*self.tree.get_children())
        try:
            refuelings = self.refueling_repo.get_all_by_vehicle_id(self.vehicle_id)
            refuelings.sort(key=lambda x: str(x.refueling_date), reverse=True)

            for ref in refuelings:
                date_val = ref.refueling_date
                if isinstance(date_val, str):
                    try:
                        date_val = datetime.strptime(date_val, '%Y-%m-%d').strftime('%d/%m/%Y')
                    except:
                        pass
                elif hasattr(date_val, 'strftime'):
                    date_val = date_val.strftime('%d/%m/%Y')

                total = float(ref.price_per_liter) * float(ref.liters)

                self.tree.insert("", "end", iid=str(ref.refueling_id), values=(
                    date_val,
                    f"R$ {total:.2f}",
                    f"{ref.liters}L",
                    f"{ref.km_traveled}",
                    (ref.fuel_station or "-").title(),
                    ref.fuel_type.capitalize(),
                    (ref.description or "").capitalize()
                ))
        except Exception:
            pass

    def adicionar_abastecimento(self):
        from app.interface.vehicle.interface_cadastrar_abastecimento import InterfaceAddRefueling
        InterfaceAddRefueling(self.parent, self.db_path, self.vehicle_id).show()

    def excluir_abastecimento(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um registro.")
            return

        if messagebox.askyesno("Confirmar", "Deseja excluir este registro?"):
            if self.refueling_repo.delete(int(selected[0])):
                self.load_refuelings()
                messagebox.showinfo("Sucesso", "Registro removido com sucesso.")

    def baixar_comprovante(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um registro.")
            return

        ref = self.refueling_repo.get_by_id(int(selected[0]))
        if not ref or not ref.receipt:
            messagebox.showinfo("Informação", "Sem comprovante anexo.")
            return

        ext = ".pdf" if ref.receipt.startswith(b"%PDF") else ".jpg"

        path = filedialog.asksaveasfilename(
            defaultextension=ext,
            initialfile=f"Comprovante_{self.vehicle_id}_{selected[0]}",
            title="Salvar comprovante"
        )

        if path:
            try:
                with open(path, "wb") as f:
                    f.write(ref.receipt)
                messagebox.showinfo("Sucesso", "Arquivo salvo com sucesso.")
            except Exception:
                messagebox.showerror("Erro", "Falha ao salvar o arquivo.")

    def back(self):
        from app.interface.vehicle.interface_veiculo import InterfaceListVehicles
        InterfaceListVehicles(self.parent, self.db_path).show()

