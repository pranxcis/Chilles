# src/components/status_badges.py module
# src/components/status_badges.py
import customtkinter as ctk
from src.theme.theme import Theme

class StatusBadge(ctk.CTkFrame):
    """Status pill badge for rooms, orders, or transactions."""
    def __init__(self, master, status: str = "Available", **kwargs):
        # Determine color based on status
        status_lower = status.lower()
        if "occup" in status_lower:
            bg = Theme.STATUS_OCCUPIED
        elif "maint" in status_lower:
            bg = Theme.STATUS_MAINTENANCE
        else:
            bg = Theme.STATUS_AVAILABLE

        super().__init__(master, fg_color=bg, corner_radius=6, **kwargs)
        
        self.label = ctk.CTkLabel(
            self,
            text=status.upper(),
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#FFFFFF"
        )
        self.label.pack(padx=10, pady=3)

    def update_status(self, status: str):
        status_lower = status.lower()
        if "occup" in status_lower:
            bg = Theme.STATUS_OCCUPIED
        elif "maint" in status_lower:
            bg = Theme.STATUS_MAINTENANCE
        else:
            bg = Theme.STATUS_AVAILABLE
            
        self.configure(fg_color=bg)
        self.label.configure(text=status.upper())