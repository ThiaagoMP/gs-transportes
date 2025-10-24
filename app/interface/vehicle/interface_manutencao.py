import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os
from app.components.list_rounded_button import ListRoundedButton
from app.interface.vehicle.interface_cadastrar_manutencao import InterfaceAddMaintence
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

        tk.Label(
            self.parent,
            text=f"Manutenções de {self.vehicle_name}",
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
            columns=("Data Início", "Data Fim", "Valor", "Preventiva", "Quilometragem", "Descrição"),
            show="headings",
            height=15
        )

        col_defs = [
            ("Data Início", 150, False),
            ("Data Fim", 150, False),
            ("Valor", 150, False),
            ("Preventiva", 150, False),
            ("Quilometragem", 150, False),
            ("Descrição", 200, True),
        ]

        for col, width, stretch in col_defs:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, stretch=stretch)

        self.tree.pack(fill="both", expand=True, pady=10)

        button_frame = tk.Frame(list_frame, bg=self.bg_main)
        button_frame.pack(pady=10)

        actions = [
            ("Adicionar Manutenção", self.adicionar_manutencao),
            ("Baixar Comprovante", self.baixar_comprovante),
            ("Voltar", self.back),
            ("Excluir Manutenção", self.excluir_manutencao)
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

        self.load_maintenances()

    def load_maintenances(self):
        self.tree.delete(*self.tree.get_children())
        all_maintenances = self.maintenance_repo.get_all()
        vehicle_maintenances = [m for m in all_maintenances if m.vehicle_id == self.vehicle_id]

        vehicle_maintenances.sort(key=lambda m: m.start_date, reverse=True)

        for maintenance in vehicle_maintenances:
            start_date_display = maintenance.start_date.strftime('%d/%m/%Y') if isinstance(maintenance.start_date, datetime) else str(maintenance.start_date)
            end_date_display = maintenance.end_date.strftime('%d/%m/%Y') if isinstance(maintenance.end_date, datetime) else str(maintenance.end_date)

            self.tree.insert("", "end", iid=str(maintenance.maintenance_id), values=(
                start_date_display,
                end_date_display,
                f"{maintenance.amount:.2f}",
                "Sim" if maintenance.preventive else "Não",
                f"{maintenance.mileage_at_service:.0f}",
                maintenance.description or ""
            ))

    def adicionar_manutencao(self):
        try:
            interface = InterfaceAddMaintence(self.parent, self.db_path, self.vehicle_id)
            interface.show()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar manutenção: {str(e)}")

    def excluir_manutencao(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione uma manutenção para excluir.")
            return

        maintenance_id = int(selected_item[0])
        if messagebox.askyesno("Confirmação", "Deseja realmente excluir esta manutenção?"):
            try:
                if self.maintenance_repo.delete(maintenance_id):
                    messagebox.showinfo("Sucesso", "Manutenção excluída com sucesso!")
                    self.load_maintenances()
                else:
                    messagebox.showerror("Erro", "Falha ao excluir a manutenção.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir manutenção: {str(e)}")

    def baixar_comprovante(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione uma manutenção para baixar o comprovante.")
            return

        maintenance_id = int(selected_item[0])
        maintenance = self.maintenance_repo.get_by_id(maintenance_id)

        if not maintenance or not maintenance.receipt:
            messagebox.showinfo("Info", "Não há comprovante para esta manutenção.")
            return

        receipt_bytes = maintenance.receipt

        if receipt_bytes[:4] == b"%PDF":
            ext = ".pdf"
        elif receipt_bytes[:2] == b"\xff\xd8":
            ext = ".jpg"
        elif receipt_bytes[:8] == b"\x89PNG\r\n\x1a\n":
            ext = ".png"
        else:
            ext = ".bin"

        nome_sanitizado = "".join(c for c in self.vehicle_name if c.isalnum() or c in (' ', '_')).replace(" ", "_")
        data_str = maintenance.start_date.strftime("%d%m%Y") if hasattr(maintenance.start_date, "strftime") else str(
            maintenance.start_date)
        initial_filename = f"comprovante_{nome_sanitizado}_{data_str}{ext}"

        file_path = filedialog.asksaveasfilename(
            defaultextension=ext,
            filetypes=[("PDF", "*.pdf"), ("JPEG", "*.jpg"), ("PNG", "*.png")],
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
