import customtkinter as ctk
import pyperclip

class FavoriteView(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db

        ctk.CTkLabel(self, text="Favorite Algorithms", font=("Inter", 20, "bold")).pack(pady=10)

        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Your Collection")
        self.scroll_frame.pack(fill="both", expand=True, pady=10)

        self.load_favorites()

    def load_favorites(self):
        # Clear existing widgets
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        all_algos = self.db.get_all()
        favorites = [a for a in all_algos if a.get("is_favorite", False)]

        if not favorites:
            ctk.CTkLabel(self.scroll_frame, text="No favorites added yet.").pack(pady=20)
            return

        for algo in favorites:
            self.create_fav_card(algo)

    def create_fav_card(self, algo):
        card = ctk.CTkFrame(self.scroll_frame)
        card.pack(fill="x", pady=5, padx=5)
        
        ctk.CTkLabel(card, text=algo['name'], font=("Inter", 14, "bold")).pack(side="left", padx=10)
        
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(side="right")
        
        ctk.CTkButton(btn_frame, text="Copy", width=60, 
                      command=lambda: pyperclip.copy(algo['code'])).pack(side="left", padx=5)
        
        # Remove from favorites button
        ctk.CTkButton(btn_frame, text="Unfavorite", width=80, fg_color="#e74c3c", 
                      hover_color="#c0392b", command=lambda: self.remove_fav(algo)).pack(side="left", padx=5)

    def remove_fav(self, target_algo):
        all_algos = self.db.get_all()
        for algo in all_algos:
            if algo['name'] == target_algo['name']:
                algo['is_favorite'] = False
        self.db.save(all_algos)
        self.load_favorites() # Refresh the view