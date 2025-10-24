import tkinter as tk
from tkinter import ttk
from datetime import datetime
from calendar import monthrange

class CustomCalendar(tk.Toplevel):
    def __init__(self, parent, callback=None, initial_date=None):
        super().__init__(parent)
        self.callback = callback
        self.selected_date = initial_date or datetime.today().date()
        self.current_year = self.selected_date.year
        self.current_month = self.selected_date.month

        self.title("Selecionar Data")
        self.geometry("520x650")
        self.configure(bg="#1c1c1e")
        self.resizable(False, False)

        self.bg_main = "#1c1c1e"
        self.bg_button = "#3a3f47"
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"
        self.hover_bg = "#5a5f67"
        self.selected_bg = "#ff5722"
        self.weekday_bg = "#2a2a2a"

        self.font_title = ("Segoe UI", 18, "bold")
        self.font_label = ("Segoe UI", 12)
        self.font_button = ("Segoe UI", 10)

        self._build_ui()

    def _build_ui(self):
        title_frame = tk.Frame(self, bg=self.bg_main)
        title_frame.pack(pady=10)
        tk.Label(title_frame, text="Calendario", font=self.font_title, bg=self.bg_main, fg=self.accent).pack(side="left", padx=5)
        tk.Label(title_frame, text="Selecionar Data", font=self.font_title, bg=self.bg_main, fg=self.accent).pack(side="left")

        select_frame = tk.Frame(self, bg=self.bg_main, relief="ridge", bd=3, padx=15, pady=10)
        select_frame.pack(pady=5, padx=20, fill="x")

        tk.Label(select_frame, text="Mes:", font=self.font_label, bg=self.bg_main, fg=self.fg_text).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.month_combo = ttk.Combobox(select_frame, values=["Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho",
                                                              "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"],
                                        state="readonly", font=self.font_label, width=12)
        self.month_combo.current(self.current_month - 1)
        self.month_combo.bind("<<ComboboxSelected>>", self._change_month)
        self.month_combo.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(select_frame, text="Ano:", font=self.font_label, bg=self.bg_main, fg=self.fg_text).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.year_combo = ttk.Combobox(select_frame, values=[str(y) for y in range(1900, 2101)], state="readonly", font=self.font_label, width=8)
        self.year_combo.set(str(self.current_year))
        self.year_combo.bind("<<ComboboxSelected>>", self._change_year)
        self.year_combo.grid(row=0, column=3, padx=5, pady=5)

        nav_frame = tk.Frame(self, bg=self.bg_main)
        nav_frame.pack(pady=5)
        tk.Button(nav_frame, text="<", font=("Segoe UI", 16), bg=self.bg_button, fg=self.fg_text,
                  command=self._prev_month, relief="flat", width=4, height=1).pack(side="left", padx=15)
        tk.Button(nav_frame, text=">", font=("Segoe UI", 16), bg=self.bg_button, fg=self.fg_text,
                  command=self._next_month, relief="flat", width=4, height=1).pack(side="right", padx=15)

        days_frame = tk.Frame(self, bg=self.bg_main, relief="ridge", bd=2)
        days_frame.pack(pady=3, padx=20, fill="x")

        self.days_frame = tk.Frame(self, bg=self.bg_main, relief="ridge", bd=2)
        self.days_frame.pack(pady=3, padx=20, fill="y")
        self._populate_days()

        ok_frame = tk.Frame(self, bg=self.bg_main)
        ok_frame.pack(pady=15)
        tk.Button(ok_frame, text="Salvar", font=self.font_button, bg=self.accent, fg=self.fg_text,
                  command=self._confirm, relief="raised", bd=4, width=14, height=2).pack()

    def _change_month(self, event):
        month_names = ["Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho",
                       "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.current_month = month_names.index(self.month_combo.get()) + 1
        self._populate_days()

    def _change_year(self, event):
        self.current_year = int(self.year_combo.get())
        self._populate_days()

    def _prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self._update_combos()
        self._populate_days()

    def _next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self._update_combos()
        self._populate_days()

    def _update_combos(self):
        month_names = ["Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho",
                       "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.month_combo.current(self.current_month - 1)
        self.year_combo.set(str(self.current_year))

    def _populate_days(self):
        for widget in self.days_frame.winfo_children():
            widget.destroy()

        _, num_days = monthrange(self.current_year, self.current_month)
        first_weekday = datetime(self.current_year, self.current_month, 1).weekday()
        first_weekday = (first_weekday + 1) % 7

        for row in range(6):
            for col in range(7):
                day_num = row * 7 + col - first_weekday + 1
                if 1 <= day_num <= num_days:
                    btn = tk.Button(self.days_frame, text=str(day_num), font=self.font_button, bg=self.bg_button, fg=self.fg_text,
                                    relief="flat", width=8, height=2, command=lambda d=day_num: self._select_day(d))
                    btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.hover_bg))
                    btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.selected_bg if datetime(self.current_year, self.current_month, int(b['text'])).date() == self.selected_date else self.bg_button))
                    if datetime(self.current_year, self.current_month, day_num).date() == self.selected_date:
                        btn.config(bg=self.selected_bg)
                    btn.grid(row=row, column=col, padx=1, pady=1, sticky="nsew")
                else:
                    tk.Label(self.days_frame, text="", width=8, height=2, bg=self.bg_main).grid(row=row, column=col, padx=1, pady=1, sticky="nsew")

    def _select_day(self, day):
        self.selected_date = datetime(self.current_year, self.current_month, day).date()
        self._populate_days()

    def _confirm(self):
        if self.callback:
            self.callback(self.selected_date)
        self.destroy()
