import tkinter as tk
import os

from app.interface.driver.interface_list_drivers import InterfaceListDrivers
from app.interface.trip.interface_viagens import InterfaceViagem
from app.interface.vehicle.interface_veiculo import InterfaceListVehicles
from app.interface.student.interface_aluno import InterfaceAluno
from app.interface.route.interface_linha import InterfaceLinha
from app.interface.report.interface_report import InterfaceRelatorio


class RoundedButton(tk.Canvas):
    def __init__(
        self,
        parent,
        text,
        command=None,
        width=200,
        height=44,
        bg="#2a2a2d",
        fg="#d1d1d1",
        hover_bg="#ff7f32",
        font=("Segoe UI", 13, "bold")
    ):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=parent["bg"],
            highlightthickness=0
        )

        self.command = command
        self.bg = bg
        self.hover_bg = hover_bg

        self.rect = self.create_round_rect(
            2, 2, width - 2, height - 2, 12, fill=bg, outline=""
        )
        self.text_id = self.create_text(
            width // 2,
            height // 2,
            text=text,
            fill=fg,
            font=font
        )

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)

    def create_round_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def on_enter(self, _):
        self.itemconfig(self.rect, fill=self.hover_bg)

    def on_leave(self, _):
        self.itemconfig(self.rect, fill=self.bg)

    def on_click(self, _):
        if self.command:
            self.command()


class InterfacePrincipal:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("GS Transportes")
        self.root.state("zoomed")
        self.root.configure(bg="#1c1c1e")

        self.db_path = os.path.join(
            os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
            "GS-Transportes",
            "gs_transportes.db"
        )

        self.bg_main = "#1c1c1e"
        self.bg_sidebar = "#2a2a2d"
        self.accent = "#ff7f32"
        self.text_secondary = "#d1d1d1"

        self.build_layout()

    def build_layout(self):
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.header = tk.Frame(self.root, bg=self.bg_sidebar, height=80)
        self.header.grid(row=0, column=0, columnspan=2, sticky="nsew")

        self.title_label = tk.Label(
            self.header,
            text="GS Transportes",
            font=("Segoe UI", 26, "bold"),
            fg=self.accent,
            bg=self.bg_sidebar
        )
        self.title_label.pack(pady=20)

        self.sidebar = tk.Frame(self.root, bg=self.bg_sidebar, width=260)
        self.sidebar.grid(row=1, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        self.root.grid_columnconfigure(0, minsize=260)

        self.main_content = tk.Frame(self.root, bg=self.bg_main)
        self.main_content.grid(row=1, column=1, sticky="nsew", padx=24, pady=24)

        menu = [
            ("Motoristas", lambda: self.show_section(InterfaceListDrivers)),
            ("Veículos", lambda: self.show_section(InterfaceListVehicles)),
            ("Alunos", lambda: self.show_section(InterfaceAluno)),
            ("Linhas", lambda: self.show_section(InterfaceLinha)),
            ("Viagens", lambda: self.show_section(InterfaceViagem)),
            ("Relatórios", self.abrir_relatorios),
        ]

        for text, action in menu:
            btn = RoundedButton(
                self.sidebar,
                text=text,
                command=action,
                bg=self.bg_sidebar,
                hover_bg=self.accent
            )
            btn.pack(pady=10, padx=20, fill="x")

        self.welcome_label = tk.Label(
            self.main_content,
            text="Bem-vindo ao GS Transportes\nSelecione uma opção no menu",
            font=("Segoe UI", 22, "bold"),
            bg=self.bg_main,
            fg=self.text_secondary,
            justify="center"
        )
        self.welcome_label.place(relx=0.5, rely=0.5, anchor="center")

    def clear_main(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

    def show_section(self, section_cls):
        self.clear_main()
        section_cls(self.main_content, self.db_path).show()

    def abrir_relatorios(self):
        self.clear_main()
        InterfaceRelatorio(self.main_content, self.db_path).show()


def main():
    root = tk.Tk()
    InterfacePrincipal(root)
    root.mainloop()


if __name__ == "__main__":
    main()
