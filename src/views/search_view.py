import customtkinter as ctk
import pyperclip
import tkinter.filedialog as fd
import tkinter.messagebox as mb
import textwrap
from pygments import lex
from pygments.lexers import get_lexer_by_name
from utils import apply_syntax_highlighting

# --- TOOLTIP HELPER ---
class HoverTip:
    def __init__(self, widget, text, delay=300):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tip_window = None
        self.id = None
        
        # Bind enter, leave, and click events
        self.widget.bind("<Enter>", self.schedule_tip)
        self.widget.bind("<Leave>", self.hide_tip)
        self.widget.bind("<ButtonPress>", self.hide_tip) # Hide if the user clicks

    def schedule_tip(self, event=None):
        # Cancel any existing scheduled tip to prevent duplicates
        if self.id:
            self.widget.after_cancel(self.id)
        # Schedule the tooltip to show after the delay
        self.id = self.widget.after(self.delay, self.show_tip)

    def show_tip(self, event=None):
        if self.tip_window:
            return
            
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
        
        self.tip_window = tw = ctk.CTkToplevel(self.widget)
        tw.wm_overrideredirect(True) # Remove window borders
        
        # Keep tooltip on top of everything and prevent it from stealing focus
        if hasattr(tw, 'wm_attributes'):
            tw.wm_attributes("-topmost", True)
            
        tw.wm_geometry(f"+{x}+{y}")
        
        ctk.CTkLabel(tw, text=self.text, fg_color="#2c3e50", text_color="white", 
                     corner_radius=6, padx=8, pady=4, font=("Inter", 11)).pack()

    def hide_tip(self, event=None):
        # Cancel the timer if the mouse leaves before it pops up
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None
            
        # Destroy the window if it exists
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

        # --- 1. Control Zone (Pinned to Right) ---
        self.ctrls = ctk.CTkFrame(self.header, fg_color="transparent")
        self.ctrls.pack(side="right", padx=(5, 15), pady=15)

        self.add_btn = ctk.CTkButton(self.ctrls, text="+", width=45, height=40, fg_color="#34b86b", font=("Inter", 22, "bold"), command=self.app_ptr.show_add_view)
        self.add_btn.grid(row=0, column=0, padx=5)
        HoverTip(self.add_btn, "Add New Algorithm")

        self.fav_btn = ctk.CTkButton(self.ctrls, text="★", width=45, height=40, fg_color="gray25", command=self.toggle_fav_filter)
        self.fav_btn.grid(row=0, column=1, padx=5)
        HoverTip(self.fav_btn, "Show Favorites Only")
        
        # --- NEW: Export Button ---
        self.export_btn = ctk.CTkButton(self.ctrls, text="📄", width=45, height=40, fg_color="#a91717", font=("Inter", 20), command=self.show_export_popup)
        self.export_btn.grid(row=0, column=2, padx=5)
        HoverTip(self.export_btn, "Export as PDF")

        self.mode_switch = ctk.CTkSwitch(self.ctrls, text="Contest Mode", command=self.toggle_contest)
        if self.settings.contest_mode: self.mode_switch.select()
        self.mode_switch.grid(row=0, column=3, padx=10) # Moved to column 3

        # --- 2. Search Zone (Left/Center) ---
        self.search_container = ctk.CTkFrame(self.header, fg_color="transparent")
        self.search_container.pack(side="left", fill="x", expand=True, padx=(15, 5))

        self.name_ent = ctk.CTkEntry(self.search_container, placeholder_text="🔍 Search Name...", height=40)
        self.name_ent.grid(row=0, column=0, padx=5, pady=15, sticky="ew")
        self.name_ent.bind("<KeyRelease>", lambda e: self.perform_search())

        # Category ComboBox
        all_algos = self.db.get_all()
        categories = sorted(list(set(a.get('category', 'General') for a in all_algos)))
        self.cat_combo = ctk.CTkComboBox(self.search_container, values=["All Categories"] + categories, 
                                        height=40, command=lambda _: self.perform_search(), state="readonly")
        self.cat_combo.grid(row=0, column=1, padx=5, pady=15, sticky="ew")
        self.cat_combo.set("All Categories")

        self.tag_ent = ctk.CTkEntry(self.search_container, placeholder_text="🏷️ Tags...", height=40)
        self.tag_ent.grid(row=0, column=2, padx=5, pady=15, sticky="ew")
        self.tag_ent.bind("<KeyRelease>", lambda e: self.perform_search())

        self.comp_ent = ctk.CTkEntry(self.search_container, placeholder_text="📊 Complexity...", height=40)
        self.comp_ent.grid(row=0, column=3, padx=5, pady=15, sticky="ew")
        self.comp_ent.bind("<KeyRelease>", lambda e: self.perform_search())

        # Weight distribution for 4 columns
        self.search_container.grid_columnconfigure(0, weight=2) 
        self.search_container.grid_columnconfigure((1, 2, 3), weight=1)

        self.results_area = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.results_area.pack(fill="both", expand=True)
        
        self.apply_contest_ui()
        self.perform_search()

        # FIX: Force focus to the parent frame (main_view) 
        # so entries don't auto-focus on startup.
        self.after(200, lambda: self.master.focus_set())

    def toggle_contest(self):
        self.settings.toggle_contest_mode(self.mode_switch.get())
        self.apply_contest_ui()
        self.perform_search()

    def apply_contest_ui(self):
        """Removes Add/Edit capabilities and extra search bars in Contest Mode."""
        self.tag_ent.grid()
        self.comp_ent.grid()
        self.add_btn.grid()
        self.export_btn.grid()
        self.cat_combo.grid()

        # Clear active text
        self.name_ent.delete(0, 'end')
        self.tag_ent.delete(0, 'end')
        self.comp_ent.delete(0, 'end')
        self.cat_combo.set("All Categories")

        self.name_ent.configure(placeholder_text="🔍 Search Name...")
        self.tag_ent.configure(placeholder_text="🏷️ Tags...", height=40)
        self.comp_ent.configure(placeholder_text="📊 Complexity...", height=40)
        
        if self.settings.contest_mode:
            self.tag_ent.grid_remove()
            self.comp_ent.grid_remove()
            self.add_btn.grid_remove()
            self.export_btn.grid_remove()
            # cat_combo remains visible in contest mode
            
        # FIX: Ensure focus goes back to the background when toggling
        if hasattr(self, "master"):
            self.master.focus_set()
    
    def toggle_fav_filter(self):
        self.fav_filter = not self.fav_filter
        self.fav_btn.configure(fg_color="#f39c12" if self.fav_filter else "gray25")
        self.perform_search()

    def perform_search(self):
        selected_cat = self.cat_combo.get()
        criteria = {
            "name": self.name_ent.get(), 
            "category": "" if selected_cat == "All Categories" else selected_cat,
            "tag": self.tag_ent.get(), 
            "complexity": self.comp_ent.get(), 
            "fav_only": self.fav_filter
        }
        results = self.db.search(criteria, self.settings.contest_mode, self.settings.restrictions)
        
        # Clear the results area
        for widget in self.results_area.winfo_children(): 
            widget.destroy()
            
        # Group algorithms by category
        grouped_algos = {}
        for algo in results:
            cat = algo.get('category', 'General')
            if cat not in grouped_algos:
                grouped_algos[cat] = []
            grouped_algos[cat].append(algo)
            
        # Render headers and cards
        for cat in sorted(grouped_algos.keys()):
            # Create the Category Header Label
            ctk.CTkLabel(
                self.results_area, 
                text=cat, 
                font=("Inter", 18, "bold"), 
                text_color="#e0e0e0", 
                anchor="w"
            ).pack(fill="x", padx=10, pady=(20, 5))
            
            # Render the cards for this specific category
            for algo in grouped_algos[cat]: 
                self.create_algo_card(algo)

    def create_algo_card(self, algo):
        card = ctk.CTkFrame(self.results_area, fg_color="gray20", corner_radius=10)
        card.pack(fill="x", pady=6, padx=5)

        # --- LEFT SIDE: Name + Meta grouped together ---
        left_panel = ctk.CTkFrame(card, fg_color="transparent")
        left_panel.pack(side="left", padx=20, pady=12)

        title_row = ctk.CTkFrame(left_panel, fg_color="transparent")
        title_row.pack(anchor="w")

        ctk.CTkLabel(title_row, text=algo['name'], font=("Inter", 17, "bold")).pack(side="left")
        
        # (The inline category display was removed from here)
        
        # Complexity & Tags
        if not self.settings.contest_mode:
            ctk.CTkLabel(title_row, text=f"  {algo.get('complexity', 'N/A')}", 
                         text_color="#3498db", font=("Inter", 12)).pack(side="left")
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
        
        w, h = 900, 650
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2) - 40
        detail_win.geometry(f"{w}x{h}+{x}+{y}")
        detail_win.after(10, detail_win.lift)

        # Header section
        header = ctk.CTkFrame(detail_win, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 5))
        ctk.CTkLabel(header, text=algo['name'], font=("Inter", 26, "bold")).pack(side="left")
        
        # Code Textbox
        code_box = ctk.CTkTextbox(detail_win, font=("Consolas", 14), border_width=1)
        code_box.pack(fill="both", expand=True, padx=25, pady=10)

        # --- Language Selection UI ---
        versions = algo.get('versions', [])
        lang_names = [v['lang'] for v in versions]
        
        def switch_lang(choice):
            selected_version = next((v for v in versions if v['lang'] == choice), None)
            if selected_version:
                code_box.configure(state="normal")
                code_box.delete("0.0", "end")
                code_box.insert("0.0", selected_version['code'])
                apply_syntax_highlighting(code_box, choice)
                code_box.configure(state="disabled")

        # Combo Box for Language Selection
        lang_selector = ctk.CTkComboBox(header, values=lang_names, command=switch_lang, width=150, state="readonly")
        lang_selector.pack(side="right", padx=10)
        lang_selector.set(lang_names[0] if lang_names else "No Languages")
        
        # Initialize with first language
        switch_lang(lang_selector.get())

        # Copy button
        copy_btn = ctk.CTkButton(detail_win, text="⎘", font=("Inter", 24), width=45, height=45, 
                                fg_color="gray30", command=lambda: pyperclip.copy(code_box.get("0.0", "end").strip()))
        copy_btn.place(relx=0.96, rely=0.13, anchor="ne")
        HoverTip(copy_btn, "Copy Code")

        # Footer
        footer = ctk.CTkFrame(detail_win, fg_color="transparent")
        footer.pack(fill="x", padx=25, pady=15)
        ctk.CTkLabel(footer, text=f"Complexity: {algo.get('complexity', 'N/A')}", 
                    text_color="#3498db", font=("Inter", 14, "bold")).pack(side="left")
        
        # The Edit Button Logic
        if not self.settings.contest_mode:
            ctk.CTkButton(footer, text="Edit All Settings", fg_color="gray25", 
                        command=lambda: [detail_win.destroy(), self.app_ptr.show_edit_view(algo)]).pack(side="right")

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
    def show_export_popup(self):
        pop = ctk.CTkToplevel(self)
        pop.title("Export PDF")
        
        # Center the popup
        w, h = 320, 180
        pop.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() // 2) - (w // 2)
        y = self.winfo_rooty() + (self.winfo_height() // 2) - (h // 2)
        pop.geometry(f"{w}x{h}+{x}+{y}")
        pop.grab_set()

        ctk.CTkLabel(pop, text="What would you like to export?", font=("Inter", 16, "bold")).pack(pady=30)

        btn_frame = ctk.CTkFrame(pop, fg_color="transparent")
        btn_frame.pack()

        ctk.CTkButton(btn_frame, text="All Algorithms", fg_color="#3498db", width=120,
                      command=lambda: self.export_pdf(False, pop)).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Favorites Only", fg_color="#f39c12", width=120,
                      command=lambda: self.export_pdf(True, pop)).pack(side="left", padx=10)

    def export_pdf(self, fav_only, pop_window):
        pop_window.destroy()
        
        # Ask user where to save the file
        filepath = fd.asksaveasfilename(
            defaultextension=".pdf", 
            filetypes=[("PDF Documents", "*.pdf")],
            title="Save PDF As"
        )
        if not filepath: 
            return

        all_algos = self.db.get_all()
        if fav_only:
            all_algos = [a for a in all_algos if a.get('is_favorite')]

        if not all_algos:
            mb.showwarning("No Data", "There are no algorithms to export.")
            return

        try:
            from fpdf import FPDF
            
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # --- 1. SAFE TEXT HELPER ---
            def safe_write(text, width_limit, cell_height):
                clean = str(text).replace('\t', '    ').encode('latin-1', 'replace').decode('latin-1')
                lines = textwrap.wrap(clean, width=width_limit, break_long_words=True)
                if not lines:
                    pdf.ln(cell_height)
                else:
                    for line in lines:
                        pdf.set_x(15)
                        pdf.multi_cell(w=180, h=cell_height, text=line)

            # --- 2. SYNTAX HIGHLIGHTER HELPER ---
            def write_highlighted_code(code, lang):
                try:
                    # Map c# to csharp for pygments
                    safe_lang = lang.lower().replace('c#', 'csharp')
                    lexer = get_lexer_by_name(safe_lang)
                except:
                    lexer = get_lexer_by_name("text")

                pdf.set_font("Courier", '', 10)
                
                # Process line by line to keep FPDF strictly inside margins
                for line in code.split('\n'):
                    line = line.replace('\t', '    ')
                    wrapped_lines = textwrap.wrap(line, width=85, break_long_words=True)
                    
                    if not wrapped_lines:
                        pdf.ln(5)
                        continue
                        
                    for w_line in wrapped_lines:
                        pdf.set_x(15) # Force cursor to left margin
                        
                        # Tokenize the string chunk
                        for token, text in lex(w_line, lexer):
                            token_str = str(token)
                            
                            # Map Pygments tokens to PDF RGB Colors (Light Theme)
                            if 'Comment' in token_str:
                                pdf.set_text_color(34, 139, 34)  # Forest Green
                            elif 'Keyword' in token_str:
                                pdf.set_text_color(0, 0, 255)    # Blue
                            elif 'String' in token_str:
                                pdf.set_text_color(163, 21, 21)  # Dark Red
                            elif 'Number' in token_str:
                                pdf.set_text_color(205, 92, 92)  # Indian Red / Orange
                            elif 'Name.Function' in token_str or 'Name.Class' in token_str:
                                pdf.set_text_color(43, 145, 175) # Teal
                            else:
                                pdf.set_text_color(0, 0, 0)      # Black
                                
                            clean_text = text.encode('latin-1', 'replace').decode('latin-1')
                            pdf.write(5, clean_text)
                            
                        pdf.ln(5) # Move to next line

            # --- 3. ORGANIZE DATA INTO SECTIONS (CATEGORIES) ---
            grouped_algos = {}
            for algo in all_algos:
                cat = algo.get('category', 'General')
                if cat not in grouped_algos:
                    grouped_algos[cat] = []
                grouped_algos[cat].append(algo)

            # --- 4. RENDER PDF ---
            for cat in sorted(grouped_algos.keys()):
                pdf.add_page()
                
                # --- SECTION HEADER ---
                pdf.set_font("Helvetica", 'B', 24)
                pdf.set_text_color(41, 128, 185) # Nice Blue Header
                pdf.cell(0, 15, cat, ln=True, align='L')
                
                # Draw a divider line
                pdf.set_draw_color(41, 128, 185)
                pdf.set_line_width(0.5)
                pdf.line(15, pdf.get_y(), 195, pdf.get_y())
                pdf.ln(10)
                
                # --- PRINT ALGORITHMS IN THIS SECTION ---
                for algo in grouped_algos[cat]:
                    # Title
                    pdf.set_font("Helvetica", 'B', 16)
                    pdf.set_text_color(0, 0, 0)
                    safe_write(f"{algo.get('name', 'Unnamed')}", 60, 8)
                    pdf.ln(2)
                    
                    # Metadata
                    pdf.set_font("Helvetica", 'I', 11)
                    pdf.set_text_color(100, 100, 100)
                    safe_write(f"Complexity: {algo.get('complexity', 'N/A')}", 80, 6)
                    
                    tags = ", ".join(algo.get('tags', [])) if algo.get('tags') else "None"
                    safe_write(f"Tags: {tags}", 80, 6)
                    pdf.ln(4)

                    # Code Versions
                    for version in algo.get('versions', []):
                        pdf.set_font("Helvetica", 'B', 12)
                        pdf.set_text_color(0, 0, 0)
                        safe_write(f"Language: {version.get('lang', 'Unknown')}", 80, 8)
                        
                        # Call the new syntax highlighting writer
                        write_highlighted_code(version.get('code', ''), version.get('lang', ''))
                            
                        pdf.ln(6) # Space between languages
                    
                    pdf.ln(10) # Big space between algorithms
                    
            pdf.output(filepath)
            mb.showinfo("Success", f"PDF successfully saved to:\n{filepath}")
            
        except Exception as e:
            mb.showerror("Error", f"An error occurred while creating the PDF:\n{str(e)}")