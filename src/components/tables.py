# src/components/tables.py module
# src/components/tables.py
import customtkinter as ctk
from src.theme.theme import Theme

class DataTable(ctk.CTkFrame):
    """Reusable scrollable table container for records, orders, and logs."""
    def __init__(self, master, columns: list, **kwargs):
        super().__init__(master, fg_color=Theme.BG_CARD, corner_radius=10, **kwargs)
        self.columns = columns
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header Row
        self.header_frame = ctk.CTkFrame(self, fg_color=Theme.BG_HOVER, corner_radius=6, height=40)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        for idx, col in enumerate(columns):
            self.header_frame.grid_columnconfigure(idx, weight=1)
            lbl = ctk.CTkLabel(
                self.header_frame,
                text=col.upper(),
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=Theme.TEXT_PRIMARY
            )
            lbl.grid(row=0, column=idx, padx=10, pady=10, sticky="w")

        # Scrollable Body Rows Area
        self.body_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.body_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.body_frame.grid_columnconfigure(0, weight=1)

    def clear_rows(self):
        for widget in self.body_frame.winfo_children():
            widget.destroy()

    def add_row(self, values: list, row_idx: int):
        row_container = ctk.CTkFrame(self.body_frame, fg_color="transparent", height=35)
        row_container.grid(row=row_idx, column=0, sticky="ew", pady=2)
        
        for idx, val in enumerate(values):
            row_container.grid_columnconfigure(idx, weight=1)
            lbl = ctk.CTkLabel(
                row_container,
                text=str(val),
                font=ctk.CTkFont(size=12),
                text_color=Theme.TEXT_MUTED
            )
            lbl.grid(row=0, column=idx, padx=10, sticky="w")