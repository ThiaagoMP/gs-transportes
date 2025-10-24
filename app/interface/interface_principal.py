import tkinter as tk
from tkinter import messagebox
import os

from app.interface.driver.interface_list_drivers import InterfaceListDrivers
from app.interface.trip.interface_viagens import InterfaceViagem
from app.interface.vehicle.interface_veiculo import InterfaceListVehicles
from app.interface.student.interface_aluno import InterfaceAluno
from app.interface.route.interface_linha import InterfaceLinha
from app.interface.report.interface_report import InterfaceRelatorio


class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=180, height=40,
                 bg="#2a2a2d", fg="#d1d1d1", hover_bg="#ff7f32", font=("Segoe UI", 13, "bold")):
        super().__init__(parent, width=width, height=height, highlightthickness=0, bg=parent["bg"])
        self.command = command
        self.bg = bg
        self.fg = fg
        self.hover_bg = hover_bg
        self.font = font
        self.text = text
        self.rect = self.create_round_rect(2, 2, width-2, height-2, radius=12, fill=self.bg)
        self.label = self.create_text(width//2, height//2, text=self.text, fill=self.fg, font=self.font)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.tag_bind(self.rect, "<Enter>", self.on_enter)
        self.tag_bind(self.rect, "<Leave>", self.on_leave)
        self.tag_bind(self.rect, "<Button-1>", self.on_click)
        self.tag_bind(self.label, "<Enter>", self.on_enter)
        self.tag_bind(self.label, "<Leave>", self.on_leave)
        self.tag_bind(self.label, "<Button-1>", self.on_click)

    def create_round_rect(self, x1, y1, x2, y2, radius=12, **kwargs):
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1, x2, y1+radius,
            x2, y2-radius,
            x2, y2, x2-radius, y2,
            x1+radius, y2,
            x1, y2, x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def on_enter(self, event):
        self.itemconfig(self.rect, fill=self.hover_bg)

    def on_leave(self, event):
        self.itemconfig(self.rect, fill=self.bg)

    def on_click(self, event):
        if self.command:
            self.command()


class InterfacePrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("GS Transportes")
        try:
            self.root.wm_attributes('-zoomed', 1)
        except tk.TclError:
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            self.root.geometry(f"{sw}x{sh}+0+0")
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.parent_dir = os.path.dirname(os.path.dirname(self.base_dir))
        self.db_path = os.path.join(self.parent_dir, 'database', 'data', 'gs_transportes.db')
        self.bg_main = "#1c1c1e"
        self.bg_sidebar = "#2a2a2d"
        self.accent = "#ff7f32"
        self.accent_hover = "#e86b1f"
        self.text_primary = "#ffffff"
        self.text_secondary = "#d1d1d1"
        self.root.configure(bg=self.bg_main)
        self.create_layout()

    def create_layout(self):
        header_frame = tk.Frame(self.root, bg=self.bg_sidebar, height=80)
        header_frame.pack(fill="x")
        tk.Label(header_frame, text="GS Transportes",
                 font=("Segoe UI", 28, "bold"), fg=self.accent, bg=self.bg_sidebar).place(relx=0.5, y=20, anchor="n")

        self.sidebar_left = tk.Frame(self.root, width=220, bg=self.bg_sidebar)
        self.sidebar_left.pack(side="left", fill="y")
        self.sidebar_left.pack_propagate(False)

        self.main_content = tk.Frame(self.root, bg=self.bg_main)
        self.main_content.pack(side="left", fill="both", expand=True, padx=15, pady=10)

        buttons = [
            ("Motorista", lambda: self.show_section(InterfaceListDrivers(self.main_content, self.db_path))),
            ("Veículos", lambda: self.show_section(InterfaceListVehicles(self.main_content, self.db_path))),
            ("Alunos", lambda: self.show_section(InterfaceAluno(self.main_content, self.db_path))),
            ("Linhas", lambda: self.show_section(InterfaceLinha(self.main_content, self.db_path))),
            ("Viagens", lambda: self.show_section(InterfaceViagem(self.main_content, self.db_path))),
            ("Relatórios", self.abrir_relatorios)
        ]

        for text, command in buttons:
            btn = RoundedButton(self.sidebar_left, text=text, command=command,
                                bg=self.bg_sidebar, fg=self.text_secondary,
                                hover_bg=self.accent)
            btn.pack(pady=10, padx=20)

        self.content_label = tk.Label(
            self.main_content,
            text="Bem-vindo ao GS Transportes!\nSelecione uma opção no menu à esquerda.",
            font=("Segoe UI", 22, "bold"),
            bg=self.bg_main,
            fg=self.text_secondary,
            justify="center",
            anchor="center"
        )
        self.content_label.place(relx=0.5, rely=0.45, anchor="center")

    def show_view_edit_motorista(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()
        try:
            interface = InterfaceListDrivers(self.main_content, self.db_path)
            interface.show()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir a interface de visualização/editar: {str(e)}")

    def show_section(self, section):
        for widget in self.main_content.winfo_children():
            widget.destroy()
        section.show()

    def abrir_relatorios(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()
        interface = InterfaceRelatorio(self.main_content, self.db_path)
        interface.show()


def main():
    root = tk.Tk()
    app = InterfacePrincipal(root)
    root.mainloop()


if __name__ == "__main__":
    main()
