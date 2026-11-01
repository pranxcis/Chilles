# src/views/transactions/transaction_management_view.py
import customtkinter as ctk
from src.theme.theme import Theme
from src.components.dialogs import BaseDialog
from src.repositories.transaction_repository import TransactionRepository
from src.repositories.customer_repository import CustomerRepository
from src.utils.formatters import format_currency

class TransactionManagementView(ctk.CTkFrame):
    """Financial Audit Log & RUD View for completed transactions, sales records, and receipt inspection."""
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=Theme.BG_DARK, corner_radius=0, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.main_container = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.main_container.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=24, pady=20)
        self.main_container.grid_columnconfigure(0, weight=1)

        self._build_header_controls()

        self.feed_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.feed_container.grid(row=1, column=0, sticky="nsew", pady=(14, 0))
        self.feed_container.grid_columnconfigure(0, weight=1)

        self.load_transactions()

    def _build_header_controls(self):
        header_card = ctk.CTkFrame(self.main_container, fg_color=Theme.BG_CARD, corner_radius=12, border_width=1, border_color=Theme.BORDER_COLOR)
        header_card.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        header_card.grid_columnconfigure(1, weight=1)

        title_frame = ctk.CTkFrame(header_card, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=20, pady=16, sticky="w")
        
        ctk.CTkLabel(title_frame, text="TRANSACTION AUDIT LOG (RUD)", font=ctk.CTkFont(size=14, weight="bold"), text_color=Theme.TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(title_frame, text="Compilation log for completed session bill-outs and sales records.", font=ctk.CTkFont(size=11), text_color=Theme.TEXT_MUTED).pack(anchor="w", pady=(2, 0))

        self.combo_method = ctk.CTkComboBox(
            header_card,
            values=["All Methods", "Cash", "GCash", "Credit Card", "Debit Card"],
            height=38,
            width=150,
            command=lambda v: self.load_transactions()
        )
        self.combo_method.grid(row=0, column=1, padx=12, pady=16, sticky="e")
        self.combo_method.set("All Methods")

        self.entry_search = ctk.CTkEntry(header_card, placeholder_text="🔍 Search Txn ID...", height=38, width=200)
        self.entry_search.grid(row=0, column=2, padx=20, pady=16, sticky="e")
        self.entry_search.bind("<KeyRelease>", lambda e: self.load_transactions())

    def load_transactions(self):
        for widget in self.feed_container.winfo_children():
            widget.destroy()

        transactions = TransactionRepository.get_all()
        method_filter = self.combo_method.get()
        query = self.entry_search.get().strip().lower()

        filtered = []
        for txn in transactions:
            if method_filter != "All Methods" and txn.payment_method != method_filter:
                continue
            if not query or query in txn.transaction_id.lower() or query in txn.session_id.lower():
                filtered.append(txn)

        if not filtered:
            empty_frame = ctk.CTkFrame(self.feed_container, fg_color=Theme.BG_CARD, corner_radius=12)
            empty_frame.grid(row=0, column=0, sticky="ew", pady=40, padx=10)
            empty_frame.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(empty_frame, text="No transaction logs found matching criteria.", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=13)).pack(pady=35)
            return

        for idx, txn in enumerate(filtered[::-1]):
            card = self._create_transaction_card(self.feed_container, txn)
            card.grid(row=idx, column=0, sticky="ew", pady=6)

    def _create_transaction_card(self, master, txn) -> ctk.CTkFrame:
        card = ctk.CTkFrame(master, fg_color=Theme.BG_CARD, corner_radius=10, border_width=1, border_color=Theme.BORDER_COLOR)
        card.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 4))
        header.grid_columnconfigure(0, weight=1)

        cust = CustomerRepository.get_by_id(txn.customer_id)
        c_name = cust.full_name if cust else "Guest"

        ctk.CTkLabel(header, text=f"Txn: {txn.transaction_id} — Guest: {c_name}", font=ctk.CTkFont(size=12, weight="bold"), text_color=Theme.TEXT_PRIMARY).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(header, text=txn.timestamp, font=ctk.CTkFont(size=11), text_color=Theme.TEXT_MUTED).grid(row=0, column=1, sticky="e")

        footer = ctk.CTkFrame(card, fg_color="transparent")
        footer.grid(row=1, column=0, sticky="ew", padx=16, pady=(4, 12))
        footer.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(footer, text=f"Method: {txn.payment_method} | Paid: {format_currency(float(txn.total_paid))}", font=ctk.CTkFont(size=12, weight="bold"), text_color=Theme.ACCENT_TEAL).grid(row=0, column=0, sticky="w")

        # Action Buttons (Show More / Edit / Delete)
        btns = ctk.CTkFrame(footer, fg_color="transparent")
        btns.grid(row=0, column=1, sticky="e")

        ctk.CTkButton(btns, text="Show More", width=80, height=28, fg_color=Theme.BG_HOVER, hover_color=Theme.ACCENT_TEAL, font=ctk.CTkFont(size=10, weight="bold"), command=lambda t=txn: self.open_details_dialog(t)).pack(side="left", padx=2)
        ctk.CTkButton(btns, text="Edit", width=50, height=28, fg_color=Theme.BG_HOVER, hover_color="#3498DB", font=ctk.CTkFont(size=10, weight="bold"), command=lambda t=txn: self.open_edit_dialog(t)).pack(side="left", padx=2)
        ctk.CTkButton(btns, text="Delete", width=60, height=28, fg_color="#A93226", hover_color="#C0392B", font=ctk.CTkFont(size=10, weight="bold"), command=lambda tid=txn.transaction_id: self.delete_transaction(tid)).pack(side="left", padx=2)

        return card

    def open_details_dialog(self, txn):
        dialog = BaseDialog(self, title=f"Transaction Audit Details: {txn.transaction_id}", width=460, height=400)
        
        box = ctk.CTkFrame(dialog.container, fg_color=Theme.BG_HOVER, corner_radius=8)
        box.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        box.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(box, text="Session ID:", text_color=Theme.TEXT_MUTED).grid(row=0, column=0, padx=12, pady=4, sticky="w")
        ctk.CTkLabel(box, text=txn.session_id, text_color=Theme.TEXT_PRIMARY).grid(row=0, column=1, padx=12, pady=4, sticky="e")

        ctk.CTkLabel(box, text="Rental Amount:", text_color=Theme.TEXT_MUTED).grid(row=1, column=0, padx=12, pady=4, sticky="w")
        ctk.CTkLabel(box, text=format_currency(float(txn.rental_amount)), text_color=Theme.TEXT_PRIMARY).grid(row=1, column=1, padx=12, pady=4, sticky="e")

        ctk.CTkLabel(box, text="Food Amount:", text_color=Theme.TEXT_MUTED).grid(row=2, column=0, padx=12, pady=4, sticky="w")
        ctk.CTkLabel(box, text=format_currency(float(txn.food_amount)), text_color=Theme.TEXT_PRIMARY).grid(row=2, column=1, padx=12, pady=4, sticky="e")

        ctk.CTkLabel(box, text="Overtime Amount:", text_color=Theme.TEXT_MUTED).grid(row=3, column=0, padx=12, pady=4, sticky="w")
        ctk.CTkLabel(box, text=format_currency(float(txn.overtime_amount)), text_color=Theme.TEXT_PRIMARY).grid(row=3, column=1, padx=12, pady=4, sticky="e")

        ctk.CTkLabel(box, text="Discount Applied:", text_color=Theme.TEXT_MUTED).grid(row=4, column=0, padx=12, pady=4, sticky="w")
        ctk.CTkLabel(box, text=format_currency(float(txn.discount_amount)), text_color=Theme.TEXT_PRIMARY).grid(row=4, column=1, padx=12, pady=4, sticky="e")

        ctk.CTkLabel(box, text="Total Paid:", font=ctk.CTkFont(size=12, weight="bold"), text_color=Theme.TEXT_PRIMARY).grid(row=5, column=0, padx=12, pady=(8, 12), sticky="w")
        ctk.CTkLabel(box, text=format_currency(float(txn.total_paid)), font=ctk.CTkFont(size=14, weight="bold"), text_color=Theme.ACCENT_TEAL).grid(row=5, column=1, padx=12, pady=(8, 12), sticky="e")

        dialog.add_action_buttons(confirm_text="Close", on_confirm=dialog.close)

    def open_edit_dialog(self, txn):
        dialog = BaseDialog(self, title=f"Edit Transaction: {txn.transaction_id}", width=400, height=280)
        
        form = ctk.CTkFrame(dialog.container, fg_color="transparent")
        form.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        form.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(form, text="Payment Method *", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(5, 2))
        combo_method = ctk.CTkComboBox(form, values=["Cash", "GCash", "Credit Card", "Debit Card"], height=38)
        combo_method.pack(fill="x", pady=(0, 15))
        combo_method.set(txn.payment_method)

        def save():
            txn.payment_method = combo_method.get()
            TransactionRepository.save(txn)
            dialog.close()
            self.load_transactions()

        dialog.add_action_buttons(confirm_text="Save Changes", on_confirm=save)

    def delete_transaction(self, transaction_id: str):
        TransactionRepository.delete(transaction_id)
        self.load_transactions()