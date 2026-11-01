# src/components/header.py
import customtkinter as ctk
from datetime import datetime
from src.theme.theme import Theme
from src.core.state_manager import StateManager

class Header(ctk.CTkFrame):
    """Upgraded top header bar displaying active section title, branch context, live clock, and user badge."""
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=Theme.BG_DARK, height=65, corner_radius=0, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        # Left Section: Section Title & Branch Subtitle
        left_frame = ctk.CTkFrame(self, fg_color="transparent")
        left_frame.grid(row=0, column=0, padx=35, pady=(25, 0), sticky="w")
        left_frame.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            left_frame, 
            text="Dashboard", 
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        self.subtitle_label = ctk.CTkLabel(
            left_frame, 
            text="Chilles KTV • Main Branch Console", 
            font=ctk.CTkFont(size=11),
            text_color=Theme.TEXT_MUTED
        )
        self.subtitle_label.grid(row=1, column=0, sticky="w", pady=(0, 2))

        # Right Section: Live Clock & User Badge
        right_frame = ctk.CTkFrame(self, fg_color="transparent")
        right_frame.grid(row=0, column=1, padx=25, pady=(12, 0), sticky="e")

        # Live Clock Label
        self.clock_label = ctk.CTkLabel(
            right_frame,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        self.clock_label.pack(side="left", padx=(0, 15))

        # User Profile Badge Pill
        user_pill = ctk.CTkFrame(
            right_frame, 
            fg_color=Theme.BG_CARD, 
            corner_radius=8, 
            border_width=1, 
            border_color=Theme.BORDER_COLOR
        )
        user_pill.pack(side="left")

        user_icon = ctk.CTkLabel(user_pill, text="👤", font=ctk.CTkFont(size=12))
        user_icon.pack(side="left", padx=(10, 4), pady=6)

        current_user = StateManager.get("current_user", "Administrator")
        self.user_label = ctk.CTkLabel(
            user_pill,
            text=current_user,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=Theme.ACCENT_TEAL
        )
        self.user_label.pack(side="left", padx=(0, 12), pady=6)

        # Subtle bottom border line
        self.divider = ctk.CTkFrame(self, height=1, fg_color=Theme.BORDER_COLOR)
        self.divider.grid(row=1, column=0, columnspan=2, sticky="ew")

        # Initialize live clock ticker
        self._update_clock()

    def update_title(self, title: str):
        """Update active view title when navigating through the sidebar."""
        self.title_label.configure(text=title)

    def _update_clock(self):
        """Refresh live date and timestamp every second."""
        now_str = datetime.now().strftime("%b %d, %Y  •  %I:%M:%S %p")
        self.clock_label.configure(text=now_str)
        self.after(1000, self._update_clock)