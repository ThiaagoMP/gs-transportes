import tkinter as tk
from tkinter import ttk, messagebox
from app.repositories.trip_repository import TripRepository
from app.models.trip import Trip
from app.components.list_rounded_button import ListRoundedButton

class InterfaceViagem:
    def __init__(self, parent, db_path):
        self.parent = parent
        self.db_path = db_path
        self.trip_repo = TripRepository(self.db_path)

        self.bg_main = "#1c1c1e"
        self.bg_button = "#3a3f47"
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        self.parent.configure(bg=self.bg_main)

        tk.Label(self.parent, text="Lista de Viagens", font=("Segoe UI", 26, "bold"), bg=self.bg_main, fg=self.accent).pack(pady=(20, 10), padx=25, fill="x")

        main_frame = tk.Frame(self.parent, bg=self.bg_main)
        main_frame.pack(padx=30, pady=10, fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", font=("Segoe UI", 12), background=self.bg_main, fieldbackground=self.bg_main, foreground=self.fg_text)
        style.configure("Treeview.Heading", font=("Segoe UI", 13, "bold"), background=self.accent, foreground="#ffffff")
        style.map("Treeview", background=[("selected", "#333333")], foreground=[("selected", "#ffffff")])

        self.tree = ttk.Treeview(main_frame, columns=("Veículo", "Despesas (R$)", "Quilometragem (km)", "Valor por Passageiro (R$)", "Passageiros", "Data de Início", "Data de Fim"), show="headings", height=15)

        col_defs = [
            ("Veículo", 150),
            ("Despesas (R$)", 120),
            ("Quilometragem (km)", 150),
            ("Valor por Passageiro (R$)", 150),
            ("Passageiros", 150),
            ("Data de Início", 120),
            ("Data de Fim", 120),
        ]

        for col, width in col_defs:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)

        self.tree.pack(fill="both", expand=True, pady=10)
        self.tree.bind("<Double-1>", self.on_double_click)

        button_frame = tk.Frame(main_frame, bg=self.bg_main)
        button_frame.pack(pady=10)

        actions = [
            ("Cadastrar Viagem", self.cadastrar_viagem),
            ("Editar Viagem", self.editar_viagem),
            ("Excluir Viagem", self.confirm_delete),
        ]

        for text, cmd in actions:
            bg_color = "#f44336" if text.startswith("Excluir") else self.bg_button
            btn = ListRoundedButton(
                button_frame,
                text=text,
                command=cmd,
                width=210,
                height=50,
                bg=bg_color,
                fg=self.fg_text,
                hover_bg=self.accent,
                font=("Segoe UI", 11, "bold"))
            btn.pack(side="left", padx=10, pady=6)

        self.load_trips()

    def load_trips(self):
        self.tree.delete(*self.tree.get_children())
        trips = self.trip_repo.get_all()
        for trip in trips:
            trip_id = getattr(trip, 'trip_id', None)
            if trip_id is None or not str(trip_id).strip():
                continue

            self.tree.insert("", "end", iid=str(trip_id), values=(
                getattr(trip, 'vehicle_id', ''),
                f"{float(getattr(trip, 'additional_expenses', 0.0)):.2f}" if getattr(trip, 'additional_expenses', None) is not None else '0.00',
                getattr(trip, 'total_km', ''),
                f"{float(getattr(trip, 'passenger_fare', 0.0)):.2f}" if getattr(trip, 'passenger_fare', None) is not None else '0.00',
                getattr(trip, 'passenger_count', ''),
                getattr(trip, 'start_date', ''),
                getattr(trip, 'end_date', '')
            ))

    def on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            try:
                trip_id = int(item)
                from app.interface.trip.interface_editar_viagem import InterfaceEditarViagem
                interface = InterfaceEditarViagem(self.parent, self.db_path, trip_id)
                interface.show()
            except ValueError:
                messagebox.showerror("Erro", "ID da viagem inválido.")

    def cadastrar_viagem(self):
        try:
            from app.interface.trip.interface_cadastrar_viagem import InterfaceCadastrarViagem
            interface = InterfaceCadastrarViagem(self.parent, self.db_path)
            interface.show()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir o cadastro: {str(e)}")

    def confirm_delete(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione uma viagem para excluir.")
            return

        trip_id = selected_item[0]
        if not trip_id.strip():
            messagebox.showerror("Erro", "ID da viagem inválido.")
            return

        try:
            trip_id = int(trip_id)
        except ValueError:
            messagebox.showerror("Erro", "ID da viagem inválido (não é um número).")
            return

        if messagebox.askyesno("Confirmação", f"Deseja realmente excluir a viagem com ID {trip_id}?"):
            if self.trip_repo.delete(trip_id):
                messagebox.showinfo("Sucesso", f"Viagem com ID {trip_id} excluída com sucesso!")
                self.load_trips()
            else:
                messagebox.showerror("Erro", "Falha ao excluir a viagem.")

    def editar_viagem(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione uma viagem para editar.")
            return
        try:
            trip_id = int(selected_item[0])
            from app.interface.trip.interface_editar_viagem import InterfaceEditarViagem
            interface = InterfaceEditarViagem(self.parent, self.db_path, trip_id)
            interface.show()
        except ValueError:
            messagebox.showerror("Erro", "ID da viagem inválido.")