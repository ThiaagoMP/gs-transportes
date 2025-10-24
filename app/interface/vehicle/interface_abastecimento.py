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
        self.bg_button = "#3a3f47"
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        self.parent.configure(bg=self.bg_main)

        tk.Label(
            self.parent,
            text=f"Abastecimentos de {self.vehicle_name}",
            font=("Segoe UI", 24, "bold"),
            bg=self.bg_main,
            fg=self.accent,
            anchor="w"
        ).pack(pady=(20, 10), padx=25, fill="x")

        main_frame = tk.Frame(self.parent, bg=self.bg_main)
        main_frame.pack(padx=30, pady=10, fill="both", expand=True)

        list_frame = tk.Frame(main_frame, bg=self.bg_main)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        font=("Segoe UI", 12),
                        background=self.bg_main,
                        fieldbackground=self.bg_main,
                        foreground=self.fg_text)
        style.configure("Treeview.Heading",
                        font=("Segoe UI", 13, "bold"),
                        background=self.accent,
                        foreground="#ffffff")
        style.map("Treeview",
                  background=[("selected", "#333333")],
                  foreground=[("selected", "#ffffff")])

        self.tree = ttk.Treeview(
            list_frame,
            columns=("Data", "Valor Total", "Litros", "Quilometragem", "Posto", "Combustível", "Descrição"),
            show="headings",
            height=15
        )

        col_defs = [
            ("Data", 150, False),
            ("Valor Total", 150, False),
            ("Litros", 150, False),
            ("Quilometragem", 150, False),
            ("Posto", 150, False),
            ("Combustível", 150, False),
            ("Descrição", 150, True),
        ]

        for col, width, stretch in col_defs:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, stretch=stretch)

        self.tree.pack(fill="both", expand=True, pady=10)

        button_frame = tk.Frame(list_frame, bg=self.bg_main)
        button_frame.pack(pady=10)

        actions = [
            ("Adicionar Abastecimento", self.adicionar_abastecimento),
            ("Baixar Comprovante", self.baixar_comprovante),
            ("Voltar", self.back),
            ("Excluir Abastecimento", self.excluir_abastecimento)
        ]

        for text, cmd in actions:
            bg_color = "#f44336" if text.startswith("Excluir") else self.bg_button
            btn = ListRoundedButton(
                button_frame,
                text=text,
                command=cmd,
                width=200,
                height=45,
                bg=bg_color,
                fg=self.fg_text,
                hover_bg=self.accent,
                font=("Segoe UI", 11, "bold"),
                shadow=True
            )
            btn.pack(side="left", padx=10, pady=6)

        self.load_refuelings()

    def load_refuelings(self):
        self.tree.delete(*self.tree.get_children())
        vehicle_refuelings = self.refueling_repo.get_all_by_vehicle_id(self.vehicle_id)

        def sort_key(r):
            try:
                if isinstance(r.refueling_date, str):
                    return datetime.strptime(r.refueling_date, '%Y-%m-%d')
                elif isinstance(r.refueling_date, datetime):
                    return r.refueling_date
                else:
                    return datetime.min
            except:
                return datetime.min

        vehicle_refuelings.sort(key=sort_key, reverse=True)

        for refueling in vehicle_refuelings:
            date_display = refueling.refueling_date.strftime('%d/%m/%Y') if isinstance(refueling.refueling_date, datetime) else str(refueling.refueling_date)

            total_value = refueling.price_per_liter * refueling.liters

            self.tree.insert("", "end", iid=str(refueling.refueling_id), values=(
                date_display,
                f"{total_value:.2f}",
                f"{refueling.liters}",
                f"{refueling.km_traveled:.0f}",
                refueling.fuel_station,
                refueling.fuel_type,
                refueling.description or ""
            ))

    def adicionar_abastecimento(self):
        try:
            from app.interface.vehicle.interface_cadastrar_abastecimento import InterfaceAddRefueling
            interface = InterfaceAddRefueling(self.parent, self.db_path, self.vehicle_id)
            interface.show()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar abastecimento: {str(e)}")

    def excluir_abastecimento(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um abastecimento para excluir.")
            return

        refueling_id = int(selected_item[0])
        if messagebox.askyesno("Confirmação", "Deseja realmente excluir este abastecimento?"):
            try:
                if self.refueling_repo.delete(refueling_id):
                    messagebox.showinfo("Sucesso", "Abastecimento excluído com sucesso!")
                    self.load_refuelings()
                else:
                    messagebox.showerror("Erro", "Falha ao excluir o abastecimento.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir abastecimento: {str(e)}")

    def baixar_comprovante(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um abastecimento para baixar o comprovante.")
            return

        refueling_id = int(selected_item[0])
        refueling = self.refueling_repo.get_by_id(refueling_id)

        if not refueling or not refueling.receipt:
            messagebox.showinfo("Info", "Não há comprovante para este abastecimento.")
            return

        receipt_bytes = refueling.receipt

        if receipt_bytes[:4] == b"%PDF":
            ext = ".pdf"
        elif receipt_bytes[:2] == b"\xff\xd8":
            ext = ".jpg"
        elif receipt_bytes[:8] == b"\x89PNG\r\n\x1a\n":
            ext = ".png"
        else:
            ext = ".bin"

        nome_sanitizado = "".join(c for c in self.vehicle_name if c.isalnum() or c in (' ', '_')).replace(" ", "_")
        data_str = refueling.refueling_date.strftime("%d%m%Y") if hasattr(refueling.refueling_date, "strftime") else str(
            refueling.refueling_date)
        initial_filename = f"comprovante_{nome_sanitizado}_{data_str}{ext}"

        file_path = filedialog.asksaveasfilename(
            defaultextension=ext,
            filetypes=[("PDF", "*.pdf"), ("PNG", "*.png"), ("JPEG", "*.jpg")],
            initialfile=initial_filename,
            title="Salvar Comprovante"
        )

        if not file_path:
            return

        try:
            with open(file_path, "wb") as f:
                f.write(receipt_bytes)
            messagebox.showinfo("Sucesso", f"Comprovante salvo em:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível salvar o arquivo: {str(e)}")

    def back(self):
        from app.interface.vehicle.interface_veiculo import InterfaceListVehicles
        interface = InterfaceListVehicles(self.parent, self.db_path)
        interface.show()
