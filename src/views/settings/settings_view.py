# src/views/settings/settings_view.py
import os
import customtkinter as ctk

from src.theme.theme import Theme
from src.components.dialogs import BaseDialog
from src.repositories.json_repository import JSONRepository
from src.services.backup_service import BackupService
from src.services.activity_log_service import ActivityLogService

class SettingsView(ctk.CTkFrame):
    """Settings module for managing business profile settings, activity logs, and system backups."""
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=Theme.BG_DARK, corner_radius=0, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_container = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=25, pady=20)
        self.main_container.grid_columnconfigure(0, weight=1)

        self._render_business_profile_card()
        self._render_backup_restore_card()
        self._render_activity_logs_card()

    def _render_business_profile_card(self):
        """Render editable Business Profile settings form."""
        card = ctk.CTkFrame(self.main_container, fg_color=Theme.BG_CARD, corner_radius=12, border_width=1, border_color=Theme.BORDER_COLOR)
        card.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        card.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(card, text="Business Profile & Receipts", font=ctk.CTkFont(size=16, weight="bold"), text_color=Theme.TEXT_PRIMARY).grid(row=0, column=0, columnspan=2, padx=20, pady=(16, 10), sticky="w")

        # Load existing business profile
        biz_data = JSONRepository.load_data("business.json") or {}

        ctk.CTkLabel(card, text="Establishment Name", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=1, column=0, padx=20, pady=(5, 2), sticky="w")
        self.entry_name = ctk.CTkEntry(card, height=38)
        self.entry_name.grid(row=2, column=0, padx=(20, 10), pady=(0, 12), sticky="ew")
        self.entry_name.insert(0, biz_data.get("name", "Chilles KTV"))

        ctk.CTkLabel(card, text="Contact Phone", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=1, column=1, padx=(10, 20), pady=(5, 2), sticky="w")
        self.entry_phone = ctk.CTkEntry(card, height=38)
        self.entry_phone.grid(row=2, column=1, padx=(10, 20), pady=(0, 12), sticky="ew")
        self.entry_phone.insert(0, biz_data.get("phone", "0956-123-4567"))

        ctk.CTkLabel(card, text="Physical Address", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=3, column=0, columnspan=2, padx=20, pady=(5, 2), sticky="w")
        self.entry_address = ctk.CTkEntry(card, height=38)
        self.entry_address.grid(row=4, column=0, columnspan=2, padx=20, pady=(0, 12), sticky="ew")
        self.entry_address.insert(0, biz_data.get("address", "123 Music Avenue, Taguig City, Metro Manila"))

        ctk.CTkLabel(card, text="Receipt Footer Message", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=5, column=0, columnspan=2, padx=20, pady=(5, 2), sticky="w")
        self.entry_footer = ctk.CTkEntry(card, height=38)
        self.entry_footer.grid(row=6, column=0, columnspan=2, padx=20, pady=(0, 16), sticky="ew")
        self.entry_footer.insert(0, biz_data.get("receipt_footer", "Thank you for singing with us! Please come again."))

        btn_save = ctk.CTkButton(card, text="Save Profile Settings", height=38, fg_color=Theme.ACCENT_TEAL, font=ctk.CTkFont(size=12, weight="bold"), command=self.save_business_profile)
        btn_save.grid(row=7, column=1, padx=20, pady=(0, 16), sticky="e")

    def save_business_profile(self):
        biz_data = {
            "name": self.entry_name.get().strip(),
            "phone": self.entry_phone.get().strip(),
            "address": self.entry_address.get().strip(),
            "receipt_footer": self.entry_footer.get().strip()
        }
        JSONRepository.save_data("business.json", biz_data)
        
        dialog = BaseDialog(self, title="Settings Saved", width=380, height=180)
        ctk.CTkLabel(dialog.container, text="Business profile updated successfully.", text_color=Theme.TEXT_PRIMARY, font=ctk.CTkFont(size=13)).grid(row=2, column=0, padx=20, pady=20)
        dialog.add_action_buttons(confirm_text="OK", on_confirm=dialog.close, cancel_text=None)

    def _render_backup_restore_card(self):
        """Render JSON data backup and restore operations card."""
        card = ctk.CTkFrame(self.main_container, fg_color=Theme.BG_CARD, corner_radius=12, border_width=1, border_color=Theme.BORDER_COLOR)
        card.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        card.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(card, text="Database Backup & Restore", font=ctk.CTkFont(size=16, weight="bold"), text_color=Theme.TEXT_PRIMARY).grid(row=0, column=0, columnspan=2, padx=20, pady=(16, 10), sticky="w")

        ctk.CTkLabel(
            card, 
            text="Safely backup all system JSON records or restore from a previously created snapshot archive.", 
            font=ctk.CTkFont(size=12), 
            text_color=Theme.TEXT_MUTED
        ).grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 16), sticky="w")

        btn_backup = ctk.CTkButton(card, text="💾 Create Backup Archive", height=38, fg_color=Theme.ACCENT_TEAL, font=ctk.CTkFont(size=12, weight="bold"), command=self.create_backup)
        btn_backup.grid(row=2, column=0, padx=(20, 10), pady=(0, 16), sticky="ew")

        btn_restore = ctk.CTkButton(card, text="📂 Restore from Backup", height=38, fg_color=Theme.BG_HOVER, hover_color="#C0392B", font=ctk.CTkFont(size=12, weight="bold"), command=self.restore_backup)
        btn_restore.grid(row=2, column=1, padx=(10, 20), pady=(0, 16), sticky="ew")

    def create_backup(self):
        backup_path = BackupService.create_backup()
        if backup_path:
            dialog = BaseDialog(self, title="Backup Created", width=420, height=200)
            ctk.CTkLabel(dialog.container, text=f"Backup archive created successfully:\n{backup_path}", text_color=Theme.TEXT_PRIMARY, font=ctk.CTkFont(size=12), justify="center").grid(row=2, column=0, padx=20, pady=20)
            dialog.add_action_buttons(confirm_text="OK", on_confirm=dialog.close, cancel_text=None)

    def restore_backup(self):
        """Prompt to select and restore a zip backup archive."""
        file_path = ctk.filedialog.askopenfilename(
            title="Select Backup File",
            filetypes=[("Zip Files", "*.zip")]
        )
        if file_path:
            success = BackupService.restore_backup(file_path)
            if success:
                dialog = BaseDialog(self, title="Restore Successful", width=400, height=200)
                ctk.CTkLabel(dialog.container, text="System restored successfully.\nPlease restart the application to reload state.", text_color=Theme.TEXT_PRIMARY, font=ctk.CTkFont(size=12), justify="center").grid(row=2, column=0, padx=20, pady=20)
                dialog.add_action_buttons(confirm_text="OK", on_confirm=dialog.close, cancel_text=None)

    def _render_activity_logs_card(self):
        """Render activity log history feed."""
        card = ctk.CTkFrame(self.main_container, fg_color=Theme.BG_CARD, corner_radius=12, border_width=1, border_color=Theme.BORDER_COLOR)
        card.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text="System Activity Audit Log", font=ctk.CTkFont(size=16, weight="bold"), text_color=Theme.TEXT_PRIMARY).grid(row=0, column=0, padx=20, pady=(16, 10), sticky="w")

        log_box = ctk.CTkTextbox(card, height=160, corner_radius=8, border_width=1, border_color=Theme.BORDER_COLOR, fg_color=Theme.BG_DARK)
        log_box.grid(row=1, column=0, padx=20, pady=(0, 16), sticky="ew")

        # Load logs from file
        try:
            if os.path.exists(ActivityLogService.LOG_FILE):
                with open(ActivityLogService.LOG_FILE, "r", encoding="utf-8") as f:
                    log_box.insert("1.0", f.read())
            else:
                log_box.insert("1.0", "No system activities recorded yet.")
        except Exception:
            log_box.insert("1.0", "Error loading activity logs.")

        log_box.configure(state="disabled")