import customtkinter as ctk
from utils import apply_syntax_highlighting

class EditView(ctk.CTkFrame):
    def __init__(self, parent, db, algo_to_edit, app_ptr):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.app_ptr = app_ptr
        self.old_name = algo_to_edit['name']
        self.current_algo = algo_to_edit
        self.versions = algo_to_edit.get('versions', []) #[cite: 15]

        # --- HEADER ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(header, text="← Back", width=80, 
                      command=self.app_ptr.show_search_view).pack(side="left")
        
        ctk.CTkLabel(header, text=f"Editing: {self.old_name}", 
                     font=("Inter", 22, "bold")).pack(expand=True)

        # Meta Rows[cite: 15]
        self.name_ent = self.create_row("Name:", algo_to_edit['name'])
        self.comp_ent = self.create_row("Complexity:", algo_to_edit.get('complexity', ""))
        self.tags_ent = self.create_row("Tags:", ", ".join(algo_to_edit.get('tags', [])))

        # --- VERSION CONTROL ROW ---
        lang_row = ctk.CTkFrame(self, fg_color="transparent")
        lang_row.pack(pady=4, fill="x", padx=100)
        ctk.CTkLabel(lang_row, text="Select Language:", width=150, anchor="w").pack(side="left")
        
        lang_names = [v['lang'] for v in self.versions] #[cite: 15]
        self.lang_selector = ctk.CTkComboBox(lang_row, values=lang_names, width=200, 
                                             command=self.load_version_code, state="readonly")
        self.lang_selector.pack(side="left", padx=5)

        ctk.CTkButton(lang_row, text="+ New", width=70, fg_color="#3498db", 
                      command=self.add_new_language_flow).pack(side="left", padx=5)

        ctk.CTkButton(lang_row, text="Delete Lang", width=110, fg_color="#e67e22", 
                      command=self.pop_delete_version).pack(side="left", padx=5)

        # Code Box[cite: 15]
        ctk.CTkLabel(self, text="Source Code:", font=("Inter", 12, "bold")).pack(anchor="w", padx=100)
        self.code_text_var = "" # Placeholder for logic
        self.code_box = ctk.CTkTextbox(self, width=700, height=320, font=("Consolas", 13))
        self.code_box.pack(pady=10)

        if lang_names:
            self.lang_selector.set(lang_names[0])
            self.load_version_code(lang_names[0])

        # Bottom Buttons[cite: 15]
        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(pady=15)
        ctk.CTkButton(btns, text="Delete Algorithm", fg_color="#e74c3c", width=180, height=45, 
                      command=self.pop_delete).pack(side="left", padx=10)
        ctk.CTkButton(btns, text="Save Changes", fg_color="#2ecc71", width=180, height=45, 
                      command=self.pop_save).pack(side="left", padx=10)
        self.focus()
    # --- POPUP DIALOGS (Centered) ---

    def pop_save(self):
        pop = ctk.CTkToplevel(self) #[cite: 15]
        pop.title("Save Changes?")
        self.center_popup(pop, 400, 165) #[cite: 15]
        
        ctk.CTkLabel(pop, text="Save all changes to this algorithm?", font=("Inter", 16, "bold")).pack(pady=30)
        
        b = ctk.CTkFrame(pop, fg_color="transparent")
        b.pack()
        ctk.CTkButton(b, text="Cancel", fg_color="gray30", command=pop.destroy).pack(side="left", padx=5)
        ctk.CTkButton(b, text="Save", fg_color="#2ecc71", command=lambda: self.do_save(pop)).pack(side="left", padx=5)

    def pop_delete(self):
        pop = ctk.CTkToplevel(self) #[cite: 15]
        pop.title("Delete Algorithm?")
        self.center_popup(pop, 400, 165) #[cite: 15]
        
        ctk.CTkLabel(pop, text="Delete this algorithm and all its versions?", font=("Inter", 16, "bold")).pack(pady=30)
        
        b = ctk.CTkFrame(pop, fg_color="transparent")
        b.pack()
        ctk.CTkButton(b, text="Cancel", fg_color="gray30", command=pop.destroy).pack(side="left", padx=5)
        ctk.CTkButton(b, text="Delete", fg_color="#e74c3c", command=lambda: self.do_del(pop)).pack(side="left", padx=5)

    def pop_delete_version(self):
        lang = self.lang_selector.get()
        if not lang or lang == "": return
        
        pop = ctk.CTkToplevel(self) #[cite: 15]
        pop.title("Delete Language?")
        self.center_popup(pop, 400, 165) #[cite: 15]
        
        ctk.CTkLabel(pop, text=f"Delete the {lang} code version?", font=("Inter", 16, "bold")).pack(pady=30)
        
        b = ctk.CTkFrame(pop, fg_color="transparent")
        b.pack()
        ctk.CTkButton(b, text="Cancel", fg_color="gray30", command=pop.destroy).pack(side="left", padx=5)
        ctk.CTkButton(b, text="Delete", fg_color="#e67e22", command=lambda: self.do_delete_version(lang, pop)).pack(side="left", padx=5)

    # --- LOGIC METHODS ---

    def add_new_language_flow(self):
        """Custom centered dialog to replace CTkInputDialog."""
        pop = ctk.CTkToplevel(self)
        pop.title("New Language")
        self.center_popup(pop, 350, 180)
        
        ctk.CTkLabel(pop, text="Enter Language Name:", font=("Inter", 14, "bold")).pack(pady=15)
        entry = ctk.CTkEntry(pop, width=250)
        entry.pack(pady=5)
        entry.focus()

        def confirm():
            new_lang = entry.get().strip()
            if new_lang:
                current_vals = list(self.lang_selector.cget("values"))
                if new_lang not in current_vals:
                    current_vals.append(new_lang)
                    self.lang_selector.configure(values=current_vals)
                self.lang_selector.set(new_lang)
                self.code_box.delete("0.0", "end")
                pop.destroy()

        btn_b = ctk.CTkFrame(pop, fg_color="transparent")
        btn_b.pack(pady=15)
        ctk.CTkButton(btn_b, text="Add", width=100, command=confirm).pack(side="left", padx=5)
        ctk.CTkButton(btn_b, text="Cancel", width=100, fg_color="gray30", command=pop.destroy).pack(side="left", padx=5)

    def do_save(self, pop_window):
        data = self.db.get_all()
        curr_lang = self.lang_selector.get()
        curr_code = self.code_box.get("0.0", "end").strip()
        
        found = False
        for v in self.versions:
            if v['lang'] == curr_lang:
                v['code'] = curr_code
                found = True
                break
        if not found and curr_lang:
            self.versions.append({"lang": curr_lang, "code": curr_code})

        # Assuming you've added a self.cat_ent field in your EditView UI
        self.current_algo.update({
            "name": self.name_ent.get(),
            "complexity": self.comp_ent.get(),
            "category": self.cat_ent.get().strip() if hasattr(self, 'cat_ent') else self.current_algo.get('category', 'General'),
            "tags": [t.strip() for t in self.tags_ent.get().split(",")] if self.tags_ent.get() else [],
            "versions": self.versions
        })
        
        for i, a in enumerate(data):
            if a['name'] == self.old_name:
                data[i] = self.current_algo
                break
        
        self.db.save(data)
        pop_window.destroy()
        self.app_ptr.show_search_view()

    def do_del(self, pop_window):
        self.db.save([a for a in self.db.get_all() if a['name'] != self.old_name])
        pop_window.destroy()
        self.app_ptr.show_search_view()

    def do_delete_version(self, lang_to_del, pop_window):
        self.versions = [v for v in self.versions if v['lang'] != lang_to_del]
        self.current_algo['versions'] = self.versions
        
        new_langs = [v['lang'] for v in self.versions]
        self.lang_selector.configure(values=new_langs)
        
        if new_langs:
            self.lang_selector.set(new_langs[0])
            self.load_version_code(new_langs[0])
        else:
            self.lang_selector.set("")
            self.code_box.delete("0.0", "end")
            
        pop_window.destroy()

    def load_version_code(self, choice):
        selected = next((v for v in self.versions if v['lang'] == choice), None)
        if selected:
            self.code_box.delete("0.0", "end")
            self.code_box.insert("0.0", selected['code'])
            apply_syntax_highlighting(self.code_box, choice)

    def create_row(self, lbl, val):
        r = ctk.CTkFrame(self, fg_color="transparent")
        r.pack(pady=4, fill="x", padx=100)
        ctk.CTkLabel(r, text=lbl, width=150, anchor="w").pack(side="left")
        e = ctk.CTkEntry(r, width=400)
        e.insert(0, val)
        e.pack(side="left")
        return e

    def center_popup(self, win, w, h):
        """Centers the popup window relative to the main application window."""
        win.update_idletasks() #[cite: 15]
        
        # Get parent coordinates to center relative to app window
        parent = self.winfo_toplevel()
        main_x = parent.winfo_x()
        main_y = parent.winfo_y()
        main_w = parent.winfo_width()
        main_h = parent.winfo_height()
        
        # Calculate coordinates[cite: 15]
        x = main_x + (main_w // 2) - (w // 2)
        y = main_y + (main_h // 2) - (h // 2) - 20
        
        win.geometry(f"{w}x{h}+{x}+{y}")
        win.grab_set() #[cite: 15]