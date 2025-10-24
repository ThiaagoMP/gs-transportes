import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

from app.components.custom_calendar import CustomCalendar
from app.models.driver import Driver
from app.repositories.driver_repository import DriverRepository


class InterfaceEditDriver(tk.Frame):
    def __init__(self, parent, db_path, driver: Driver):
        super().__init__(parent, bg="#1c1c1e")
        self.parent = parent
        self.driver = driver
        self.db_path = db_path
        self.driver_repo = DriverRepository(db_path)

        self.bg_main = "#1c1c1e"
        self.bg_button = "#3a3f47"
        self.fg_text = "#ffffff"
        self.accent = "#ff7f32"

        self.font_title = ("Segoe UI", 26, "bold")
        self.font_label = ("Segoe UI", 14)
        self.font_entry = ("Segoe UI", 12)
        self.font_button = ("Segoe UI", 10)

        self.fields = {}
        self.show()
        self._preencher_dados()

    def show(self):
        from app.components.list_rounded_button import ListRoundedButton

        tk.Label(self, text="Editar Motorista", font=self.font_title,
                 bg=self.bg_main, fg=self.accent).pack(pady=20)

        self.form_frame = tk.Frame(self, bg=self.bg_main)
        self.form_frame.pack(padx=30, pady=10)

        labels = [
            "Nome*", "Salário (R$)*", "Contato*", "Data de Início*", "Data de Término",
            "CPF*", "RG*", "CNH*", "Informações Extras"
        ]

        for idx, label in enumerate(labels):
            tk.Label(self.form_frame, text=label, font=self.font_label,
                     bg=self.bg_main, fg=self.fg_text, anchor="w") \
                .grid(row=idx, column=0, sticky="w", pady=5)

            if label == "Informações Extras":
                entry = tk.Text(self.form_frame, width=40, height=4, font=self.font_entry,
                                bg="#2a2a2a", fg=self.fg_text, insertbackground=self.fg_text)
            elif "Data" in label:
                frame = tk.Frame(self.form_frame, bg=self.bg_main)
                frame.grid(row=idx, column=1, padx=10, pady=5, sticky="w")
                entry = tk.Entry(frame, font=self.font_entry, width=25,
                                 bg="#2a2a2a", fg=self.fg_text, insertbackground=self.fg_text)
                entry.pack(side="left")
                tk.Button(frame, text="📅", font=self.font_button, bg=self.bg_button, fg=self.fg_text,
                          relief="flat", command=lambda e=entry, l=label: self._open_calendar(e, l)).pack(side="left",
                                                                                                          padx=5)
                tk.Button(frame, text="Limpar", font=self.font_button, bg=self.bg_button, fg=self.fg_text,
                          relief="flat", command=lambda e=entry: e.delete(0, tk.END)).pack(side="left", padx=5)
            else:
                entry = tk.Entry(self.form_frame, font=self.font_entry, width=40,
                                 bg="#2a2a2a", fg=self.fg_text, insertbackground=self.fg_text)

                if label == "CPF*":
                    entry.bind("<KeyRelease>", lambda e: self._mask_cpf())
                if label == "RG*":
                    entry.bind("<KeyRelease>", lambda e: self._mask_rg())
                if label == "CNH*":
                    entry.bind("<KeyRelease>", lambda e: self._mask_cnh())

            if "Data" not in label:
                entry.grid(row=idx, column=1, padx=10, pady=5, sticky="w")
            self.fields[label] = entry

        button_frame = tk.Frame(self, bg=self.bg_main)
        button_frame.pack(pady=20)

        ListRoundedButton(button_frame, text="Salvar", width=200, height=50,
                          bg=self.bg_button, fg=self.fg_text,
                          command=self.save_driver).pack(side="left", padx=10)

        if self.driver.end_date:
            ListRoundedButton(button_frame, text="Remover Histórico", width=200, height=50,
                              bg=self.bg_button, fg=self.fg_text,
                              command=self.remove_history).pack(side="left", padx=10)

        ListRoundedButton(button_frame, text="Voltar", width=200, height=50,
                          bg=self.bg_button, fg=self.fg_text,
                          command=self.back).pack(side="left", padx=10)

        tk.Label(self, text="* Campos obrigatórios", font=("Segoe UI", 12, "italic"),
                 bg=self.bg_main, fg=self.fg_text).pack(pady=5)

    def _open_calendar(self, entry, label):
        def set_date(date):
            entry.delete(0, tk.END)
            entry.insert(0, date.strftime("%d/%m/%Y"))

        initial_date = None
        if entry.get():
            try:
                initial_date = datetime.strptime(entry.get(), "%d/%m/%Y").date()
            except ValueError:
                pass
        CustomCalendar(self, callback=set_date, initial_date=initial_date)

    def clear_dates(self):
        self.fields["Data de Início*"].delete(0, tk.END)
        self.fields["Data de Término"].delete(0, tk.END)

    def _preencher_dados(self):
        self.fields["Nome*"].insert(0, self.driver.name)
        self.fields["Salário (R$)*"].insert(0, str(self.driver.salary))
        self.fields["Contato*"].insert(0, self.driver.contact)
        if self.driver.start_date:
            self.fields["Data de Início*"].insert(0, datetime.strptime(self.driver.start_date, "%Y-%m-%d").strftime("%d/%m/%Y"))
        if self.driver.end_date:
            self.fields["Data de Término"].insert(0, datetime.strptime(self.driver.end_date, "%Y-%m-%d").strftime("%d/%m/%Y"))

        self.fields["CPF*"].insert(0, self._mask_cpf_apply(self.driver.cpf))
        self.fields["RG*"].insert(0, self._mask_rg_apply(self.driver.rg))
        self.fields["CNH*"].insert(0, self.driver.cnh)

        if self.driver.extra_info:
            self.fields["Informações Extras"].insert("1.0", self.driver.extra_info)

    def _mask_cpf(self):
        entry = self.fields["CPF*"]
        v = ''.join(filter(str.isdigit, entry.get()))[:11]
        entry.delete(0, tk.END)
        entry.insert(0, self._mask_cpf_apply(v))

    def _mask_cpf_apply(self, v):
        if len(v) > 9:
            return f"{v[:3]}.{v[3:6]}.{v[6:9]}-{v[9:]}"
        elif len(v) > 6:
            return f"{v[:3]}.{v[3:6]}.{v[6:]}"
        elif len(v) > 3:
            return f"{v[:3]}.{v[3:]}"
        else:
            return v

    def _mask_rg(self):
        entry = self.fields["RG*"]
        v = ''.join(filter(str.isdigit, entry.get()))[:9]
        entry.delete(0, tk.END)
        entry.insert(0, self._mask_rg_apply(v))

    def _mask_rg_apply(self, v):
        if len(v) > 5:
            return f"{v[:2]}.{v[2:5]}.{v[5:8]}-{v[8:]}"
        elif len(v) > 2:
            return f"{v[:2]}.{v[2:5]}.{v[5:8]}"
        else:
            return v

    def _mask_cnh(self):
        entry = self.fields["CNH*"]
        v = ''.join(filter(str.isdigit, entry.get()))[:20]
        entry.delete(0, tk.END)
        entry.insert(0, v)

    def save_driver(self):
        try:
            start_date_str = self.fields["Data de Início*"].get()
            end_date_str = self.fields["Data de Término"].get()

            start_date = datetime.strptime(start_date_str, "%d/%m/%Y").date() if start_date_str else None
            end_date = datetime.strptime(end_date_str, "%d/%m/%Y").date() if end_date_str else None

            if start_date and end_date and start_date >= end_date:
                messagebox.showerror("Erro", "A data de início deve ser anterior à data de término.")
                return

            start_date_formatted = start_date.strftime("%Y-%m-%d") if start_date else None
            end_date_formatted = end_date.strftime("%Y-%m-%d") if end_date else None

            name = self.fields["Nome*"].get()
            salary = float(self.fields["Salário (R$)*"].get())
            contact = self.fields["Contato*"].get()
            cpf = self.fields["CPF*"].get()
            rg = self.fields["RG*"].get()
            cnh = self.fields["CNH*"].get()
            extra_info = self.fields["Informações Extras"].get("1.0", tk.END).strip() or None

            driver = Driver(
                driver_id=self.driver.driver_id,
                name=name,
                salary=salary,
                contact=contact,
                start_date=start_date_formatted,
                end_date=end_date_formatted,
                cpf=cpf,
                rg=rg,
                cnh=cnh,
                extra_info=extra_info
            )

            self.driver_repo.update(driver)

            messagebox.showinfo("Sucesso", f"Motorista '{driver.name}' atualizado com sucesso!")
        except ValueError as e:
            messagebox.showerror("Erro", f"Formato de data inválido: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def remove_history(self):
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja remover o histórico deste motorista?"):
            try:
                self.driver_repo.delete(self.driver.driver_id)
                messagebox.showinfo("Sucesso", f"Histórico do motorista '{self.driver.name}' removido com sucesso!")
                self.back()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

    def back(self):
        from app.interface.driver.interface_list_drivers import InterfaceListDrivers
        interface = InterfaceListDrivers(self.parent, self.db_path)
        interface.show()
        self.destroy()
