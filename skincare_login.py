# login_view.py
import tkinter as tk
from tkinter import messagebox

APP_W, APP_H = 360, 800
TXT = "#1F2937"
TXT_MUTED = "#6B7280"
ACCENT = "#8B5CF6"

VALID_USER = "TBD"
VALID_PASS = "414008"

class LoginFrame(tk.Frame):
    """Login page. Calls on_success() after a successful sign-in."""
    def __init__(self, master, on_success):
        super().__init__(master, width=APP_W, height=APP_H)
        self.pack_propagate(False)
        self.on_success = on_success

        # Background gradient and bottom white container
        self.canvas = tk.Canvas(self, width=APP_W, height=APP_H, highlightthickness=0)
        self.canvas.place(x=0, y=0)
        self.draw_vertical_gradient(self.canvas, 0, 0, APP_W, int(APP_H * 0.62),
                                    "#A855F7", "#EC4899")
        self.draw_round_rect(self.canvas, 0, int(APP_H * 0.55), APP_W, APP_H, 28, fill="#FFFFFF")

        # White cosmetics outline icon + title
        self.draw_cosmetics_icon(self.canvas, APP_W / 2, 120, scale=1.0, color="#FFFFFF")
        self.canvas.create_text(APP_W / 2, 220, anchor="n", text="SKINOVATE",
                                fill="#FFFFFF", font=("Segoe UI", 20, "bold"))

        # Form
        form = tk.Frame(self, bg="#FFFFFF")
        form.place(x=24, y=int(APP_H * 0.62))

        self.email_var = tk.StringVar()
        self.pass_var = tk.StringVar()

        self.email_entry = self.input_pill(form, placeholder="EMAIL",
                                           var=self.email_var, is_password=False, pady=8)
        self.pass_entry = self.input_pill(form, placeholder="PASSWORD",
                                          var=self.pass_var, is_password=True, pady=8)

        tk.Label(form, text="Test account: TBD   Password: 414008",
                 fg=TXT_MUTED, bg="#FFFFFF", font=("Segoe UI", 9)).pack(pady=(0, 10))

        tk.Button(form, text="SIGN IN", font=("Segoe UI", 11, "bold"),
                  fg="#FFFFFF", bg=ACCENT, activebackground="#7C3AED",
                  bd=0, relief="flat", width=24, height=2,
                  command=self.try_login).pack(pady=(0, 10))

        tk.Button(form, text="CREATE AN ACCOUNT", font=("Segoe UI", 10),
                  fg="#9CA3AF", bg="#F3F4F6", bd=0, relief="flat",
                  state="disabled", width=24, height=2).pack(pady=(0, 6))

    def input_pill(self, parent, placeholder, var, is_password=False, pady=6):
        """Rounded input with placeholder. Password shows bullets only while focused."""
        wrap = tk.Frame(parent, bg="#FFFFFF")
        wrap.pack(pady=pady)

        pill = tk.Canvas(wrap, width=APP_W - 48, height=40, bg="#FFFFFF", highlightthickness=0)
        pill.pack()
        self.draw_round_rect(pill, 0, 0, APP_W - 48, 40, 20, fill="#EDE9FE")

        entry = tk.Entry(wrap, textvariable=var, bd=0, relief="flat",
                         bg="#EDE9FE", fg=TXT, insertbackground=TXT,
                         width=28, font=("Segoe UI", 10))
        entry.place(x=18, y=9)
        entry.insert(0, placeholder)
        entry.config(fg="#9CA3AF")

        def on_focus_in(_):
            if entry.get() == placeholder:
                entry.delete(0, "end")
                entry.config(fg=TXT)
            if is_password:
                entry.config(show="•")

        def on_focus_out(_):
            if entry.get() == "":
                entry.insert(0, placeholder)
                entry.config(fg="#9CA3AF")
                if is_password:
                    entry.config(show="")

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
        entry.bind("<Return>", lambda _e: self.try_login())
        return entry

    def _read_clean(self):
        user = self.email_var.get().strip()
        pwd = self.pass_var.get().strip()
        if user.upper() == "EMAIL": user = ""
        if pwd.upper() == "PASSWORD": pwd = ""
        return user, pwd

    def try_login(self):
        user, pwd = self._read_clean()
        if not user or not pwd:
            messagebox.showwarning("Missing", "Please enter the test account (TBD / 414008).")
            return
        if user == VALID_USER and pwd == VALID_PASS:
            # Switch after this callback returns to avoid refresh issues
            self.after(0, self.on_success)
        else:
            messagebox.showerror("Login failed", "Incorrect email or password.\nUse: TBD / 414008")

    # --- drawing helpers ---
    @staticmethod
    def draw_vertical_gradient(c, x1, y1, x2, y2, color1, color2, steps=100):
        def hex_to_rgb(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
        r1, g1, b1 = hex_to_rgb(color1); r2, g2, b2 = hex_to_rgb(color2)
        h = y2 - y1
        for i in range(steps):
            r = r1 + (r2 - r1) * i // steps
            g = g1 + (g2 - g1) * i // steps
            b = b1 + (b2 - b1) * i // steps
            c.create_rectangle(x1, y1 + i * h / steps, x2, y1 + (i + 1) * h / steps,
                               outline="", fill=f"#{r:02x}{g:02x}{b:02x}")

    @staticmethod
    def draw_round_rect(c, x1, y1, x2, y2, r, **kw):
        pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
               x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
        c.create_polygon(pts, smooth=True, **kw)

    @staticmethod
    def draw_cosmetics_icon(c, cx, top_y, scale=1.0, color="#FFFFFF"):
        body_w = 90 * scale; body_h = 110 * scale
        cap_w = 46 * scale; cap_h = 16 * scale
        neck_h = 10 * scale; line_w = 3
        x1 = cx - body_w / 2; x2 = cx + body_w / 2
        y1 = top_y + cap_h + neck_h; y2 = y1 + body_h
        c.create_rectangle(x1, y1, x2, y2, outline=color, width=line_w)
        c.create_rectangle(cx - cap_w / 2, top_y, cx + cap_w / 2, top_y + cap_h,
                           outline=color, width=line_w)
        c.create_line(cx - cap_w / 4, top_y + cap_h, cx - cap_w / 4, y1, fill=color, width=line_w)
        c.create_line(cx + cap_w / 4, top_y + cap_h, cx + cap_w / 4, y1, fill=color, width=line_w)
        label_h = 20 * scale; label_w = body_w * 0.55
        ly = y1 + body_h * 0.5 - label_h / 2
        c.create_rectangle(cx - label_w / 2, ly, cx + label_w / 2, ly + label_h,
                           outline=color, width=line_w)
