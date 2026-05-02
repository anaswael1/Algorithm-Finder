import customtkinter as ctk
from utils import apply_syntax_highlighting

class AddView(ctk.CTkFrame):
    def __init__(self, parent, db, app_ptr):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.app_ptr = app_ptr

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=10)
        ctk.CTkButton(header, text="← Back", width=80, command=self.app_ptr.show_search_view).pack(side="left")
        ctk.CTkLabel(header, text="Add New Algorithm", font=("Inter", 22, "bold")).pack(expand=True)

        self.name_entry = ctk.CTkEntry(self, placeholder_text="Algorithm Name", width=500)
        self.name_entry.pack(pady=10)

        # Meta Row with 4 inputs now
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(pady=5)
        
        self.comp_entry = ctk.CTkEntry(row, placeholder_text="Complexity", width=140)
        self.comp_entry.pack(side="left", padx=5)
        
        self.cat_entry = ctk.CTkEntry(row, placeholder_text="Category", width=140)
        self.cat_entry.pack(side="left", padx=5)
        
        self.tags_entry = ctk.CTkEntry(row, placeholder_text="Tags (comma separated)", width=140)
        self.tags_entry.pack(side="left", padx=5)
        
        self.lang_entry = ctk.CTkEntry(row, placeholder_text="Language", width=140)
        self.lang_entry.pack(side="left", padx=5)
        
        # --- NEW BINDINGS FOR LANGUAGE ENTRY ---
        self.lang_entry.bind("<FocusOut>", self.trigger_highlight)
        self.lang_entry.bind("<KeyRelease>", self.trigger_highlight)

        ctk.CTkLabel(self, text="Source Code:", font=("Inter", 12, "bold")).pack(anchor="w", padx=100)
        self.code_text = ctk.CTkTextbox(self, width=700, height=420, border_width=1, font=("Consolas", 13))
        self.code_text.pack(pady=10)
        
        # --- NEW BINDING FOR CODE BOX ---
        self.code_text.bind("<KeyRelease>", self.trigger_highlight)

        self.save_btn = ctk.CTkButton(self, text="Save Code", height=45, fg_color="#34b86b", command=self.save_data)
        self.save_btn.pack(pady=10)
        self.focus()
    
    def trigger_highlight(self, event=None):
        """Highlights the code based on the current language entry."""
        lang = self.lang_entry.get().strip()
        if lang:
            apply_syntax_highlighting(self.code_text, lang)

    def perform_final_save(self, name, code, lang, algo_list):
        algo_list.append({
            "name": name,
            "complexity": self.comp_entry.get() or "N/A",
            "category": self.cat_entry.get().strip() or "General",
            "tags": [t.strip() for t in self.tags_entry.get().split(",")] if self.tags_entry.get() else [],
            "is_favorite": False,
            "versions": [{"lang": lang, "code": code}]
        })
        self.db.save(algo_list)
        self.app_ptr.show_search_view()

    def save_data(self):
        name = self.name_entry.get().strip()
        code = self.code_text.get("0.0", "end").strip()
        lang = self.lang_entry.get().strip()
        
        if name and code and lang:
            all_algos = self.db.get_all()
            existing = next((a for a in all_algos if a['name'].lower() == name.lower()), None)
            
            if existing:
                self.show_override_dialog(name, code, lang, all_algos)
            else:
                self.perform_final_save(name, code, lang, all_algos)

    def show_override_dialog(self, name, code, lang, all_algos):
        pop = ctk.CTkToplevel(self)
        pop.title("Confirm Override")
        self.center_popup(pop, 400, 200)
        
        ctk.CTkLabel(pop, text=f"'{name}' already exists.\nOverride all versions?", 
                     font=("Inter", 14, "bold")).pack(pady=20)
        
        btn_frame = ctk.CTkFrame(pop, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="Override", fg_color="#e74c3c",
                      command=lambda: self.perform_override(name, code, lang, all_algos, pop)).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancel", fg_color="gray30", 
                      command=pop.destroy).pack(side="left", padx=10)

    def perform_override(self, name, code, lang, all_algos, pop_window):
        updated_algos = [a for a in all_algos if a['name'].lower() != name.lower()]
        self.perform_final_save(name, code, lang, updated_algos)
        pop_window.destroy()

    def center_popup(self, win, w, h):
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (w // 2)
        y = (win.winfo_screenheight() // 2) - (h // 2) - 50
        win.geometry(f"{w}x{h}+{x}+{y}")
        win.grab_set()