import customtkinter as ctk
import pyperclip

# --- TOOLTIP HELPER ---
class HoverTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
        self.tip_window = tw = ctk.CTkToplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        ctk.CTkLabel(tw, text=self.text, fg_color="#2c3e50", text_color="white", 
                     corner_radius=6, padx=8, pady=4, font=("Inter", 11)).pack()

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

class SearchView(ctk.CTkFrame):
    def __init__(self, parent, db, settings, app_ptr):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.settings = settings
        self.app_ptr = app_ptr
        self.fav_filter = False

        # --- HEADER PANEL ---
        self.header = ctk.CTkFrame(self, fg_color="gray15", corner_radius=12)
        self.header.pack(fill="x", pady=(0, 15))

        self.name_ent = ctk.CTkEntry(self.header, placeholder_text="🔍 Search Name...", height=40)
        self.name_ent.grid(row=0, column=0, padx=(15, 5), pady=15, sticky="ew")
        self.name_ent.bind("<KeyRelease>", lambda e: self.perform_search())

        self.tag_ent = ctk.CTkEntry(self.header, placeholder_text="🏷️ Tags...", height=40)
        self.tag_ent.grid(row=0, column=1, padx=5, pady=15, sticky="ew")
        self.tag_ent.bind("<KeyRelease>", lambda e: self.perform_search())

        self.comp_ent = ctk.CTkEntry(self.header, placeholder_text="📊 Complexity...", height=40)
        self.comp_ent.grid(row=0, column=2, padx=5, pady=15, sticky="ew")
        self.comp_ent.bind("<KeyRelease>", lambda e: self.perform_search())

        ctrls = ctk.CTkFrame(self.header, fg_color="transparent")
        ctrls.grid(row=0, column=3, padx=(5, 15))

        self.fav_btn = ctk.CTkButton(ctrls, text="★", width=45, height=40, fg_color="gray25", command=self.toggle_fav_filter)
        self.fav_btn.pack(side="left", padx=5)
        HoverTip(self.fav_btn, "Show Favorites Only")

        self.mode_switch = ctk.CTkSwitch(ctrls, text="Contest", command=self.toggle_contest)
        if self.settings.contest_mode: self.mode_switch.select()
        self.mode_switch.pack(side="left", padx=10)

        self.add_btn = ctk.CTkButton(ctrls, text="+", width=45, height=40, fg_color="#2ecc71", font=("Inter", 22, "bold"), command=self.app_ptr.show_add_view)
        self.add_btn.pack(side="left", padx=5)
        HoverTip(self.add_btn, "Add New Algorithm")

        self.header.grid_columnconfigure((0, 1, 2), weight=1)

        self.results_area = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.results_area.pack(fill="both", expand=True)
        
        self.apply_contest_ui()
        self.perform_search()

    def toggle_contest(self):
        self.settings.toggle_contest_mode(self.mode_switch.get())
        self.apply_contest_ui()
        self.perform_search()

    def apply_contest_ui(self):
        """Wipes real text and resets the 'ghost' background text properly."""
        
        # --- 1. Reset everything to 'normal' first to avoid glitches ---
        self.name_ent.configure(state="normal")
        self.tag_ent.configure(state="normal")
        self.comp_ent.configure(state="normal")

        # --- 2. Wipe any real characters typed in the boxes ---
        self.name_ent.delete(0, 'end')
        self.tag_ent.delete(0, 'end')
        self.comp_ent.delete(0, 'end')

        if self.settings.contest_mode:
            # --- 3. Set the 'Ghost' Background text (NOT editable) ---
            self.tag_ent.configure(placeholder_text="🏷️ Tags (Disabled)")
            self.comp_ent.configure(placeholder_text="📊 Complexity (Disabled)")
            
            # --- 4. LOCK THEM[cite: 7] ---
            # Now we disable them so the user can't even click inside
            self.tag_ent.configure(state="disabled", fg_color="gray30")
            self.comp_ent.configure(state="disabled", fg_color="gray30")
        else:
            # Restore normal mode background text
            self.tag_ent.configure(placeholder_text="🏷️ Tags...", state="normal", fg_color="gray20")
            self.comp_ent.configure(placeholder_text="📊 Complexity...", state="normal", fg_color="gray20")

        # Always ensure the Name bar has its background text and focus
        self.name_ent.configure(placeholder_text="🔍 Search Name...")
        self.name_ent.focus()
    
    def toggle_fav_filter(self):
        self.fav_filter = not self.fav_filter
        self.fav_btn.configure(fg_color="#f39c12" if self.fav_filter else "gray25")
        self.perform_search()

    def perform_search(self):
        criteria = {"name": self.name_ent.get(), "tag": self.tag_ent.get(), "complexity": self.comp_ent.get(), "fav_only": self.fav_filter}
        results = self.db.search(criteria, self.settings.contest_mode, self.settings.restrictions)
        for widget in self.results_area.winfo_children(): widget.destroy()
        for algo in results: self.create_algo_card(algo)

    def create_algo_card(self, algo):
        card = ctk.CTkFrame(self.results_area, fg_color="gray20", corner_radius=10)
        card.pack(fill="x", pady=6, padx=5)

        # --- LEFT SIDE: Name + Meta grouped together ---
        left_panel = ctk.CTkFrame(card, fg_color="transparent")
        left_panel.pack(side="left", padx=20, pady=12)

        # Top line: Name + Complexity (behind it)
        title_row = ctk.CTkFrame(left_panel, fg_color="transparent")
        title_row.pack(anchor="w")

        ctk.CTkLabel(title_row, text=algo['name'], font=("Inter", 17, "bold")).pack(side="left")
        
        if not self.settings.contest_mode:
            ctk.CTkLabel(title_row, text=f"  ({algo.get('complexity', 'N/A')})", 
                         text_color="#3498db", font=("Inter", 12)).pack(side="left")

        # Bottom line: Tags (behind the start of the name)
        if not self.settings.contest_mode:
            tag_row = ctk.CTkFrame(left_panel, fg_color="transparent")
            tag_row.pack(anchor="w", pady=(4, 0))
            for tag in algo.get('tags', []):
                if tag.strip():
                    ctk.CTkLabel(tag_row, text=f" {tag} ", font=("Inter", 10), 
                                 fg_color="#34495e", corner_radius=6).pack(side="left", padx=(0, 5))

        # --- RIGHT SIDE: Only Buttons ---
        right_panel = ctk.CTkFrame(card, fg_color="transparent")
        right_panel.pack(side="right", padx=15)

        is_fav = algo.get('is_favorite', False)
        card_fav = ctk.CTkButton(right_panel, text="★", width=35, fg_color="transparent", 
                                 text_color="#f1c40f" if is_fav else "gray", font=("Inter", 20))
        card_fav.configure(command=lambda: self.toggle_fav_realtime(algo, card_fav))
        card_fav.pack(side="left", padx=5)

        ctk.CTkButton(right_panel, text="View", width=80, fg_color="#3498db", font=("Inter", 13, "bold"),
                      command=lambda a=algo: self.open_detail_view(a)).pack(side="left", padx=5)

    def open_detail_view(self, algo):
        detail_win = ctk.CTkToplevel(self)
        detail_win.title(f"Viewing: {algo['name']}")
        
        # --- Smaller Y-axis (600) and better centering ---
        w, h = 900, 600
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2) - 40
        detail_win.geometry(f"{w}x{h}+{x}+{y}")
        detail_win.after(10, detail_win.lift)

        header = ctk.CTkFrame(detail_win, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 5))
        ctk.CTkLabel(header, text=algo['name'], font=("Inter", 26, "bold")).pack(side="left")
        
        code_box = ctk.CTkTextbox(detail_win, font=("Consolas", 14), border_width=1)
        code_box.pack(fill="both", expand=True, padx=25, pady=10)
        code_box.insert("0.0", algo['code'])
        code_box.configure(state="disabled")

        # Copy icon ⎘
        copy_btn = ctk.CTkButton(detail_win, text="⎘", font=("Inter", 24), width=45, height=45, fg_color="gray30", command=lambda: pyperclip.copy(algo['code']))
        copy_btn.place(relx=0.96, rely=0.18, anchor="ne")

        footer = ctk.CTkFrame(detail_win, fg_color="transparent")
        footer.pack(fill="x", padx=25, pady=15)
        ctk.CTkLabel(footer, text=f"Complexity: {algo.get('complexity', 'N/A')}", text_color="#3498db", font=("Inter", 14, "bold")).pack(side="left")
        ctk.CTkButton(footer, text="Edit All Settings", fg_color="gray25", command=lambda: [detail_win.destroy(), self.app_ptr.show_edit_view(algo)]).pack(side="right")

    def toggle_fav_realtime(self, algo, btn):
        all_data = self.db.get_all()
        state = False
        for item in all_data:
            if item['name'] == algo['name']:
                item['is_favorite'] = not item.get('is_favorite', False)
                state = item['is_favorite']
                break
        self.db.save(all_data)
        btn.configure(text_color="#f1c40f" if state else "gray")
        self.perform_search()