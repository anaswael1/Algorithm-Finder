import customtkinter as ctk
from views.search_view import SearchView
from views.add_view import AddView
from database import Database
from settings_manager import SettingsManager
from views.favorite_view import FavoriteView

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
from views.add_view import EditView # Update your imports

class HoverTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tip_window = tw = ctk.CTkToplevel(self.widget)
        tw.wm_overrideredirect(True) # Remove window borders
        tw.wm_geometry(f"+{x}+{y}")
        
        label = ctk.CTkLabel(tw, text=self.text, fg_color="#2c3e50", 
                             corner_radius=6, padx=5, pady=2)
        label.pack()

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

class AlgorithmFinderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Algorithm Finder Pro")
        self.geometry("1100x700")
        self.db = Database()
        self.settings = SettingsManager()

        # Single Main Frame (No Sidebar)
        self.main_view = ctk.CTkFrame(self, fg_color="transparent")
        self.main_view.pack(fill="both", expand=True, padx=20, pady=20)

        self.show_search_view()
        self.center_window()

    def show_search_view(self):
        self.clear_main_view()
        self.current_view = SearchView(self.main_view, self.db, self.settings, self)
        self.current_view.pack(fill="both", expand=True)

    def show_add_view(self):
        self.clear_main_view()
        self.current_view = AddView(self.main_view, self.db, self) # Added app_ptr
        self.current_view.pack(fill="both", expand=True)

    def show_edit_view(self, algo):
        self.clear_main_view()
        self.current_view = EditView(self.main_view, self.db, algo, self)
        self.current_view.pack(fill="both", expand=True)

    def clear_main_view(self):
        for widget in self.main_view.winfo_children():
            widget.destroy()
    def center_window(self, width=1100, height=700):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        # Calculate position (the -50 moves it slightly toward the top)
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2) - 50
        self.geometry(f"{width}x{height}+{x}+{y}")