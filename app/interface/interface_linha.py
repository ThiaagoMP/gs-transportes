import tkinter as tk
from tkinter import ttk


class InterfaceLinha:
    def __init__(self, parent, db_path):
        self.parent = parent
        self.db_path = db_path

    def show(self):
        # Limpar o conteúdo atual do painel principal
        for widget in self.parent.winfo_children():
            widget.destroy()

        # Título da seção
        tk.Label(
            self.parent,
            text="Gerenciar Linhas",
            font=("Arial", 14, "bold"),
            bg="#ffffff"
        ).pack(pady=10)

        tk.Label(
            self.parent,
            text="Aqui você pode cadastrar, editar ou visualizar linhas.",
            font=("Arial", 12),
            bg="#ffffff"
        ).pack(pady=5)