# main.py
import tkinter as tk
from tkinter import simpledialog, messagebox
from datetime import date, timedelta
import calendar

from skincare_login import LoginFrame, APP_W, APP_H

# --- theme ---
BG = "#F4F6F8"
TXT = "#1F2937"
TXT_MUTED = "#6B7280"
CARD_BG = "#FFFFFF"
ACCENT = "#8B5CF6"
GRAY = "#E5E7EB"
GREEN = "#10B981"

# Color palette for products (first = red, second = blue, etc.)
PRODUCT_COLORS = [
    "#EF4444",  # red
    "#3B82F6",  # blue
    "#10B981",  # green
    "#F59E0B",  # amber
    "#A855F7",  # violet
    "#06B6D4",  # cyan
]

# =========================
# UI style helpers（只加样式，不改功能）
# =========================
SURFACE = "#FFFFFF"
PRIMARY = "#8B5CF6"
PRIMARY_2 = "#EC4899"

def _grad(c1, c2, steps):
    def h2r(h): return tuple(int(h[i:i+2], 16) for i in (1, 3, 5))
    def r2h(r): return "#%02x%02x%02x" % r
    a, b = h2r(c1), h2r(c2)
    out = []
    for i in range(steps):
        t = i/(steps-1) if steps > 1 else 0
        out.append(r2h((int(a[0] + (b[0]-a[0])*t),
                        int(a[1] + (b[1]-a[1])*t),
                        int(a[2] + (b[2]-a[2])*t))))
    return out

def banner(parent, text):
    cv = tk.Canvas(parent, height=68, highlightthickness=0, bg=BG)
    cv.pack(fill="x")
    for i, c in enumerate(_grad(PRIMARY, PRIMARY_2, 160)):
        cv.create_rectangle(i*5, 0, i*5+5, 68, outline="", fill=c)
    cv.create_text(16, 38, anchor="w", text=text, fill="white", font=("Segoe UI", 16, "bold"))
    return cv

def make_card(parent, pad=(10,10,10,10)):
    outer = tk.Frame(parent, bg="#E9ECF2")
    inner = tk.Frame(outer, bg=SURFACE, highlightthickness=1, highlightbackground="#EEF1F6")
    inner.pack(padx=1, pady=1, fill="both", expand=True)
    l, t, r, b = pad
    outer.pack(padx=(l, r), pady=(t, b), fill="x")
    return outer, inner

class PillButton(tk.Button):
    def __init__(self, master, text, command=None, primary=False, **kw):
        base = dict(
            text=text, command=command, bd=0, padx=14, pady=8, cursor="hand2",
            font=("Segoe UI", 10, "bold") if primary else ("Segoe UI", 10),
            bg=PRIMARY if primary else "#F1F5FE",
            fg="white" if primary else TXT,
            activebackground="#EC4899" if primary else "#E8F0FF",
            activeforeground="white" if primary else TXT,
        )
        base.update(kw)
        super().__init__(master, **base)
        self._primary = primary
        self.bind("<Enter>", lambda e: self.config(bg=("#EC4899" if self._primary else "#E8F0FF")))
        self.bind("<Leave>", lambda e: self.config(bg=(PRIMARY if self._primary else "#F1F5FE")))

class VScrollFrame(tk.Frame):
    """简易竖向滚动容器：在固定高度里滚动显示内容"""
    def __init__(self, master, height=220, **kw):
        super().__init__(master, **kw)
        self.canvas = tk.Canvas(self, bg=SURFACE, highlightthickness=0, height=height)
        self.vbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=SURFACE)

        self.inner.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.vbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.vbar.pack(side="right", fill="y")

# ---------- bottom nav ----------
class NavBar(tk.Frame):
    def __init__(self, master, on_select):
        super().__init__(master, bg="#FFFFFF", height=60)
        self.on_select = on_select
        self.pack_propagate(False)
        for i in range(4):
            self.grid_columnconfigure(i, weight=1)
        self.items = [("home", "🏠"), ("products", "🧴"), ("explore", "🔍"), ("settings", "⚙️")]
        self.buttons = []
        for idx, (_, icon) in enumerate(self.items):
            btn = tk.Button(
                self, text=icon, font=("Segoe UI Emoji", 16), bd=0,
                bg="#FFFFFF", fg="#94A3B8", activebackground="#F8FAFC",
                activeforeground=TXT, command=lambda i=idx: self.on_select(i)
            )
            btn.grid(row=0, column=idx, sticky="nsew", pady=8)
            self.buttons.append(btn)

    def set_active(self, idx):
        for i, btn in enumerate(self.buttons):
            if i == idx:
                btn.config(fg=TXT, font=("Segoe UI Emoji", 16, "bold"))
            else:
                btn.config(fg="#94A3B8", font=("Segoe UI Emoji", 16, "normal"))

# ---------- product data ----------
class ProductManager:
    def __init__(self):
        self.products = {}
        self._next_id = 1

    def add(self, name, total, desc="— (edit me)"):
        total = int(total)
        pid = self._next_id
        self._next_id += 1
        self.products[pid] = {
            "name": name,
            "total": total,
            "remaining": total,
            "streak": 0,
            "streak_start": None,
            "last_used_date": None,
            "purchased": False,
            "last_tier_shown": 0,
            "desc": desc,
        }
        return pid

    def remove(self, pid):
        if pid in self.products:
            del self.products[pid]

    def toggle_purchased(self, pid, flag=None):
        if pid in self.products:
            self.products[pid]["purchased"] = (not self.products[pid]["purchased"]) if flag is None else bool(flag)

    def mark_used_today(self, pid, day: date):
        p = self.products[pid]
        prev = p["last_used_date"]

        if prev is None:
            p["streak"] = 1
            p["streak_start"] = day
        elif prev == day:
            pass
        elif prev == day - timedelta(days=1):
            p["streak"] += 1
        else:
            p["streak"] = 1
            p["streak_start"] = day

        p["last_used_date"] = day
        if p["remaining"] > 0:
            p["remaining"] -= 1

        tier = self.calc_discount(p["total"], p["streak"])
        crossed = tier if tier > p["last_tier_shown"] else 0
        if tier > p["last_tier_shown"]:
            p["last_tier_shown"] = tier
        return crossed

    @staticmethod
    def calc_discount(total, streak):
        if streak >= total:
            return 10
        ratio = streak / max(total, 1)
        if ratio > 2 / 3:
            return 8
        if ratio > 1 / 3:
            return 5
        return 0

# ---------- Home ----------
class CalendarHomeFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, width=APP_W, height=APP_H, bg=BG)
        self.pack_propagate(False)

        self.app = self.winfo_toplevel()
        self.pm = getattr(self.app, "_product_manager", None) or ProductManager()
        self.app._product_manager = self.pm

        today = date.today()
        self.year = today.year
        self.month = today.month
        self.checkins = set()
        self.cells = {}

        if not hasattr(self.app, "_plan_start"):
            self.app._plan_start = today
        self.plan_start = self.app._plan_start

        banner(self, "Skinovate Tracker")

        top = tk.Frame(self, bg=BG); top.pack(fill="x", pady=(12, 4), padx=12)
        tk.Label(top, text="Skinovate Tracker", bg=BG, fg=TXT,
                 font=("Segoe UI", 16, "bold")).pack(side="left")
        PillButton(top, "?", command=self.show_rules).pack(side="left", padx=(8, 0))

        nav = tk.Frame(top, bg=BG); nav.pack(side="right")
        PillButton(nav, "◀", command=self.prev_month).pack(side="left")
        self.month_lbl = tk.Label(nav, text=self.month_title(), bg=BG, fg=TXT, font=("Segoe UI", 11))
        self.month_lbl.pack(side="left", padx=4)
        PillButton(nav, "▶", command=self.next_month).pack(side="left")

        container = tk.Frame(self, bg=BG); container.pack(fill="both", expand=True, padx=10, pady=6)
        container.grid_rowconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=0)
        container.grid_columnconfigure(0, weight=1)

        # Calendar（保持逻辑不变，仅卡片外观）
        CALENDAR_MAX_H = 280
        _, cal_card_inner = make_card(container, pad=(8, 0, 12, 8))
        self.cal_frame = tk.Frame(cal_card_inner, bg=SURFACE, height=CALENDAR_MAX_H)
        self.cal_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.cal_frame.pack_propagate(False)

        # Products 区：标题+Add 固定，列表可滚动（解决 Product B 不全）
        _, list_card_inner = make_card(container, pad=(8, 0, 12, 12))

        header = tk.Frame(list_card_inner, bg=SURFACE)
        header.pack(fill="x", padx=8, pady=(8, 4))
        tk.Label(header, text="Products", bg=SURFACE, fg=TXT, font=("Segoe UI", 12, "bold")).pack(side="left")
        PillButton(header, "Add", primary=True, fg= "black", command=self.add_product_dialog).pack(side="right")

        # 可滚动列表区域（高度固定，超出滚动）
        self.scroll = VScrollFrame(list_card_inner, height=220, bg=SURFACE)
        self.scroll.pack(fill="x", padx=4, pady=(0, 8))
        self.list_frame = tk.Frame(self.scroll.inner, bg=SURFACE)  # 实际放 item 的容器
        self.list_frame.pack(fill="x")

        self.build_calendar()
        self.refresh_sidebar()

    def month_title(self):
        return f"{self.year}-{self.month:02d}"

    def prev_month(self):
        if self.month == 1:
            self.month = 12; self.year -= 1
        else:
            self.month -= 1
        self.refresh_calendar_header()

    def next_month(self):
        if self.month == 12:
            self.month = 1; self.year += 1
        else:
            self.month += 1
        self.refresh_calendar_header()

    def refresh_calendar_header(self):
        self.month_lbl.config(text=self.month_title())
        self.build_calendar()

    def _product_color_map(self):
        plan = getattr(self.app, "_plan", []) or []
        names_in_plan = []
        for s in plan:
            nm = s.get("step")
            if nm and nm not in names_in_plan:
                names_in_plan.append(nm)
        existing_names = [p["name"] for _, p in sorted(self.pm.products.items())]
        ordered_names = [n for n in names_in_plan if n in existing_names] or existing_names
        return {n: PRODUCT_COLORS[i % len(PRODUCT_COLORS)] for i, n in enumerate(ordered_names)}

    def build_calendar(self):
        for w in self.cal_frame.winfo_children():
            w.destroy()

        head = tk.Frame(self.cal_frame, bg=SURFACE); head.pack(fill="x", pady=(0, 4))
        for i, wd in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            lbl = tk.Label(head, text=wd, bg=SURFACE, fg=TXT_MUTED, font=("Segoe UI", 9))
            lbl.grid(row=0, column=i, padx=3, pady=2, sticky="nsew")
            head.grid_columnconfigure(i, weight=1)

        grid = tk.Frame(self.cal_frame, bg=SURFACE); grid.pack(fill="both", expand=True)

        cal_obj = calendar.Calendar(firstweekday=0)
        weeks = cal_obj.monthdatescalendar(self.year, self.month)

        self.cells = {}
        for r, week in enumerate(weeks):
            grid.grid_rowconfigure(r, weight=1)
            for c, d in enumerate(week):
                grid.grid_columnconfigure(c, weight=1)
                cell = tk.Frame(grid, width=40, height=24, bg="#FFFFFF", bd=0, relief="flat")
                cell.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")

                in_month = (d.month == self.month)
                bg = "#FFFFFF" if in_month else "#F3F4F6"
                cell.configure(bg=bg)

                day_lbl = tk.Label(cell, text=str(d.day), bg=bg,
                                   fg=TXT if in_month else "#9CA3AF", font=("Segoe UI", 10, "bold"))
                day_lbl.place(x=6, y=4)

                if d in self.checkins:
                    cell.configure(bg="#F5F5F5")
                    day_lbl.configure(text="✓", fg=GREEN, bg="#F5F5F5")

                badge = tk.Canvas(cell, width=12, height=54, bg=bg, highlightthickness=0)
                badge.place(x=40 - 12 - 2, y=4)
                badge.delete("all")

                def on_cell_click(event, day=d, frame=cell, dk=day_lbl, bd=badge):
                    self.day_menu(day, frame, dk, bd)

                cell.bind("<Button-1>", on_cell_click)
                day_lbl.bind("<Button-1>", on_cell_click)

                self.cells[d] = {"cell": cell, "day_lbl": day_lbl, "badge": badge}

        self._refresh_all_markers()

    def _compute_goal_dates(self):
        milestones = {}
        base_plan_start = getattr(self.app, "_plan_start", date.today())
        for p in self.pm.products.values():
            total = int(p.get("total", 0) or 0)
            if total <= 0:
                continue
            base = p.get("streak_start") or base_plan_start
            m1 = total // 3
            m2 = (2 * total) // 3
            days = []
            if m1 > 0: days.append(base + timedelta(days=m1 - 1))
            if m2 > 0: days.append(base + timedelta(days=m2 - 1))
            for d in days:
                milestones.setdefault(d, []).append(p["name"])
        return milestones

    def _refresh_all_markers(self):
        color_map = self._product_color_map()
        milestone_map = self._compute_goal_dates()
        for d, parts in self.cells.items():
            bd = parts["badge"]; bg = parts["cell"].cget("bg")
            bd.configure(bg=bg); bd.delete("all")
            products_today = milestone_map.get(d, [])
            if not products_today: continue
            ordered_names = [nm for nm in color_map.keys() if nm in products_today]
            for nm in products_today:
                if nm not in ordered_names: ordered_names.append(nm)
            margin_top, step_y, radius, cx = 2, 9, 3, 6
            for idx, name in enumerate(ordered_names):
                y = margin_top + idx * step_y
                col = color_map.get(name, "#D1D5DB")
                bd.create_oval(cx - radius, y, cx + radius, y + 2 * radius, fill=col, outline="")

    def day_menu(self, d: date, frame, day_lbl, badge_canvas):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Check in", command=lambda: self.checkin_day(d))
        menu.add_separator()
        menu.add_command(label="Add product", command=self.add_product_dialog)
        menu.add_command(label="Remove product", command=self.remove_product_dialog)
        try:
            menu.tk_popup(frame.winfo_rootx() + 10, frame.winfo_rooty() + 10)
        finally:
            menu.grab_release()

    def checkin_day(self, d: date):
        if d > date.today():
            messagebox.showwarning("Notice", "You cannot check in a future date.")
            return
        if not self.pm.products:
            messagebox.showinfo("Notice", "Please add at least one product (Add button).")
            return

        used = self.select_products_dialog("Select the products you used")
        if not used: return

        crossed_tiers = []
        for pid in used:
            tier = self.pm.mark_used_today(pid, d)
            if tier: crossed_tiers.append((pid, tier))

        self.checkins.add(d)
        parts = self.cells.get(d)
        if parts:
            parts["cell"].configure(bg="#F5F5F5")
            parts["day_lbl"].configure(text="✓", fg=GREEN, bg="#F5F5F5")

        if crossed_tiers:
            best = max(t for _, t in crossed_tiers)
            pct_rank = 80 if best == 10 else (60 if best == 8 else 40)
            messagebox.showinfo(
                "Congratulations!",
                f"You just reached a new discount tier ({best}%).\nYour consistency beats {pct_rank}% of users—keep it up!"
            )

        self.refresh_sidebar()
        self._refresh_all_markers()

    # ----- products panel (bottom → scrollable) -----
    def refresh_sidebar(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        cmap = self._product_color_map()
        plan = getattr(self.app, "_plan", []) or []
        plan_names = []
        for s in plan:
            nm = s.get("step")
            if nm and nm not in plan_names:
                plan_names.append(nm)

        name_to_pid = {p["name"]: pid for pid, p in self.pm.products.items()}
        ordered = [name for name in plan_names if name in name_to_pid]
        if not ordered:
            tk.Label(self.list_frame, text="No products (take the quiz to create a plan).",
                     bg=SURFACE, fg=TXT_MUTED).pack(pady=8, anchor="w")
            return

        def color_for(name): return cmap.get(name, "#D1D5DB")

        for name in ordered:
            pid = name_to_pid[name]
            p = self.pm.products[pid]

            box = tk.Frame(self.list_frame, bg=SURFACE, highlightthickness=1, highlightbackground=GRAY)
            box.pack(fill="x", pady=6, padx=4)

            topbar = tk.Frame(box, bg=SURFACE); topbar.pack(fill="x", padx=6, pady=(6, 0))
            tk.Label(topbar, text=p["name"], bg=SURFACE, fg=TXT, font=("Segoe UI", 10, "bold")).pack(side="left")
            tk.Frame(topbar, bg=SURFACE).pack(side="left", expand=True, fill="x")
            dot = tk.Canvas(topbar, width=12, height=12, bg=SURFACE, highlightthickness=0)
            dot.pack(side="right", padx=2)
            dot.create_oval(3, 3, 9, 9, fill=color_for(p["name"]), outline="")

            tk.Label(box, text=f"Remaining {p['remaining']}/{p['total']}  •  Streak {p['streak']}",
                     bg=SURFACE, fg=TXT_MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=6, pady=(0, 6))

            btns = tk.Frame(box, bg=SURFACE); btns.pack(fill="x", padx=6, pady=(0, 8))

            def on_set_total(product_id=pid):
                p0 = self.pm.products[product_id]
                old_total = int(p0["total"]); old_remaining = int(p0["remaining"])
                used = max(0, old_total - old_remaining)
                new_total = simpledialog.askinteger(
                    "Set total usages",
                    f"Enter total usages for {p0['name']} (current {old_total}):",
                    parent=self, minvalue=1, maxvalue=365, initialvalue=old_total
                )
                if new_total:
                    p0["total"] = int(new_total)
                    p0["remaining"] = max(0, int(new_total) - used)
                    self.refresh_sidebar()
                    self._refresh_all_markers()

            PillButton(btns, "Set total", command=on_set_total).pack(side="left", padx=(0, 6))
            PillButton(btns, "Use today", command=lambda i=pid: self.use_product_today(i)).pack(side="left", padx=(0, 6))
            PillButton(btns, "Delete", command=lambda i=pid: self.delete_product(i)).pack(side="left")

            if p["remaining"] <= 5:
                PillButton(btns, "Mark as finished",
                           command=lambda i=pid: self.finish_product(i)).pack(side="right")

    def use_product_today(self, pid):
        tier = self.pm.mark_used_today(pid, date.today())
        self.checkins.add(date.today())
        parts = self.cells.get(date.today())
        if parts:
            parts["cell"].configure(bg="#F5F5F5")
            parts["day_lbl"].configure(text="✓", fg=GREEN, bg="#F5F5F5")
        if tier:
            pct_rank = 80 if tier == 10 else (60 if tier == 8 else 40)
            messagebox.showinfo(
                "Congratulations!",
                f"You just reached a new discount tier ({tier}%).\nYour consistency beats {pct_rank}% of users—keep it up!"
            )
        self.refresh_sidebar()
        self._refresh_all_markers()

    def finish_product(self, pid):
        p = self.pm.products[pid]
        disc = ProductManager.calc_discount(p["total"], p["streak"])
        messagebox.showinfo("Finished", f"{p['name']} is marked as finished.\nDiscount: {disc}%")
        if messagebox.askyesno("Finished", "Remove this product from the list?"):
            self.pm.remove(pid)
            self.refresh_sidebar()
            self._refresh_all_markers()

    # dialogs（按钮统一换 PillButton，不改逻辑）
    def add_product_dialog(self):
        name = simpledialog.askstring("Add product", "Product name:", parent=self)
        if not name: return
        total = simpledialog.askinteger("Add product", "Total usages (default 30):",
                                        parent=self, initialvalue=30, minvalue=1, maxvalue=365) or 30
        desc = simpledialog.askstring("Add product", "Short description (e.g., hydration):", parent=self) or "— (edit me)"
        self.pm.add(name, total, desc=desc)
        self.refresh_sidebar()
        self._refresh_all_markers()

    def delete_product(self, pid):
        self.pm.remove(pid)
        self.refresh_sidebar()
        self._refresh_all_markers()

    def remove_product_dialog(self):
        if not self.pm.products:
            messagebox.showinfo("Remove", "No products to remove."); return
        dlg = tk.Toplevel(self); dlg.title("Remove product", fg="black"); dlg.configure(bg=SURFACE)
        tk.Label(dlg, text="Select products to remove:", bg=SURFACE).pack(padx=10, pady=8)
        vars_ = {}
        for pid, p in self.pm.products.items():
            v = tk.BooleanVar(value=False); vars_[pid] = v
            tk.Checkbutton(dlg, text=p["name"], variable=v, bg=SURFACE).pack(anchor="w", padx=12)

        def do_del():
            for pid, v in list(vars_.items()):
                if v.get(): self.pm.remove(pid)
            self.refresh_sidebar(); dlg.destroy(); self._refresh_all_markers()

        PillButton(dlg, "Remove", primary=True, command=do_del).pack(pady=10)

    def select_products_dialog(self, title):
        dlg = tk.Toplevel(self); dlg.title(title); dlg.configure(bg=SURFACE)
        sel = {}
        tk.Label(dlg, text=title, bg=SURFACE, font=("Segoe UI", 10, "bold")).pack(padx=10, pady=8)
        for pid, p in self.pm.products.items():
            v = tk.BooleanVar(value=False); sel[pid] = v
            tk.Checkbutton(dlg, text=f"{p['name']} ({p['remaining']}/{p['total']})",
                           variable=v, bg=SURFACE).pack(anchor="w", padx=12)
        chosen = []

        def ok():
            chosen.extend([pid for pid, v in sel.items() if v.get()])
            dlg.destroy()

        PillButton(dlg, "OK", primary=True, command=ok).pack(pady=10)
        dlg.grab_set(); dlg.wait_window()
        return chosen

    def show_rules(self):
        messagebox.showinfo(
            "Rules",
            "• Check-in: select products you used (future dates are not allowed).\n"
            "• Finish window: when a product is near completion (remaining ≤ 5), you can mark it as finished.\n"
            "• Discount tiers: 1/3→5%, 2/3→8%, total→10% based on continuous streaks.\n"
            "• Calendar markers: colored dots appear ONLY on milestone days."
        )

# ---------- Products tab ----------
class ProductsFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, width=APP_W, height=APP_H, bg=BG)
        self.pack_propagate(False)

        self.app = self.winfo_toplevel()
        self.pm = getattr(self.app, "_product_manager", None) or ProductManager()
        self.app._product_manager = self.pm

        if not hasattr(self.app, "_profile"):
            self.app._profile = {"completed": False, "username": "User", "skin_type": None, "goal": None}
        if not hasattr(self.app, "_plan"):
            self.app._plan = []

        banner(self, "Products & Plan")
        _, body_inner = make_card(self, pad=(12, 12, 12, 8))
        self.body = tk.Frame(body_inner, bg=SURFACE)
        self.body.pack(fill="both", expand=True)

        self.render()
        if not self.app._profile["completed"]:
            self.after(50, lambda: self.open_quiz(keep_plan=False))

    def pick_start_date(self):
        dlg = tk.Toplevel(self); dlg.title("Plan start date"); dlg.configure(bg=SURFACE)
        tk.Label(dlg, text="Choose when your plan streak starts:", bg=SURFACE).grid(
            row=0, column=0, columnspan=3, padx=10, pady=(10, 4))
        today = date.today()
        yv = tk.IntVar(value=today.year); mv = tk.IntVar(value=today.month); dv = tk.IntVar(value=today.day)
        tk.Label(dlg, text="Year", bg=SURFACE).grid(row=1, column=0, padx=6, pady=2, sticky="e")
        tk.Spinbox(dlg, from_=2000, to=2100, width=6, textvariable=yv).grid(row=1, column=1, padx=6, pady=2, sticky="w")
        tk.Label(dlg, text="Month", bg=SURFACE).grid(row=2, column=0, padx=6, pady=2, sticky="e")
        tk.Spinbox(dlg, from_=1, to=12, width=4, textvariable=mv).grid(row=2, column=1, padx=6, pady=2, sticky="w")
        tk.Label(dlg, text="Day", bg=SURFACE).grid(row=3, column=0, padx=6, pady=2, sticky="e")
        tk.Spinbox(dlg, from_=1, to=31, width=4, textvariable=dv).grid(row=3, column=1, padx=6, pady=2, sticky="w")

        def save():
            try:
                sd = date(int(yv.get()), int(mv.get()), int(dv.get()))
            except Exception:
                messagebox.showerror("Invalid date", "Please enter a valid date."); return
            self.app._plan_start = sd
            messagebox.showinfo("Plan start", f"Plan start set to {sd.isoformat()}.")
            if hasattr(self.app, "_home_ref") and self.app._home_ref.winfo_exists():
                self.app._home_ref._refresh_all_markers()
            dlg.destroy()

        PillButton(dlg, "Save", primary=True, command=save).grid(row=4, column=0, columnspan=2, pady=10)
        dlg.grab_set(); dlg.wait_window()

    def recommend_for(self, skin_type: str, goal: str):
        if skin_type == "dry":
            pA = ("Product A", "hydration / barrier"); pB = ("Product B", "deep moisture")
            am_order = [pA]; pm_order = [pA, pB]
        elif skin_type == "oily":
            pA = ("Product A", "oil-control / clarify"); pB = ("Product B", "lightweight moisture")
            am_order = [pA]; pm_order = [pA, pB]
        else:
            pA = ("Product A", "mild balance"); pB = ("Product B", "balanced hydration")
            am_order = [pA]; pm_order = [pB]

        goal_times_am = 1; goal_times_pm = 1
        if goal == "acne": pm_order = [pA, pB]
        elif goal == "hydration": goal_times_pm = 2
        elif goal == "brightening": am_order = [pA]; pm_order = [pB]
        elif goal == "sensitivity": am_order = []; pm_order = [pA, pB]
        elif goal == "antiaging": pm_order = [pB, pA]

        products = [pA, pB]; plan = []
        for prod in am_order: plan.append({"step": prod[0], "time": "AM", "times": goal_times_am})
        for prod in pm_order: plan.append({"step": prod[0], "time": "PM", "times": goal_times_pm})
        return {"products": products, "plan": plan}

    def sync_plan_with_products(self):
        names = {p["name"] for _, p in self.pm.products.items()}
        self.app._plan = [s for s in self.app._plan if s.get("step") in names]

    def clean_and_render(self):
        self.sync_plan_with_products()
        self.render()
        if hasattr(self.app, "_home_ref") and self.app._home_ref.winfo_exists():
            self.app._home_ref.refresh_sidebar()
            self.app._home_ref._refresh_all_markers()

    def render(self):
        for w in self.body.winfo_children():
            w.destroy()

        prof = self.app._profile; plan = self.app._plan

        card = tk.Frame(self.body, bg=SURFACE, highlightthickness=1, highlightbackground=GRAY)
        card.pack(fill="x", pady=(0, 8))
        t1 = prof["skin_type"] or "—"; g1 = (prof["goal"] or "—").replace("_", " ")
        tk.Label(card, text=f"Profile: skin type = {t1}   •   goal = {g1}",
                 bg=SURFACE, fg=TXT, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=8, pady=8)

        prods_card = tk.Frame(self.body, bg=SURFACE, highlightthickness=1, highlightbackground=GRAY)
        prods_card.pack(fill="x", pady=6)
        tk.Label(prods_card, text="Recommended products", bg=SURFACE, fg=TXT,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=8, pady=(8, 4))

        prods = list(sorted(self.pm.products.items()))[:2]
        if not prods:
            tk.Label(prods_card, text="No products yet. Take the quiz to get recommendations.",
                     bg=SURFACE, fg=TXT_MUTED).pack(anchor="w", padx=8, pady=(0, 8))
        else:
            def color_for(name):
                names = []
                for s in plan:
                    nm = s.get("step")
                    if nm and nm not in names: names.append(nm)
                if name in names:
                    idx = names.index(name); return PRODUCT_COLORS[idx % len(PRODUCT_COLORS)]
                return "#D1D5DB"

            for pid, p in prods:
                row = tk.Frame(prods_card, bg=SURFACE); row.pack(fill="x", padx=8, pady=(6, 2))

                left = tk.Frame(row, bg=SURFACE); left.pack(side="left", anchor="w")
                tk.Label(left, text=p["name"], bg=SURFACE, fg=TXT, font=("Segoe UI", 10, "bold")).pack(anchor="w")
                tk.Label(left, text=p.get("desc", "— (edit me)"), bg=SURFACE, fg=TXT_MUTED, font=("Segoe UI", 9)).pack(anchor="w")

                right = tk.Frame(row, bg=SURFACE); right.pack(side="right", anchor="e")
                tier = self.pm.calc_discount(p["total"], p["streak"])
                disc_txt = f"eligible {tier}% discount" if tier > 0 else "no discount"
                tk.Label(right, text=f"{disc_txt}", bg=SURFACE, fg=("#16A34A" if tier > 0 else TXT_MUTED),
                         font=("Segoe UI", 9)).pack(anchor="e")
                tk.Label(right, text=f"Remaining {p['remaining']}/{p['total']}", bg=SURFACE, fg=TXT_MUTED,
                         font=("Segoe UI", 9)).pack(anchor="e")

                line2 = tk.Frame(prods_card, bg=SURFACE); line2.pack(fill="x", padx=8, pady=(0, 6))

                def on_set_total(product_id=pid):
                    p0 = self.pm.products[product_id]
                    old_total = int(p0["total"]); old_remaining = int(p0["remaining"])
                    used = max(0, old_total - old_remaining)
                    new_total = simpledialog.askinteger(
                        "Set total usages", f"Enter total usages for {p0['name']} (current {old_total}):",
                        parent=self, minvalue=1, maxvalue=365, initialvalue=old_total
                    )
                    if new_total:
                        p0["total"] = int(new_total)
                        p0["remaining"] = max(0, int(new_total) - used)
                        self.clean_and_render()

                PillButton(line2, "Set total", command=on_set_total).pack(side="left", padx=(0, 8))

                state_lbl = tk.Label(line2, text=("Purchased" if p["purchased"] else "Not purchased"),
                                     bg=SURFACE, fg=("#059669" if p["purchased"] else "#9CA3AF"))
                state_lbl.pack(side="left")

                def do_buy(i=pid, lab=state_lbl):
                    self.pm.toggle_purchased(i, True); lab.config(text="Purchased", fg="#059669")

                PillButton(line2, "Buy", command=do_buy).pack(side="left", padx=(10, 0))

                tk.Frame(line2, bg=SURFACE).pack(side="left", expand=True, fill="x")
                dot = tk.Canvas(line2, width=12, height=12, bg=SURFACE, highlightthickness=0)
                dot.pack(side="right"); dot.create_oval(3, 3, 9, 9, fill=color_for(p["name"]), outline="")

        plan_card = tk.Frame(self.body, bg=SURFACE, highlightthickness=1, highlightbackground=GRAY)
        plan_card.pack(fill="x", pady=6)

        header = tk.Frame(plan_card, bg=SURFACE); header.pack(fill="x", padx=8, pady=(8, 4))
        tk.Label(header, text="Daily plan", bg=SURFACE, fg=TXT, font=("Segoe UI", 12, "bold")).pack(side="left")
        PillButton(header, "START", command=self.pick_start_date).pack(side="right")

        if not self.app._plan:
            tk.Label(plan_card, text="No plan yet. Create one after the quiz.",
                     bg=SURFACE, fg=TXT_MUTED).pack(anchor="w", padx=8, pady=(0, 8))
        else:
            for step in self.app._plan:
                tk.Label(plan_card, text=f"{step['time']} • {step['step']} ×{step['times']}",
                         bg=SURFACE, fg=TXT).pack(anchor="w", padx=8, pady=2)

        actions_wrap = tk.Frame(self.body, bg=BG); actions_wrap.pack(fill="x", padx=0, pady=(4, 8))
        actions_card = tk.Frame(actions_wrap, bg=SURFACE, highlightthickness=1, highlightbackground=GRAY)
        actions_card.pack(fill="x")

        tk.Label(actions_card, text="Actions", bg=SURFACE, fg=TXT, font=("Segoe UI", 11, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", padx=8, pady=(8, 4))
        for c in range(2): actions_card.grid_columnconfigure(c, weight=1, uniform="actions")
        actions_card.grid_rowconfigure(1, weight=1, uniform="actions")
        PillButton(actions_card, "ADJUST PLAN", command=self.adjust_plan_dialog).grid(row=1, column=0, padx=8, pady=6, sticky="nsew")
        PillButton(actions_card, "REDO QUIZ", command=self.redo_quiz_with_choice).grid(row=1, column=1, padx=8, pady=6, sticky="nsew")

    # ---------- Quiz ----------
    def redo_quiz_with_choice(self):
        if self.app._plan:
            keep = messagebox.askyesno("Redo quiz", "Keep current plan?\nYes = keep\nNo = overwrite")
        else:
            keep = False
        self.open_quiz(keep_plan=keep)

    def open_quiz(self, keep_plan=True):
        dlg = tk.Toplevel(self); dlg.title("Skincare quiz"); dlg.configure(bg=SURFACE)
        tk.Label(dlg, text="Skincare Quiz", bg=SURFACE, fg=TXT, font=("Segoe UI", 12, "bold")).pack(pady=8)

        q1=q2=q3=q4=q5=q6=None
        q1=tk.StringVar(value="none"); q2=tk.StringVar(value="none")
        q3=tk.StringVar(value="none"); q4=tk.StringVar(value="none")
        q5=tk.StringVar(value="none"); q6=tk.StringVar(value="none")

        tk.Label(dlg, text="How does your skin feel before washing or applying product?",fg= "black", bg=SURFACE).pack(anchor="w", padx=10)
        for txt, val in [("Tight / dry","dry"),("Oily","oily"),("Normal","normal")]:
            tk.Radiobutton(dlg, text=txt, variable=q1, value=val, fg= "black", bg=SURFACE).pack(anchor="w", padx=20)

        tk.Label(dlg, text="How does your skin feel after washing?", fg= "black", bg=SURFACE).pack(anchor="w", padx=10, pady=(6,0))
        for txt, val in [("Tight / dry","dry"),("Oily","oily"),("Normal","normal")]:
            tk.Radiobutton(dlg, text=txt, variable=q2, value=val, fg= "black", bg=SURFACE).pack(anchor="w", padx=20)

        tk.Label(dlg, text="By the end of the day, your skin looks…", fg= "black", bg=SURFACE).pack(anchor="w", padx=10, pady=(6,0))
        for txt, val in [("Flaky / rough","dry"),("Greasy","oily"),("Matte","normal")]:
            tk.Radiobutton(dlg, text=txt, variable=q3, value=val, fg= "black", bg=SURFACE).pack(anchor="w", padx=20)

        tk.Label(dlg, text="How often do you get breakouts?",fg= "black", bg=SURFACE).pack(anchor="w", padx=10, pady=(6,0))
        for txt, val in [("Rarely","dry"),("Sometimes","normal"),("Often","oily")]:
            tk.Radiobutton(dlg, text=txt, variable=q4, value=val, fg= "black", bg=SURFACE).pack(anchor="w", padx=20)

        tk.Label(dlg, text="What is your age group?", fg= "black", bg=SURFACE).pack(anchor="w", padx=10, pady=(6,0))
        for txt, val in [("Under 18","teen"),("18–25","young_adult"),("26–40","adult"),("41+","mature")]:
            tk.Radiobutton(dlg, text=txt, variable=q5, value=val, fg= "black", bg=SURFACE).pack(anchor="w", padx=20)

        tk.Label(dlg, text="What do you most want to improve?", fg= "black", bg=SURFACE).pack(anchor="w", padx=10, pady=(6,0))
        for txt, val in [
            ("Reduce acne / breakouts","acne"),
            ("Control oil / shine","oil_control"),
            ("Hydrate / reduce dryness","hydration"),
            ("Brighten / reduce dark spots","brightening"),
            ("Soothing sensitivity / redness","sensitivity"),
            ("Anti-aging (fine lines / firmness)","antiaging")
        ]:
            tk.Radiobutton(dlg, text=txt, variable=q6, value=val, fg= "black", bg=SURFACE).pack(anchor="w", padx=20)

        def submit():
            answers = [q1.get(), q2.get(), q3.get(), q4.get(), q5.get(), q6.get()]
            if "" in answers or "none" in answers:
                messagebox.showwarning("Incomplete", "Please answer all questions."); return

            dry = [q1.get(), q2.get(), q3.get(), q4.get()].count("dry")
            oily = [q1.get(), q2.get(), q3.get(), q4.get()].count("oily")
            normal = [q1.get(), q2.get(), q3.get(), q4.get()].count("normal")
            skin_type = "dry" if (dry > oily and dry > normal) else ("oily" if (oily > dry and oily > normal) else "normal")

            self.app._profile.update({"completed": True, "skin_type": skin_type, "goal": q6.get()})
            self.seed_recommendations()
            if (not keep_plan) or (not self.app._plan):
                self.seed_plan()

            messagebox.showinfo("Quiz result", f"Skin type: {skin_type}\nGoal: {q6.get().replace('_',' ')}")
            dlg.destroy(); self.clean_and_render()

        PillButton(dlg, "Submit", primary=True, fg= "black", command=submit).pack(pady=10)
        dlg.grab_set(); dlg.wait_window()

    def seed_recommendations(self):
        ST = self.app._profile.get("skin_type") or "normal"
        GO = self.app._profile.get("goal") or "hydration"
        rec = self.recommend_for(ST, GO)
        self.pm.products.clear(); self.pm._next_id = 1
        for name, desc in rec["products"]:
            self.pm.add(name, total=30, desc=desc)
        if hasattr(self.app, "_home_ref") and self.app._home_ref.winfo_exists():
            self.app._home_ref.refresh_sidebar(); self.app._home_ref._refresh_all_markers()

    def seed_plan(self):
        ST = self.app._profile.get("skin_type") or "normal"
        GO = self.app._profile.get("goal") or "hydration"
        rec = self.recommend_for(ST, GO)
        self.app._plan = rec["plan"]
        if hasattr(self.app, "_home_ref") and self.app._home_ref.winfo_exists():
            self.app._home_ref.refresh_sidebar(); self.app._home_ref._refresh_all_markers()

    # ---------- adjust dialogs ----------
    def adjust_products_dialog(self):
        dlg = tk.Toplevel(self); dlg.title("Adjust products"); dlg.configure(bg=SURFACE)
        tk.Label(dlg, text="Add new product (name):", bg=SURFACE).pack(padx=10, pady=(10, 2))
        ent = tk.Entry(dlg); ent.pack(padx=10)
        tk.Label(dlg, text="Total usages (default 30):", bg=SURFACE).pack(padx=10, pady=(6, 2))
        ent2 = tk.Entry(dlg); ent2.insert(0, "30"); ent2.pack(padx=10)
        tk.Label(dlg, text="Short description:", bg=SURFACE).pack(padx=10, pady=(6, 2))
        ent3 = tk.Entry(dlg); ent3.insert(0, "— (edit me)"); ent3.pack(padx=10)

        def add_new():
            name = ent.get().strip()
            try: total = int(ent2.get().strip())
            except: total = 30
            desc = ent3.get().strip() or "— (edit me)"
            if name:
                self.pm.add(name, total, desc=desc); dlg.destroy(); self.clean_and_render()

        PillButton(dlg, "Add", primary=True, command=add_new).pack(pady=10)

    def adjust_plan_dialog(self):
        plan = self.app._plan
        if not plan:
            messagebox.showinfo("Adjust plan", "No plan yet. Take the quiz first."); return

        dlg = tk.Toplevel(self); dlg.title("Adjust daily plan"); dlg.configure(bg=SURFACE)
        tk.Label(dlg, text="Edit order, times per day, and when to use.", bg=SURFACE).pack(anchor="w", padx=10, pady=8)

        holder = tk.Frame(dlg, bg=SURFACE); holder.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        items = [dict(step=s["step"], time=s.get("time", "AM"), times=int(s.get("times", 1))) for s in plan]
        rows = []; time_choices = ["AM", "PM", "Evening", "Custom"]

        def rebuild_rows():
            for w in holder.winfo_children(): w.destroy()
            rows.clear()
            for idx, s in enumerate(items):
                row = tk.Frame(holder, bg=SURFACE, highlightthickness=1, highlightbackground=GRAY)
                row.pack(fill="x", pady=4)

                tk.Label(row, text=s["step"], bg=SURFACE, fg=TXT, font=("Segoe UI", 10, "bold")).grid(
                    row=0, column=0, sticky="w", padx=6, pady=(6, 0), columnspan=4)

                tk.Label(row, text="Times:", bg=SURFACE, fg=TXT_MUTED).grid(row=1, column=0, sticky="w", padx=6)
                times_var = tk.StringVar(value=str(s["times"]))
                tk.Spinbox(row, from_=1, to=5, width=5, textvariable=times_var).grid(row=1, column=1, sticky="w", padx=6)

                tk.Label(row, text="When:", bg=SURFACE, fg=TXT_MUTED).grid(row=1, column=2, sticky="w", padx=(16, 6))
                time_var = tk.StringVar(value=s["time"] if s["time"] in time_choices else "Custom")
                tk.OptionMenu(row, time_var, *time_choices).grid(row=1, column=3, sticky="w")

                custom_var = tk.StringVar(value="" if time_var.get() != "Custom" else s["time"])
                tk.Entry(row, width=10, textvariable=custom_var).grid(row=1, column=4, sticky="w", padx=6)
                time_var.trace_add("write", lambda *_ , tv=time_var, cv=custom_var: cv.set("" if tv.get()!="Custom" else cv.get()))

                btns = tk.Frame(row, bg=SURFACE); btns.grid(row=0, column=5, rowspan=2, padx=6)
                def move_up(i=idx):
                    if i>0: items[i-1], items[i] = items[i], items[i-1]; rebuild_rows()
                def move_down(i=idx):
                    if i<len(items)-1: items[i+1], items[i] = items[i], items[i+1]; rebuild_rows()
                PillButton(btns, "↑", command=move_up).pack(side="top", pady=2)
                PillButton(btns, "↓", command=move_down).pack(side="top", pady=2)

                rows.append((times_var, time_var, custom_var, idx))

        def add_product():
            sub = tk.Toplevel(dlg); sub.title("Add product"); sub.configure(bg=SURFACE)
            tk.Label(sub, text="Product name:", bg=SURFACE).grid(row=0, column=0, sticky="w", padx=8, pady=(10, 2))
            name_e = tk.Entry(sub, width=28); name_e.grid(row=0, column=1, padx=8, pady=(10, 2))
            tk.Label(sub, text="Total usages (default 30):", bg=SURFACE).grid(row=1, column=0, sticky="w", padx=8, pady=2)
            total_e = tk.Entry(sub, width=10); total_e.insert(0, "30"); total_e.grid(row=1, column=1, sticky="w", padx=8, pady=2)
            tk.Label(sub, text="Short description:", bg=SURFACE).grid(row=2, column=0, sticky="w", padx=8, pady=2)
            desc_e = tk.Entry(sub, width=28); desc_e.insert(0, "— (edit me)"); desc_e.grid(row=2, column=1, padx=8, pady=2)
            tk.Label(sub, text="When to use:", bg=SURFACE).grid(row=3, column=0, sticky="w", padx=8, pady=(8, 2))
            when_v = tk.StringVar(value="PM"); tk.OptionMenu(sub, when_v, "AM","PM","Evening","Custom").grid(row=3, column=1, sticky="w", padx=8, pady=(8, 2))
            tk.Label(sub, text="Custom time (if Custom):", bg=SURFACE).grid(row=4, column=0, sticky="w", padx=8, pady=2)
            custom_e = tk.Entry(sub, width=12); custom_e.grid(row=4, column=1, sticky="w", padx=8, pady=2)
            tk.Label(sub, text="Times per day:", bg=SURFACE).grid(row=5, column=0, sticky="w", padx=8, pady=2)
            times_e = tk.Entry(sub, width=6); times_e.insert(0, "1"); times_e.grid(row=5, column=1, sticky="w", padx=8, pady=2)

            def do_ok():
                name = (name_e.get() or "").strip()
                if not name: messagebox.showwarning("Add product", "Please enter a product name."); return
                try: total = int((total_e.get() or "30").strip())
                except: total = 30
                desc = (desc_e.get() or "— (edit me)").strip()
                when = when_v.get()
                try: times = int((times_e.get() or "1").strip())
                except: times = 1
                when_final = custom_e.get().strip() if when == "Custom" else when
                if any(p["name"] == name for p in self.pm.products.values()):
                    messagebox.showwarning("Add product", "This product name already exists."); return
                self.pm.add(name, total, desc=desc)
                items.append({"step": name, "time": when_final, "times": max(1, times)})
                rebuild_rows(); sub.destroy()

            PillButton(sub, "Add", primary=True, command=do_ok).grid(row=6, column=0, columnspan=2, pady=10)
            sub.grab_set(); sub.wait_window()

        def replace_product():
            current_names = []
            for s in items:
                if s["step"] not in current_names: current_names.append(s["step"])
            if not current_names:
                messagebox.showinfo("Replace", "No products in plan to replace."); return
            sub = tk.Toplevel(dlg); sub.title("Replace product"); sub.configure(bg=SURFACE)
            tk.Label(sub, text="New product name:", bg=SURFACE).grid(row=0, column=0, sticky="w", padx=8, pady=(10,2))
            name_e = tk.Entry(sub, width=28); name_e.grid(row=0, column=1, padx=8, pady=(10,2))
            tk.Label(sub, text="Total usages (default 30):", bg=SURFACE).grid(row=1, column=0, sticky="w", padx=8, pady=2)
            total_e = tk.Entry(sub, width=10); total_e.insert(0,"30"); total_e.grid(row=1, column=1, sticky="w", padx=8, pady=2)
            tk.Label(sub, text="Short description:", bg=SURFACE).grid(row=2, column=0, sticky="w", padx=8, pady=2)
            desc_e = tk.Entry(sub, width=28); desc_e.insert(0,"— (edit me)"); desc_e.grid(row=2, column=1, padx=8, pady=2)
            tk.Label(sub, text="Replace which existing product?", bg=SURFACE).grid(row=3, column=0, sticky="w", padx=8, pady=(8,2))
            choice = tk.StringVar(value=current_names[0]); tk.OptionMenu(sub, choice, *current_names).grid(row=3, column=1, sticky="w", padx=8, pady=(8,2))
            def do_ok():
                new_name = (name_e.get() or "").strip()
                if not new_name: messagebox.showwarning("Replace", "Please enter a product name."); return
                try: total = int((total_e.get() or "30").strip())
                except: total = 30
                desc = (desc_e.get() or "— (edit me)").strip()
                old_name = choice.get(); old_pid = None
                for pid, p in list(self.pm.products.items()):
                    if p["name"] == old_name: old_pid = pid; break
                if old_pid is not None: self.pm.remove(old_pid)
                self.pm.add(new_name, total, desc=desc)
                for s in items:
                    if s["step"] == old_name: s["step"] = new_name
                rebuild_rows(); sub.destroy()
            PillButton(sub, "OK", primary=True, command=do_ok).grid(row=4, column=0, columnspan=2, pady=10)
            sub.grab_set(); sub.wait_window()

        def delete_product_from_plan():
            names = []
            for s in items:
                nm = s["step"];
                if nm not in names: names.append(nm)
            if not names:
                messagebox.showinfo("Delete", "No products in plan to delete."); return
            sub = tk.Toplevel(dlg); sub.title("Delete product"); sub.configure(bg=SURFACE)
            tk.Label(sub, text="Select products to delete from plan (and remove from Products):",
                     bg=SURFACE).pack(anchor="w", padx=10, pady=(10,6))
            checks = {}
            for nm in names:
                v = tk.BooleanVar(value=False); checks[nm] = v
                tk.Checkbutton(sub, text=nm, variable=v, bg=SURFACE).pack(anchor="w", padx=16)
            def do_delete():
                selected = [nm for nm, v in checks.items() if v.get()]
                if not selected: sub.destroy(); return
                items[:] = [it for it in items if it["step"] not in selected]
                for pid, p in list(self.pm.products.items()):
                    if p["name"] in selected: self.pm.remove(pid)
                rebuild_rows(); sub.destroy()
            PillButton(sub, "Delete", primary=True, command=do_delete).pack(pady=10)
            sub.grab_set(); sub.wait_window()

        rebuild_rows()

        footer = tk.Frame(dlg, bg=SURFACE); footer.pack(fill="x", padx=10, pady=(0,10))
        PillButton(footer, "Add product…", command=add_product).pack(side="left", padx=(0,6))
        PillButton(footer, "Replace product…", command=replace_product).pack(side="left", padx=(0,6))
        PillButton(footer, "Delete product…", command=delete_product_from_plan).pack(side="left")

        def save():
            for times_var, time_var, custom_var, idx in rows:
                try: items[idx]["times"] = int(times_var.get())
                except: items[idx]["times"] = 1
                tchoice = time_var.get()
                items[idx]["time"] = custom_var.get().strip() if tchoice == "Custom" else tchoice
            self.app._plan = [{"step": s["step"], "time": s["time"], "times": s["times"]} for s in items]
            dlg.destroy(); self.clean_and_render()
            if hasattr(self.app, "_home_ref") and self.app._home_ref.winfo_exists():
                self.app._home_ref.refresh_sidebar(); self.app._home_ref._refresh_all_markers()

        PillButton(footer, "Save", primary=True, command=save).pack(side="right")

# ---------- other tabs ----------
class ExploreFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, width=APP_W, height=APP_H, bg=BG)
        self.pack_propagate(False)
        tk.Label(self, text="Explore (placeholder)", bg=BG, fg=TXT, font=("Segoe UI", 20, "bold")).pack(pady=24)
        tk.Label(self, text="Search/browse features go here.", bg=BG, fg=TXT_MUTED).pack()

class SettingsFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, width=APP_W, height=APP_H, bg=BG)
        self.pack_propagate(False)
        tk.Label(self, text="Settings (placeholder)", bg=BG, fg=TXT, font=("Segoe UI", 20, "bold")).pack(pady=24)
        tk.Label(self, text="Profile and preferences.", bg=BG, fg=TXT_MUTED).pack()

# ---------- app shell ----------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Skinovate (Prototype)")
        self.geometry(f"{APP_W}x{APP_H}")
        self.resizable(False, False)

        self._current = None
        self._container = None
        self._page_frame = None
        self._nav = None
        self._product_manager = ProductManager()

        self.show_login()

    def _swap(self, widget):
        if self._current: self._current.destroy()
        if self._container:
            self._container.destroy(); self._container = None
        self._page_frame = None; self._nav = None
        self._current = widget; self._current.pack(fill="both", expand=True)

    def show_login(self):
        self._swap(LoginFrame(self, on_success=self.show_home))

    def show_home(self):
        if self._current:
            self._current.destroy(); self._current = None
        self._build_shell("home")

    def _build_shell(self, page="home"):
        if self._container: self._container.destroy()
        self._container = tk.Frame(self, bg=BG, width=APP_W, height=APP_H)
        self._container.pack(fill="both", expand=True)
        self._container.grid_rowconfigure(0, weight=1)
        self._container.grid_rowconfigure(1, weight=0)
        self._container.grid_columnconfigure(0, weight=1)

        self._page_frame = tk.Frame(self._container, bg=BG)
        self._page_frame.grid(row=0, column=0, sticky="nsew")

        self._nav = NavBar(self._container, on_select=self._on_nav_select)
        self._nav.grid(row=1, column=0, sticky="ew")
        self._switch_to(page)

    def _on_nav_select(self, idx):
        key = ["home", "products", "explore", "settings"][idx]
        self._switch_to(key)

    def _switch_to(self, key):
        for w in self._page_frame.winfo_children(): w.destroy()
        if key == "home":
            frame = CalendarHomeFrame(self._page_frame)
            if hasattr(self, "_plan_start"): frame.plan_start = self._plan_start
            frame.pack(fill="both", expand=True)
            self._home_ref = frame
            active_idx = 0
        elif key == "products":
            ProductsFrame(self._page_frame).pack(fill="both", expand=True); active_idx = 1
        elif key == "explore":
            ExploreFrame(self._page_frame).pack(fill="both", expand=True); active_idx = 2
        else:
            SettingsFrame(self._page_frame).pack(fill="both", expand=True); active_idx = 3
        self._nav.set_active(active_idx)

if __name__ == "__main__":
    App().mainloop()
