# src/components/cards.py
import customtkinter as ctk
from src.theme.theme import Theme

class MetricCard(ctk.CTkFrame):
    """Reusable card component for displaying key metrics and statistics."""
    def __init__(self, master, title: str, value: str, **kwargs):
        super().__init__(master, fg_color=Theme.BG_CARD, corner_radius=10, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        
        self.title_label = ctk.CTkLabel(
            self,
            text=title.upper(),
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=Theme.TEXT_MUTED
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")

        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        self.value_label.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="w")

    def update_value(self, new_value: str):
        self.value_label.configure(text=new_value)