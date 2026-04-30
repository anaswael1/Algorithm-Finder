import customtkinter as ctk

class AddView(ctk.CTkFrame):
    def __init__(self, parent, db, app_ptr):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.app_ptr = app_ptr

        # Back Button & Title
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=10)
        ctk.CTkButton(header, text="← Back", width=80, command=self.app_ptr.show_search_view).pack(side="left")
        ctk.CTkLabel(header, text="Add New Algorithm", font=("Inter", 22, "bold")).pack(expand=True)

        self.name_entry = ctk.CTkEntry(self, placeholder_text="Algorithm Name", width=500)
        self.name_entry.pack(pady=10)

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(pady=5)
        self.comp_entry = ctk.CTkEntry(row, placeholder_text="Complexity", width=245)
        self.comp_entry.pack(side="left", padx=5)
        self.tags_entry = ctk.CTkEntry(row, placeholder_text="Tags", width=245)
        self.tags_entry.pack(side="left", padx=5)

        # --- A LOT BIGGER Code Box (Height 420) ---
        ctk.CTkLabel(self, text="Source Code:", font=("Inter", 12, "bold")).pack(anchor="w", padx=100)
        self.code_text = ctk.CTkTextbox(self, width=700, height=420, border_width=1)
        self.code_text.pack(pady=10)

        self.save_btn = ctk.CTkButton(self, text="Save Algorithm", height=45, fg_color="#2ecc71", command=self.save_data)
        self.save_btn.pack(pady=10)

    def save_data(self):
        name, code = self.name_entry.get(), self.code_text.get("0.0", "end").strip()
        if name and code:
            all_algos = self.db.get_all()
            all_algos.append({"name": name, "code": code, "tags": [t.strip() for t in self.tags_entry.get().split(",")], "complexity": self.comp_entry.get(), "is_favorite": False})
            self.db.save(all_algos)
            self.app_ptr.show_search_view()

class EditView(ctk.CTkFrame):
    def __init__(self, parent, db, algo_to_edit, app_ptr):
        super().__init__(parent, fg_color="transparent")
        self.db, self.app_ptr, self.old_name, self.current_algo = db, app_ptr, algo_to_edit['name'], algo_to_edit

        ctk.CTkLabel(self, text=f"Editing: {self.old_name}", font=("Inter", 22, "bold")).pack(pady=10)

        self.name_ent = self.create_row("Name:", algo_to_edit['name'])
        self.comp_ent = self.create_row("Complexity:", algo_to_edit.get('complexity', ""))
        self.tags_ent = self.create_row("Tags:", ", ".join(algo_to_edit.get('tags', [])))

        # --- LITTLE BIT BIGGER Code Box (Height 320) ---
        ctk.CTkLabel(self, text="Source Code:", font=("Inter", 12, "bold")).pack(anchor="w", padx=100)
        self.code_box = ctk.CTkTextbox(self, width=700, height=320, font=("Consolas", 13))
        self.code_box.insert("0.0", algo_to_edit['code'])
        self.code_box.pack(pady=10)

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(pady=15)
        ctk.CTkButton(btns, text="Delete", fg_color="#e74c3c", width=180, height=45, font=("Inter", 14, "bold"), command=self.pop_delete).pack(side="left", padx=10)
        ctk.CTkButton(btns, text="Save Changes", fg_color="#2ecc71", width=180, height=45, font=("Inter", 14, "bold"), command=self.pop_save).pack(side="left", padx=10)

    def create_row(self, lbl, val):
        r = ctk.CTkFrame(self, fg_color="transparent")
        r.pack(pady=4, fill="x", padx=100)
        ctk.CTkLabel(r, text=lbl, width=150, anchor="w").pack(side="left")
        e = ctk.CTkEntry(r, width=400); e.insert(0, val); e.pack(side="left"); return e

    # --- BETTER CENTERING LOGIC ---
    def center_popup(self, win, w=400, h=220):
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (w // 2)
        y = (win.winfo_screenheight() // 2) - (h // 2) - 50
        win.geometry(f"{w}x{h}+{x}+{y}")
        win.grab_set()

    def pop_delete(self):
        pop = ctk.CTkToplevel(self); pop.title("Delete?"); self.center_popup(pop)
        ctk.CTkLabel(pop, text="Delete this algorithm?", font=("Inter", 18, "bold")).pack(pady=30)
        b = ctk.CTkFrame(pop, fg_color="transparent"); b.pack()
        ctk.CTkButton(b, text="Cancel", fg_color="gray30", command=pop.destroy).pack(side="left", padx=5)
        ctk.CTkButton(b, text="Delete", fg_color="#e74c3c", command=lambda: self.do_del(pop)).pack(side="left", padx=5)

    def do_del(self, p):
        self.db.save([a for a in self.db.get_all() if a['name'] != self.old_name])
        p.destroy(); self.app_ptr.show_search_view()

    def pop_save(self):
        pop = ctk.CTkToplevel(self); pop.title("Save?"); self.center_popup(pop)
        ctk.CTkLabel(pop, text="Save changes?", font=("Inter", 18, "bold")).pack(pady=30)
        b = ctk.CTkFrame(pop, fg_color="transparent"); b.pack()
        ctk.CTkButton(b, text="Cancel", fg_color="gray30", command=pop.destroy).pack(side="left", padx=5)
        ctk.CTkButton(b, text="Save", fg_color="#2ecc71", command=lambda: self.do_save(pop)).pack(side="left", padx=5)

    def do_save(self, p):
        data = self.db.get_all()
        new_algo = {"name": self.name_ent.get(), "code": self.code_box.get("0.0", "end").strip(), "complexity": self.comp_ent.get(), "tags": [t.strip() for t in self.tags_ent.get().split(",")], "is_favorite": self.current_algo.get('is_favorite', False)}
        for i, a in enumerate(data):
            if a['name'] == self.old_name: data[i] = new_algo; break
        self.db.save(data); p.destroy(); self.app_ptr.show_search_view(); self.app_ptr.current_view.open_detail_view(new_algo)