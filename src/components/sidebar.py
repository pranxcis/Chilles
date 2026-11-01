
import customtkinter as ctk
from src.theme.theme import Theme


class Sidebar(ctk.CTkFrame):
    """Modern sidebar navigation for CHILLES KTV Management System."""

    def __init__(self, master, on_navigate, **kwargs):
        super().__init__(
            master,
            width=245,
            fg_color=Theme.BG_CARD,
            corner_radius=0,
            **kwargs
        )

        self.on_navigate = on_navigate
        self.active_item = "Dashboard"
        self.buttons = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(20, weight=1)

        self._build_brand()
        self._build_navigation()
        self._build_footer()

        self._set_active("Dashboard", notify=False)

    # --------------------------------------------------
    # BRAND HEADER
    # --------------------------------------------------

    def _build_brand(self):
        brand = ctk.CTkFrame(self, fg_color="transparent")
        brand.grid(
            row=0, column=0,
            sticky="ew",
            padx=22, pady=(28, 30)
        )
        brand.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            brand,
            text="CHILLES",
            font=ctk.CTkFont(size=25, weight="bold"),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w"
        ).pack(anchor="w")

        ctk.CTkLabel(
            brand,
            text="KTV MANAGEMENT SYSTEM",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=Theme.TEXT_MUTED,
            anchor="w"
        ).pack(anchor="w", pady=(3, 0))

    # --------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------

    def _build_navigation(self):
        sections = [
            ("OVERVIEW", [
                ("Dashboard", "⌂"),
            ]),
            ("OPERATIONS", [
                ("Orders", "▤"),
                ("Sessions", "◷"),
                ("Transactions", "₱"),
            ]),
            ("MANAGEMENT", [
                ("Customers", "♙"),
                ("Rooms", "▣"),
                ("Products", "◇"),
                ("Packages", "▦"),
            ]),
            ("SYSTEM", [
                ("Reports", "▥"),
                ("Settings", "⚙"),
            ]),
        ]

        row = 1

        for section_name, items in sections:

            ctk.CTkLabel(
                self,
                text=section_name,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=Theme.TEXT_MUTED,
                anchor="w"
            ).grid(
                row=row,
                column=0,
                sticky="ew",
                padx=24,
                pady=(10, 8)
            )

            row += 1

            for name, symbol in items:
                self._create_nav_button(
                    name=name,
                    symbol=symbol,
                    row=row
                )
                row += 1

    def _create_nav_button(self, name, symbol, row):
        button = ctk.CTkButton(
            self,
            text=f"  {symbol}     {name}",
            height=42,
            corner_radius=9,
            anchor="w",
            fg_color="transparent",
            hover_color=Theme.BG_HOVER,
            text_color=Theme.TEXT_MUTED,
            font=ctk.CTkFont(size=13),
            border_spacing=12,
            command=lambda: self._set_active(name)
        )

        button.grid(
            row=row,
            column=0,
            sticky="ew",
            padx=12,
            pady=2
        )

        self.buttons[name] = button

    # --------------------------------------------------
    # FOOTER
    # --------------------------------------------------

    def _build_footer(self):
        footer = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        footer.grid(
            row=21,
            column=0,
            sticky="sew",
            padx=15,
            pady=18
        )

        separator = ctk.CTkFrame(
            footer,
            height=1,
            fg_color=Theme.BORDER_COLOR
        )
        separator.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            footer,
            text="CHILLES KTV",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w"
        ).pack(fill="x", padx=5)

        ctk.CTkLabel(
            footer,
            text="Management Dashboard  •  v1.0",
            font=ctk.CTkFont(size=10),
            text_color=Theme.TEXT_MUTED,
            anchor="w"
        ).pack(fill="x", padx=5, pady=(4, 0))

    # --------------------------------------------------
    # ACTIVE NAVIGATION
    # --------------------------------------------------

    def _set_active(self, name, notify=True):
        if name not in self.buttons:
            return

        self.active_item = name

        for btn_name, button in self.buttons.items():
            if btn_name == name:
                button.configure(
                    fg_color=Theme.ACCENT_TEAL,
                    text_color="#FFFFFF",
                    hover_color=Theme.ACCENT_TEAL
                )
            else:
                button.configure(
                    fg_color="transparent",
                    text_color=Theme.TEXT_MUTED,
                    hover_color=Theme.BG_HOVER
                )

        if notify:
            self.on_navigate(name)

    def set_active(self, name):
        """Allow the main application to change the active navigation."""
        self._set_active(name)
