# src/views/customers/customer_management_view.py
import customtkinter as ctk
from src.theme.theme import Theme
from src.components.dialogs import BaseDialog
from src.repositories.customer_repository import CustomerRepository
from src.services.customer_service import CustomerService
from src.models.customer import Customer
from src.utils.formatters import format_currency

class CustomerManagementView(ctk.CTkFrame):
    """KTV Customer Management view with full CRUD, duplicate checking, and spending metrics."""
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=Theme.BG_DARK, corner_radius=0, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Main Scrollable Shell Frame
        self.main_container = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.main_container.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=25, pady=20)
        self.main_container.grid_columnconfigure(0, weight=1)

        # 1. Top Control Bar Header
        self._init_header_controls()

        # 2. Customers Table Frame
        self.table_card = ctk.CTkFrame(
            self.main_container, 
            fg_color=Theme.BG_CARD, 
            corner_radius=12,
            border_width=1,
            border_color=Theme.BORDER_COLOR
        )
        self.table_card.grid(row=1, column=0, sticky="nsew")
        self.table_card.grid_columnconfigure(0, weight=1)

        self._init_table_header()
        
        self.rows_container = ctk.CTkFrame(self.table_card, fg_color="transparent")
        self.rows_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.rows_container.grid_columnconfigure(0, weight=1)

        self.load_customers()

    def _init_header_controls(self):
        """Header card with search entry and register button."""
        header_card = ctk.CTkFrame(self.main_container, fg_color=Theme.BG_CARD, corner_radius=12, border_width=1, border_color=Theme.BORDER_COLOR)
        header_card.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        header_card.grid_columnconfigure(1, weight=1)

        self.search_entry = ctk.CTkEntry(
            header_card,
            placeholder_text="🔍 Search guests by name or contact number...",
            width=360,
            height=40,
            corner_radius=8,
            fg_color=Theme.BG_DARK,
            border_color=Theme.BORDER_COLOR,
            text_color=Theme.TEXT_PRIMARY
        )
        self.search_entry.grid(row=0, column=0, padx=16, pady=14, sticky="w")
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_customers())

        self.add_btn = ctk.CTkButton(
            header_card,
            text="+ Register New Guest",
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=Theme.ACCENT_TEAL,
            hover_color=Theme.ACCENT_HOVER if hasattr(Theme, 'ACCENT_HOVER') else "#21867A",
            command=self.open_add_customer_dialog
        )
        self.add_btn.grid(row=0, column=2, padx=16, pady=14, sticky="e")

    def _init_table_header(self):
        """Table column header row."""
        header_row = ctk.CTkFrame(self.table_card, fg_color=Theme.BG_HOVER, corner_radius=8, height=42)
        header_row.grid(row=0, column=0, sticky="ew", padx=12, pady=12)
        
        col_weights = [2, 1.5, 2, 1, 1.2, 1.2]
        for idx, weight in enumerate(col_weights):
            header_row.grid_columnconfigure(idx, weight=int(weight * 10))

        headers = ["Full Name", "Contact No.", "Email Address", "Visits", "Total Spent", "Actions"]
        for idx, title in enumerate(headers):
            ctk.CTkLabel(
                header_row,
                text=title,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=Theme.TEXT_PRIMARY
            ).grid(row=0, column=idx, padx=10, pady=10, sticky="w")

    def load_customers(self):
        """Fetch records and render table rows."""
        for widget in self.rows_container.winfo_children():
            widget.destroy()

        customers = CustomerRepository.get_all()
        query = self.search_entry.get().strip().lower()

        if query:
            customers = [
                c for c in customers 
                if query in c.full_name.lower() or query in c.phone.lower() or query in c.email.lower()
            ]

        if not customers:
            empty_lbl = ctk.CTkLabel(
                self.rows_container,
                text="No customer records found matching your query.",
                text_color=Theme.TEXT_MUTED,
                font=ctk.CTkFont(size=13)
            )
            empty_lbl.grid(row=0, column=0, pady=40)
            return

        for idx, customer in enumerate(customers):
            self._create_customer_row(self.rows_container, customer, idx)

    def _create_customer_row(self, master, customer: Customer, row_idx: int):
        """Row item with calculated visit/spending stats."""
        row_frame = ctk.CTkFrame(master, fg_color="transparent", height=45)
        row_frame.grid(row=row_idx, column=0, sticky="ew", pady=3)
        
        col_weights = [2, 1.5, 2, 1, 1.2, 1.2]
        for idx, weight in enumerate(col_weights):
            row_frame.grid_columnconfigure(idx, weight=int(weight * 10))

        stats = CustomerService.get_customer_stats(customer.customer_id)

        ctk.CTkLabel(row_frame, text=customer.full_name, font=ctk.CTkFont(size=13, weight="bold"), text_color=Theme.TEXT_PRIMARY).grid(row=0, column=0, padx=10, sticky="w")
        ctk.CTkLabel(row_frame, text=customer.phone or "—", font=ctk.CTkFont(size=12), text_color=Theme.TEXT_MUTED).grid(row=0, column=1, padx=10, sticky="w")
        ctk.CTkLabel(row_frame, text=customer.email or "—", font=ctk.CTkFont(size=12), text_color=Theme.TEXT_MUTED).grid(row=0, column=2, padx=10, sticky="w")
        ctk.CTkLabel(row_frame, text=f"{stats['visit_count']} visits", font=ctk.CTkFont(size=12), text_color=Theme.TEXT_MUTED).grid(row=0, column=3, padx=10, sticky="w")
        ctk.CTkLabel(row_frame, text=format_currency(float(stats['total_spent'])), font=ctk.CTkFont(size=12, weight="bold"), text_color=Theme.ACCENT_TEAL).grid(row=0, column=4, padx=10, sticky="w")

        action_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        action_frame.grid(row=0, column=5, padx=10, sticky="w")

        ctk.CTkButton(
            action_frame,
            text="Edit",
            width=48,
            height=28,
            corner_radius=6,
            fg_color=Theme.BG_HOVER,
            hover_color=Theme.ACCENT_TEAL,
            font=ctk.CTkFont(size=11),
            command=lambda c=customer: self.open_edit_customer_dialog(c)
        ).pack(side="left", padx=(0, 4))

        ctk.CTkButton(
            action_frame,
            text="Del",
            width=40,
            height=28,
            corner_radius=6,
            fg_color="#2A1B1B",
            hover_color="#A93226",
            text_color="#F0F2F5",
            font=ctk.CTkFont(size=11),
            command=lambda cid=customer.customer_id, cname=customer.full_name: self.confirm_delete_customer(cid, cname)
        ).pack(side="left")

    def _build_customer_form(self, dialog, customer=None):
        """Multi-column form container for guest profile capturing."""
        scroll_form = ctk.CTkScrollableFrame(dialog.container, fg_color="transparent")
        scroll_form.grid(row=2, column=0, sticky="nsew", padx=20, pady=(10, 10))
        scroll_form.grid_columnconfigure((0, 1), weight=1)

        # First & Last Name
        ctk.CTkLabel(scroll_form, text="First Name *", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, padx=(0, 8), pady=(5, 2), sticky="w")
        entry_first = ctk.CTkEntry(scroll_form, placeholder_text="e.g. Juan", height=38)
        entry_first.grid(row=1, column=0, padx=(0, 8), pady=(0, 12), sticky="ew")

        ctk.CTkLabel(scroll_form, text="Last Name *", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=1, padx=(8, 0), pady=(5, 2), sticky="w")
        entry_last = ctk.CTkEntry(scroll_form, placeholder_text="e.g. Dela Cruz", height=38)
        entry_last.grid(row=1, column=1, padx=(8, 0), pady=(0, 12), sticky="ew")

        # Middle Name & Contact Number
        ctk.CTkLabel(scroll_form, text="Middle Name", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=2, column=0, padx=(0, 8), pady=(5, 2), sticky="w")
        entry_mid = ctk.CTkEntry(scroll_form, placeholder_text="Optional", height=38)
        entry_mid.grid(row=3, column=0, padx=(0, 8), pady=(0, 12), sticky="ew")

        ctk.CTkLabel(scroll_form, text="Contact Number *", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=2, column=1, padx=(8, 0), pady=(5, 2), sticky="w")
        entry_phone = ctk.CTkEntry(scroll_form, placeholder_text="e.g. 09171234567", height=38)
        entry_phone.grid(row=3, column=1, padx=(8, 0), pady=(0, 12), sticky="ew")

        # Email & Address
        ctk.CTkLabel(scroll_form, text="Email Address", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=4, column=0, columnspan=2, pady=(5, 2), sticky="w")
        entry_email = ctk.CTkEntry(scroll_form, placeholder_text="e.g. juan@email.com", height=38)
        entry_email.grid(row=5, column=0, columnspan=2, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(scroll_form, text="Address", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=6, column=0, columnspan=2, pady=(5, 2), sticky="w")
        entry_addr = ctk.CTkEntry(scroll_form, placeholder_text="Optional address", height=38)
        entry_addr.grid(row=7, column=0, columnspan=2, pady=(0, 12), sticky="ew")

        # Notes
        ctk.CTkLabel(scroll_form, text="Notes / Special Preferences", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=8, column=0, columnspan=2, pady=(5, 2), sticky="w")
        entry_notes = ctk.CTkTextbox(scroll_form, height=60, corner_radius=8, border_width=1, border_color=Theme.BORDER_COLOR, fg_color=Theme.BG_DARK)
        entry_notes.grid(row=9, column=0, columnspan=2, pady=(0, 15), sticky="ew")

        if customer:
            entry_first.insert(0, customer.first_name)
            entry_last.insert(0, customer.last_name)
            entry_mid.insert(0, customer.middle_name)
            entry_phone.insert(0, customer.phone)
            entry_email.insert(0, customer.email)
            entry_addr.insert(0, customer.address)
            if customer.notes:
                entry_notes.insert("1.0", customer.notes)

        return {
            "first": entry_first,
            "last": entry_last,
            "mid": entry_mid,
            "phone": entry_phone,
            "email": entry_email,
            "address": entry_addr,
            "notes": entry_notes
        }

    def open_add_customer_dialog(self):
        """Modal dialog to register a new guest with phone uniqueness validation."""
        dialog = BaseDialog(self, title="Register New Guest", width=540, height=540)
        form = self._build_customer_form(dialog)

        def save():
            first = form["first"].get().strip()
            last = form["last"].get().strip()
            phone = form["phone"].get().strip()

            if not first or not last or not phone:
                return

            cust, msg = CustomerService.create_customer(
                first_name=first,
                last_name=last,
                phone=phone,
                middle_name=form["mid"].get().strip(),
                email=form["email"].get().strip(),
                address=form["address"].get().strip(),
                notes=form["notes"].get("1.0", "end-1c").strip()
            )

            if cust:
                dialog.close()
                self.load_customers()
            else:
                err_lbl = ctk.CTkLabel(dialog.container, text=msg, text_color="#E74C3C", font=ctk.CTkFont(size=12))
                err_lbl.grid(row=3, column=0, padx=20, pady=(0, 10))

        dialog.add_action_buttons(confirm_text="Register Guest", on_confirm=save)

    def open_edit_customer_dialog(self, customer: Customer):
        """Modal dialog to update existing guest profiles."""
        dialog = BaseDialog(self, title=f"Edit Profile: {customer.full_name}", width=540, height=540)
        form = self._build_customer_form(dialog, customer=customer)

        def update():
            customer.first_name = form["first"].get().strip()
            customer.last_name = form["last"].get().strip()
            customer.middle_name = form["mid"].get().strip()
            customer.phone = form["phone"].get().strip()
            customer.email = form["email"].get().strip()
            customer.address = form["address"].get().strip()
            customer.notes = form["notes"].get("1.0", "end-1c").strip()

            success, msg = CustomerService.update_customer(customer)
            if success:
                dialog.close()
                self.load_customers()
            else:
                err_lbl = ctk.CTkLabel(dialog.container, text=msg, text_color="#E74C3C", font=ctk.CTkFont(size=12))
                err_lbl.grid(row=3, column=0, padx=20, pady=(0, 10))

        dialog.add_action_buttons(confirm_text="Save Changes", on_confirm=update)

    def confirm_delete_customer(self, customer_id: str, customer_name: str):
        """Confirmation dialog before deleting a guest record."""
        dialog = BaseDialog(self, title="Confirm Deletion", width=420, height=220)
        
        msg = ctk.CTkLabel(
            dialog.container,
            text=f"Are you sure you want to delete\n'{customer_name}'?\nHistorical transactions will be preserved.",
            text_color=Theme.TEXT_PRIMARY,
            font=ctk.CTkFont(size=13),
            justify="center"
        )
        msg.grid(row=2, column=0, padx=20, pady=20)

        def delete():
            CustomerService.delete_customer(customer_id)
            dialog.close()
            self.load_customers()

        dialog.add_action_buttons(confirm_text="Delete Guest", on_confirm=delete, confirm_color="#A93226")