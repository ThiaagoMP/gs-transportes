import tkinter as tk
from tkinter import ttk
import os
from app.interface.driver.interface_motorista import InterfaceMotorista
from app.interface.vehicle.interface_veiculo import InterfaceVeiculo
from app.interface.student.interface_aluno import InterfaceAluno
from app.interface.interface_linha import InterfaceLinha
from app.interface.interface_viagem import InterfaceViagem
from app.interface.driver.interface_visualizar_editar_motorista import InterfaceVisualizarEditar  # Nova interface para visualizar/editar

class Interface:
    def __init__(self, root):
        self.root = root
        self.root.title("GS-Transportes")

        # Maximizar a janela de forma multiplataforma
        try:
            self.root.wm_attributes('-zoomed', 1)  # Tenta maximizar no Linux/Windows
        except tk.TclError:
            # Fallback: definir geometria para as dimensões da tela
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            self.root.geometry(f"{screen_width}x{screen_height}+0+0")

        # Caminho do banco de dados
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.parent_dir = os.path.dirname(os.path.dirname(self.base_dir))
        self.db_path = os.path.join(self.parent_dir, 'database', 'data', 'gs_transportes.db')

        # Estilo moderno
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Sidebar.TButton", font=("Arial", 14, "bold"), padding=25, background="#2196f3",
                             foreground="#ffffff", borderwidth=0)
        self.style.map("Sidebar.TButton",
                       background=[("active", "#1976d2")],
                       foreground=[("active", "#ffffff")])
        self.style.configure("Header.TLabel", font=("Arial", 20, "bold"), foreground="#01579b", background="#f5f5f5")
        self.style.configure("Action.TButton", font=("Arial", 15, "bold"), padding=20, background="#4CAF50",
                             foreground="#ffffff", borderwidth=0)
        self.style.map("Action.TButton",
                       background=[("active", "#45a049")],
                       foreground=[("active", "#ffffff")])

        # Criar o layout principal
        self.create_layout()

    def create_layout(self):
        # Cabeçalho
        header_frame = tk.Frame(self.root, bg="#f5f5f5", height=60)
        header_frame.pack(fill="x", padx=10, pady=10)
        ttk.Label(
            header_frame,
            text="GS-Transportes",
            style="Header.TLabel"
        ).pack()

        # Painel lateral esquerdo para os botões
        self.sidebar_left = tk.Frame(self.root, width=200, bg="#f5f5f5", relief="flat")
        self.sidebar_left.pack(side="left", fill="y", padx=5, pady=5)

        # Painel principal para conteúdo
        self.main_content = tk.Frame(self.root, bg="#ffffff", relief="raised", borderwidth=1, padx=20, pady=20)
        self.main_content.pack(side="left", fill="both", expand=True)

        # Painel lateral direito vazio com borda
        self.sidebar_right = tk.Frame(self.root, width=200, bg="#f5f5f5", relief="raised", borderwidth=1)
        self.sidebar_right.pack(side="right", fill="y", padx=5, pady=5)

        # Botões no painel lateral esquerdo
        buttons = [
            ("Motorista", self.show_view_edit_motorista),
            ("Veículos", lambda: self.show_section(InterfaceVeiculo(self.main_content, self.db_path))),
            ("Alunos", lambda: self.show_section(InterfaceAluno(self.main_content, self.db_path))),
            ("Linhas", lambda: self.show_section(InterfaceLinha(self.main_content, self.db_path))),
            ("Viagens", lambda: self.show_section(InterfaceViagem(self.main_content, self.db_path)))
        ]

        for text, command in buttons:
            btn = ttk.Button(
                self.sidebar_left,
                text=text,
                style="Sidebar.TButton",
                command=command
            )
            btn.pack(fill="x", padx=10, pady=5)

        # Mensagem inicial no painel principal
        self.content_label = tk.Label(
            self.main_content,
            text="Bem-vindo ao GS-Transportes!\nSelecione uma opção no menu à esquerda.",
            font=("Arial", 16),
            bg="#ffffff",
            fg="#333333"
        )
        self.content_label.pack(pady=20)

    def show_driver_options(self):
        # Limpar o conteúdo atual do painel principal
        for widget in self.main_content.winfo_children():
            widget.destroy()

        # Frame para os botões de ação, alinhado no centro
        action_frame = tk.Frame(self.main_content, bg="#ffffff")
        action_frame.pack(expand=True)

        # Botão Cadastrar
        ttk.Button(
            action_frame,
            text="Cadastrar",
            style="Action.TButton",
            command=lambda: self.show_section(InterfaceMotorista(self.main_content, self.db_path))
        ).pack(expand=True, pady=15)

        # Botão Visualizar/Editar
        ttk.Button(
            action_frame,
            text="Visualizar/Editar",
            style="Action.TButton",
            command=self.show_view_edit_motorista
        ).pack(expand=True, pady=15)

    def show_view_edit_motorista(self):
        # Limpar o conteúdo atual do painel principal
        for widget in self.main_content.winfo_children():
            widget.destroy()

        try:
            # Exibir lista de motoristas para seleção e edição
            interface = InterfaceVisualizarEditar(self.main_content, self.db_path)
            interface.show()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir a interface de visualização/editar: {str(e)}")

    def show_section(self, section):
        # Limpar o conteúdo atual do painel principal
        for widget in self.main_content.winfo_children():
            widget.destroy()
        # Mostrar a nova seção
        section.show()

def main():
    root = tk.Tk()
    app = Interface(root)
    root.mainloop()

if __name__ == "__main__":
    main()