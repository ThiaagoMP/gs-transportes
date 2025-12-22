import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from app.components.custom_calendar import CustomCalendar
from app.models.driver import Driver
from app.repositories.driver_repository import DriverRepository
from app.components.list_rounded_button import ListRoundedButton


class InterfaceEditDriver:
    def __init__(self, parent, db_path, driver: Driver):
        self.parent = parent
        self.driver = driver
        self.db_path = db_path
        self.driver_repo = DriverRepository(db_path)

        self.bg_main = "#1c1c1e"
        self.bg_button = "#3a3f47"
        self.bg_field = "#2c2c2e"
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"

        self.font_title = ("Segoe UI", 18, "bold")
        self.font_label = ("Segoe UI", 9, "bold")
        self.font_entry = ("Segoe UI", 10)

        self.fields = {}
        self.date_vars = {}
        self.show()
        self._preencher_dados()

    def show(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

        self.parent.configure(bg=self.bg_main)

        tk.Label(
            self.parent,
            text="Editar cadastro de motorista",
            font=self.font_title,
            bg=self.bg_main,
            fg=self.accent
        ).pack(pady=(15, 10))

        container = tk.Frame(self.parent, bg=self.bg_main)
        container.pack(expand=True, fill="both")

        self.form_frame = tk.Frame(container, bg=self.bg_main)
        self.form_frame.pack(padx=20, pady=5)

        labels = [
            "Nome*", "Salário (R$)*", "Contato*", "Início*", "Término",
            "CPF*", "RG*", "CNH*", "Extras"
        ]

        for idx, label in enumerate(labels):
            tk.Label(
                self.form_frame,
                text=label,
                font=self.font_label,
                bg=self.bg_main,
                fg="#8e8e93",
                anchor="e"
            ).grid(row=idx, column=0, sticky="e", padx=10, pady=4)

            if label == "Extras":
                entry = tk.Text(
                    self.form_frame, width=38, height=3, font=self.font_entry,
                    bg=self.bg_field, fg=self.fg_text, insertbackground=self.fg_text,
                    relief="flat", padx=5, pady=5
                )
                entry.grid(row=idx, column=1, padx=10, pady=8, sticky="w")

            elif label in ["Início*", "Término"]:
                frame = tk.Frame(self.form_frame, bg=self.bg_main)
                frame.grid(row=idx, column=1, padx=10, pady=4, sticky="w")

                self.date_vars[label] = tk.StringVar()
                entry = tk.Label(
                    frame, textvariable=self.date_vars[label], width=22, font=self.font_entry,
                    bg=self.bg_field, fg=self.fg_text, anchor="w", padx=10
                )
                entry.pack(side="left", ipady=5)

                ListRoundedButton(
                    frame, text="Data",
                    width=70, height=30, bg=self.accent if "*" in label else self.bg_button,
                    fg=self.fg_text,
                    command=lambda l=label: self._open_calendar(l)
                ).pack(side="left", padx=5)

                if "*" not in label:
                    ListRoundedButton(
                        frame, text="X",
                        width=35, height=30, bg="#555555", fg=self.fg_text,
                        command=lambda: self.date_vars["Término"].set("")
                    ).pack(side="left")

            else:
                entry = tk.Entry(
                    self.form_frame, font=self.font_entry, width=40,
                    bg=self.bg_field, fg=self.fg_text, insertbackground=self.fg_text,
                    relief="flat", borderwidth=0
                )
                entry.grid(row=idx, column=1, padx=10, pady=4, sticky="w")
                entry.config(highlightthickness=0)

                if label == "CPF*":
                    entry.bind("<KeyRelease>", lambda e: self._mask_CPF())
                elif label == "RG*":
                    entry.bind("<KeyRelease>", lambda e: self._mask_RG())
                elif label == "CNH*":
                    entry.bind("<KeyRelease>", lambda e: self._mask_CNH())

            self.fields[label] = entry

        button_frame = tk.Frame(self.parent, bg=self.bg_main)
        button_frame.pack(side="bottom", pady=25)

        ListRoundedButton(
            button_frame, text="Salvar alterações", width=180, height=42,
            bg=self.accent, fg=self.fg_text,
            command=self.save_driver
        ).pack(side="left", padx=10)

        ListRoundedButton(
            button_frame, text="Voltar", width=120, height=42,
            bg=self.bg_button, fg=self.fg_text,
            command=self.back
        ).pack(side="left", padx=10)

    def _open_calendar(self, label):
        def set_date(date):
            self.date_vars[label].set(date.strftime("%d/%m/%Y"))

        initial_date = None
        current_val = self.date_vars[label].get()
        if current_val:
            try:
                initial_date = datetime.strptime(current_val, "%d/%m/%Y").date()
            except:
                pass
        CustomCalendar(self.parent, callback=set_date, initial_date=initial_date)

    def _preencher_dados(self):
        self.fields["Nome*"].insert(0, self.driver.name.title())
        self.fields["Salário (R$)*"].insert(0, str(self.driver.salary))
        self.fields["Contato*"].insert(0, self.driver.contact)

        if self.driver.start_date:
            self.date_vars["Início*"].set(datetime.strptime(self.driver.start_date, "%Y-%m-%d").strftime("%d/%m/%Y"))

        if self.driver.end_date:
            self.date_vars["Término"].set(datetime.strptime(self.driver.end_date, "%Y-%m-%d").strftime("%d/%m/%Y"))

        self.fields["CPF*"].insert(0, self._mask_CPF_apply(self.driver.cpf))
        self.fields["RG*"].insert(0, self._mask_RG_apply(self.driver.rg))
        self.fields["CNH*"].insert(0, self.driver.cnh)

        if self.driver.extra_info:
            self.fields["Extras"].insert("1.0", self.driver.extra_info.capitalize())

    def _mask_CPF(self):
        entry = self.fields["CPF*"]
        v = ''.join(filter(str.isdigit, entry.get()))[:11]
        entry.delete(0, tk.END)
        entry.insert(0, self._mask_CPF_apply(v))

    def _mask_CPF_apply(self, v):
        if len(v) > 9:
            return f"{v[:3]}.{v[3:6]}.{v[6:9]}-{v[9:]}"
        elif len(v) > 6:
            return f"{v[:3]}.{v[3:6]}.{v[6:]}"
        elif len(v) > 3:
            return f"{v[:3]}.{v[3:]}"
        return v

    def _mask_RG(self):
        entry = self.fields["RG*"]
        v = ''.join(filter(str.isdigit, entry.get()))[:9]
        entry.delete(0, tk.END)
        entry.insert(0, self._mask_RG_apply(v))

    def _mask_RG_apply(self, v):
        if len(v) > 8:
            return f"{v[:2]}.{v[2:5]}.{v[5:8]}-{v[8:]}"
        elif len(v) > 5:
            return f"{v[:2]}.{v[2:5]}.{v[5:]}"
        elif len(v) > 2:
            return f"{v[:2]}.{v[2:]}"
        return v

    def _mask_CNH(self):
        entry = self.fields["CNH*"]
        v = ''.join(filter(str.isdigit, entry.get()))[:20]
        entry.delete(0, tk.END)
        entry.insert(0, v)

    def save_driver(self):
        try:
            start_date_str = self.date_vars["Início*"].get()
            end_date_str = self.date_vars["Término"].get()

            start_date = datetime.strptime(start_date_str, "%d/%m/%Y").date() if start_date_str else None
            end_date = datetime.strptime(end_date_str, "%d/%m/%Y").date() if end_date_str else None

            if start_date and end_date and start_date >= end_date:
                messagebox.showerror("Erro", "Data de início deve ser anterior ao término")
                return

            driver = Driver(
                driver_id=self.driver.driver_id,
                name=self.fields["Nome*"].get(),
                salary=float(self.fields["Salário (R$)*"].get().replace(',', '.')),
                contact=self.fields["Contato*"].get(),
                start_date=start_date.strftime("%Y-%m-%d") if start_date else None,
                end_date=end_date.strftime("%Y-%m-%d") if end_date else None,
                cpf=''.join(filter(str.isdigit, self.fields["CPF*"].get())),
                rg=''.join(filter(str.isdigit, self.fields["RG*"].get())),
                cnh=self.fields["CNH*"].get(),
                extra_info=self.fields["Extras"].get("1.0", tk.END).strip().capitalize() or None
            )

            self.driver_repo.update(driver)
            messagebox.showinfo("Sucesso", "Dados atualizados")
            self.back()
        except ValueError:
            messagebox.showerror("Erro", "Verifique valores e datas")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def back(self):
        from app.interface.driver.interface_list_drivers import InterfaceListDrivers
        InterfaceListDrivers(self.parent, self.db_path).show()