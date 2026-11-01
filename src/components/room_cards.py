# src/components/room_cards.py module
# src/components/room_cards.py
import customtkinter as ctk
from src.theme.theme import Theme
from src.components.status_badges import StatusBadge

class RoomCard(ctk.CTkFrame):
    """Interactive room card showing status, capacity, and quick action buttons."""
    def __init__(self, master, room_name: str, room_type: str, status: str, capacity: int, on_click=None, **kwargs):
        super().__init__(master, fg_color=Theme.BG_CARD, corner_radius=10, **kwargs)
        self.on_click = on_click
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header (Name & Status Badge)
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        top_frame.grid_columnconfigure(0, weight=1)

        self.name_label = ctk.CTkLabel(
            top_frame,
            text=room_name,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        self.name_label.grid(row=0, column=0, sticky="w")

        self.badge = StatusBadge(top_frame, status=status)
        self.badge.grid(row=0, column=1, sticky="e")

        # Details
        details_text = f"Type: {room_type}  |  Capacity: {capacity} Persons"
        self.details_label = ctk.CTkLabel(
            self,
            text=details_text,
            font=ctk.CTkFont(size=12),
            text_color=Theme.TEXT_MUTED
        )
        self.details_label.grid(row=1, column=0, padx=15, pady=5, sticky="w")

        # Action Button
        self.action_btn = ctk.CTkButton(
            self,
            text="Manage Room",
            fg_color=Theme.ACCENT_TEAL,
            hover_color="#21867A",
            height=32,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self.on_click(room_name) if self.on_click else None
        )
        self.action_btn.grid(row=2, column=0, padx=15, pady=(10, 15), sticky="ew")