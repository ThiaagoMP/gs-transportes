import tkinter as tk

class ListRoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=210, height=50,
                 bg="#3a3f47", fg="#ffffff", hover_bg="#ff944d",
                 font=("Segoe UI", 11, "bold"), shadow=True):
        super().__init__(parent, width=width, height=height, highlightthickness=0, bg=parent["bg"])
        self.command = command
        self.bg = bg
        self.fg = fg
        self.hover_bg = hover_bg
        self.font = font
        self.text = text
        self.shadow = shadow
        self.is_pressed = False

        if self.shadow:
            self.shadow_rect = self.create_round_rect(6, 6, width-1, height-1, radius=12, fill="#141414")

        self.rect = self.create_round_rect(2, 2, width-6, height-6, radius=12, fill=self.bg)
        self.label = self.create_text(width//2 - 2, height//2 - 3, text=self.text, fill=self.fg, font=self.font)

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
        for tag in (self.rect, self.label):
            self.tag_bind(tag, "<Enter>", self.on_enter)
            self.tag_bind(tag, "<Leave>", self.on_leave)
            self.tag_bind(tag, "<ButtonPress-1>", self.on_press)
            self.tag_bind(tag, "<ButtonRelease-1>", self.on_release)

    def create_round_rect(self, x1, y1, x2, y2, radius=12, **kwargs):
        points = [
            x1+radius, y1, x2-radius, y1,
            x2, y1, x2, y1+radius,
            x2, y2-radius, x2, y2,
            x2-radius, y2, x1+radius, y2,
            x1, y2, x1, y2-radius,
            x1, y1+radius, x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def on_enter(self, event):
        if not self.is_pressed:
            self.itemconfig(self.rect, fill=self.hover_bg)

    def on_leave(self, event):
        if not self.is_pressed:
            self.itemconfig(self.rect, fill=self.bg)

    def on_press(self, event):
        if not self.is_pressed:
            self.is_pressed = True
            self.move(self.rect, 2, 2)
            self.move(self.label, 2, 2)
            self.itemconfig(self.rect, fill=self.hover_bg)

    def on_release(self, event):
        if self.is_pressed:
            self.is_pressed = False
            self.move(self.rect, -2, -2)
            self.move(self.label, -2, -2)
            self.itemconfig(self.rect, fill=self.bg)
            if self.command:
                self.command()
