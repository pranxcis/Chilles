# src/components/dialogs.py
import customtkinter as ctk
from src.theme.theme import Theme

class BaseDialog(ctk.CTkToplevel):
    """Enhanced reusable modal popup dialog with auto-centering, proper focus management, and container layout."""
    def __init__(self, master, title: str, width=460, height=420):
        super().__init__(master)
        
        self.title(title)
        self.dialog_width = width
        self.dialog_height = height
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        
        # Configure dark aesthetic
        self.configure(fg_color=Theme.BG_DARK)
        
        # Modal setup & protocol handling
        self.transient(master)
        self.protocol("WM_DELETE_WINDOW", self.close)
        
        # Center dialog relative to parent window
        self._center_window(master)

        # Layout configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main Outer Card Container
        self.container = ctk.CTkFrame(
            self, 
            fg_color=Theme.BG_CARD, 
            corner_radius=12,
            border_width=1,
            border_color=Theme.BORDER_COLOR
        )
        self.container.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(2, weight=1)  # Expand content area

        # 1. Dialog Header Title
        self.title_label = ctk.CTkLabel(
            self.container,
            text=title,
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(18, 10), sticky="w")

        # Subtle Header Separator Line
        self.header_divider = ctk.CTkFrame(self.container, height=1, fg_color=Theme.BORDER_COLOR)
        self.header_divider.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))

        # Grab modal focus AFTER building structure
        self.after(10, self._set_focus_and_grab)

    def _center_window(self, master):
        """Center the dialog on top of the master window or screen."""
        self.update_idletasks()
        try:
            parent_x = master.winfo_rootx()
            parent_y = master.winfo_rooty()
            parent_width = master.winfo_width()
            parent_height = master.winfo_height()

            x = parent_x + (parent_width // 2) - (self.dialog_width // 2)
            y = parent_y + (parent_height // 2) - (self.dialog_height // 2)
            self.geometry(f"{self.dialog_width}x{self.dialog_height}+{max(0, x)}+{max(0, y)}")
        except Exception:
            # Fallback to screen center if parent bounds are unavailable
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            x = (screen_width // 2) - (self.dialog_width // 2)
            y = (screen_height // 2) - (self.dialog_height // 2)
            self.geometry(f"{self.dialog_width}x{self.dialog_height}+{x}+{y}")

    def _set_focus_and_grab(self):
        """Safely activate modality and keyboard focus."""
        self.lift()
        self.focus_force()
        self.grab_set()

    def add_action_buttons(self, confirm_text: str, on_confirm, cancel_text: str = "Cancel", confirm_color: str = None) -> ctk.CTkFrame:
        """Helper method to append a standard two-button bottom row (Cancel & Confirm)."""
        btn_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        btn_frame.grid(row=10, column=0, sticky="ew", padx=20, pady=(10, 20))
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        btn_cancel = ctk.CTkButton(
            btn_frame,
            text=cancel_text,
            height=36,
            corner_radius=8,
            fg_color=Theme.BG_HOVER,
            hover_color="#323843",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.close
        )
        btn_cancel.grid(row=0, column=0, padx=(0, 6), sticky="ew")

        color = confirm_color or Theme.ACCENT_TEAL
        btn_confirm = ctk.CTkButton(
            btn_frame,
            text=confirm_text,
            height=36,
            corner_radius=8,
            fg_color=color,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=on_confirm
        )
        btn_confirm.grid(row=0, column=1, padx=(6, 0), sticky="ew")

        return btn_frame

    def close(self):
        """Release modality grab and safely destroy window."""
        self.grab_release()
        self.destroy()