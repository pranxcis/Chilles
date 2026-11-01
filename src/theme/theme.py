import customtkinter as ctk

class Theme:
    """Modern dark graphite/charcoal with muted sage/teal accents."""
    
    # Palette
    BG_DARK = "#121417"          # Primary dark background
    BG_CARD = "#1A1D23"          # Card / Sidebar background
    BG_HOVER = "#242830"         # Hover state background
    TEXT_PRIMARY = "#F0F2F5"     # Main white/light text
    TEXT_MUTED = "#9BA1A6"       # Secondary muted text
    ACCENT_TEAL = "#2A9D8F"      # Muted teal accent
    ACCENT_SAGE = "#52796F"      # Muted sage accent
    ACCENT_HOVER = "#21867A"     # Hover teal
    BORDER_COLOR = "#2D333B"     # Borders and dividers
    
    # Status Colors
    STATUS_AVAILABLE = "#2A9D8F" # Teal
    STATUS_OCCUPIED = "#E76F51"  # Warm Coral / Red
    STATUS_MAINTENANCE = "#E9C46A"# Amber
    
    @classmethod
    def apply_theme(cls):
        ctk.set_appearance_mode("Dark" )
        ctk.set_default_color_theme("dark-blue")