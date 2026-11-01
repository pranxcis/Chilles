# src/views/products/product_management_view.py
import customtkinter as ctk
from decimal import Decimal
from src.theme.theme import Theme
from src.components.dialogs import BaseDialog
from src.repositories.product_repository import ProductRepository
from src.services.product_service import ProductService
from src.models.product import Product
from src.utils.formatters import format_currency

class ProductManagementView(ctk.CTkFrame):
    """Food & Beverage Menu Management module supporting category filtering, price updates, and availability toggles."""
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=Theme.BG_DARK, corner_radius=0, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Main Scrollable Shell Frame
        self.main_container = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.main_container.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=25, pady=20)
        self.main_container.grid_columnconfigure(0, weight=1)

        # 1. Top Control Bar (Search, Category Filter, and Add Button)
        self._init_header_controls()

        # 2. Products Grid Frame
        self.grid_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.grid_container.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        self.grid_container.grid_columnconfigure((0, 1, 2), weight=1, uniform="prod_col")

        self.load_products()

    def _init_header_controls(self):
        """Header card with search entry, category dropdown, and new item button."""
        header_card = ctk.CTkFrame(self.main_container, fg_color=Theme.BG_CARD, corner_radius=12, border_width=1, border_color=Theme.BORDER_COLOR)
        header_card.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        header_card.grid_columnconfigure(1, weight=1)

        # Search Bar
        self.search_entry = ctk.CTkEntry(
            header_card,
            placeholder_text="🔍 Search products by name or category...",
            width=280,
            height=40,
            corner_radius=8,
            fg_color=Theme.BG_DARK,
            border_color=Theme.BORDER_COLOR,
            text_color=Theme.TEXT_PRIMARY
        )
        self.search_entry.grid(row=0, column=0, padx=(16, 8), pady=14, sticky="w")
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_products())

        # Category Filter Dropdown
        self.combo_filter = ctk.CTkComboBox(
            header_card,
            values=ProductService.CATEGORIES,
            height=40,
            width=220,
            corner_radius=8,
            command=lambda v: self.load_products()
        )
        self.combo_filter.grid(row=0, column=1, padx=8, pady=14, sticky="w")
        self.combo_filter.set("All Categories")

        # Add Item Button
        self.add_btn = ctk.CTkButton(
            header_card,
            text="+ Add Menu Item",
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=Theme.ACCENT_TEAL,
            hover_color=Theme.ACCENT_HOVER if hasattr(Theme, 'ACCENT_HOVER') else "#21867A",
            command=self.open_add_product_dialog
        )
        self.add_btn.grid(row=0, column=2, padx=16, pady=14, sticky="e")

    def load_products(self):
        """Load and render menu item cards with search and category filtering applied."""
        for widget in self.grid_container.winfo_children():
            widget.destroy()

        products = ProductRepository.get_all()
        query = self.search_entry.get().strip().lower()
        cat_filter = self.combo_filter.get()

        if cat_filter and cat_filter != "All Categories":
            products = [p for p in products if p.category == cat_filter]

        if query:
            products = [p for p in products if query in p.name.lower() or query in p.category.lower()]

        if not products:
            empty_frame = ctk.CTkFrame(self.grid_container, fg_color=Theme.BG_CARD, corner_radius=12)
            empty_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=40, padx=10)
            empty_frame.grid_columnconfigure(0, weight=1)

            empty_lbl = ctk.CTkLabel(
                empty_frame,
                text="No menu products found matching your search.",
                text_color=Theme.TEXT_MUTED,
                font=ctk.CTkFont(size=14)
            )
            empty_lbl.grid(row=0, column=0, pady=35)
            return

        for idx, product in enumerate(products):
            row = idx // 3
            col = idx % 3
            
            card = self._create_product_card(self.grid_container, product)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

    def _create_product_card(self, master, product: Product) -> ctk.CTkFrame:
        """Construct a card displaying product name, price, category, availability, and controls."""
        card = ctk.CTkFrame(
            master, 
            fg_color=Theme.BG_CARD, 
            corner_radius=12,
            border_width=1,
            border_color=Theme.BORDER_COLOR
        )
        card.grid_columnconfigure(0, weight=1)

        # Header: Name & Availability Badge
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 6))
        header_frame.grid_columnconfigure(0, weight=1)

        name_lbl = ctk.CTkLabel(
            header_frame,
            text=product.name,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=Theme.TEXT_PRIMARY,
            wraplength=180,
            justify="left"
        )
        name_lbl.grid(row=0, column=0, sticky="w")

        status_color = Theme.ACCENT_TEAL if product.is_available else "#C0392B"
        status_text = "Available" if product.is_available else "Unavailable"
        
        status_pill = ctk.CTkFrame(header_frame, fg_color=Theme.BG_HOVER, corner_radius=6)
        status_pill.grid(row=0, column=1, sticky="e")
        ctk.CTkLabel(
            status_pill, 
            text=status_text, 
            font=ctk.CTkFont(size=10, weight="bold"), 
            text_color=status_color
        ).pack(padx=6, pady=3)

        # Category & Price Info Frame
        info_frame = ctk.CTkFrame(card, fg_color=Theme.BG_HOVER, corner_radius=8)
        info_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=6)
        info_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            info_frame,
            text=product.category,
            font=ctk.CTkFont(size=11),
            text_color=Theme.TEXT_MUTED
        ).grid(row=0, column=0, padx=12, pady=8, sticky="w")

        ctk.CTkLabel(
            info_frame,
            text=format_currency(float(product.price)),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=Theme.ACCENT_TEAL
        ).grid(row=0, column=1, padx=12, pady=8, sticky="e")

        # Description
        desc_str = product.description or "No description provided."
        ctk.CTkLabel(
            card,
            text=desc_str,
            font=ctk.CTkFont(size=11),
            text_color=Theme.TEXT_MUTED,
            wraplength=260,
            justify="left"
        ).grid(row=2, column=0, padx=16, pady=(4, 12), sticky="w")

        # Action Controls
        action_frame = ctk.CTkFrame(card, fg_color="transparent")
        action_frame.grid(row=3, column=0, sticky="ew", padx=14, pady=(0, 14))
        action_frame.grid_columnconfigure((0, 1, 2), weight=1)

        btn_edit = ctk.CTkButton(
            action_frame,
            text="Edit",
            height=32,
            corner_radius=6,
            fg_color=Theme.BG_HOVER,
            hover_color=Theme.ACCENT_TEAL,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda p=product: self.open_edit_product_dialog(p)
        )
        btn_edit.grid(row=0, column=0, padx=2, sticky="ew")

        toggle_txt = "Disable" if product.is_available else "Enable"
        btn_toggle = ctk.CTkButton(
            action_frame,
            text=toggle_txt,
            height=32,
            corner_radius=6,
            fg_color=Theme.BG_HOVER,
            hover_color=Theme.ACCENT_SAGE,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda pid=product.product_id: self.toggle_product_status(pid)
        )
        btn_toggle.grid(row=0, column=1, padx=2, sticky="ew")

        btn_delete = ctk.CTkButton(
            action_frame,
            text="Delete",
            height=32,
            corner_radius=6,
            fg_color="#2A1B1B",
            hover_color="#A93226",
            text_color="#F0F2F5",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda pid=product.product_id, pname=product.name: self.confirm_delete_product(pid, pname)
        )
        btn_delete.grid(row=0, column=2, padx=2, sticky="ew")

        return card

    def _build_product_form(self, dialog, product=None):
        """Construct dialog form fields for product creation/edition."""
        scroll_form = ctk.CTkScrollableFrame(dialog.container, fg_color="transparent")
        scroll_form.grid(row=2, column=0, sticky="nsew", padx=20, pady=(10, 10))
        scroll_form.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(scroll_form, text="Product Name *", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, columnspan=2, pady=(5, 2), sticky="w")
        entry_name = ctk.CTkEntry(scroll_form, placeholder_text="e.g. Sizzling Sisig", height=38)
        entry_name.grid(row=1, column=0, columnspan=2, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(scroll_form, text="Category *", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=2, column=0, padx=(0, 8), pady=(5, 2), sticky="w")
        categories_list = [c for c in ProductService.CATEGORIES if c != "All Categories"]
        combo_cat = ctk.CTkComboBox(scroll_form, values=categories_list, height=38)
        combo_cat.grid(row=3, column=0, padx=(0, 8), pady=(0, 12), sticky="ew")

        ctk.CTkLabel(scroll_form, text="Selling Price (₱) *", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=2, column=1, padx=(8, 0), pady=(5, 2), sticky="w")
        entry_price = ctk.CTkEntry(scroll_form, placeholder_text="e.g. 220.00", height=38)
        entry_price.grid(row=3, column=1, padx=(8, 0), pady=(0, 12), sticky="ew")

        ctk.CTkLabel(scroll_form, text="Description", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=4, column=0, columnspan=2, pady=(5, 2), sticky="w")
        entry_desc = ctk.CTkTextbox(scroll_form, height=65, corner_radius=8, border_width=1, border_color=Theme.BORDER_COLOR, fg_color=Theme.BG_DARK)
        entry_desc.grid(row=5, column=0, columnspan=2, pady=(0, 15), sticky="ew")

        if product:
            entry_name.insert(0, product.name)
            combo_cat.set(product.category)
            entry_price.insert(0, str(product.price))
            if product.description:
                entry_desc.insert("1.0", product.description)
        else:
            combo_cat.set("Snacks and Appetizers")
            entry_price.insert(0, "150.00")

        return {
            "name": entry_name,
            "category": combo_cat,
            "price": entry_price,
            "description": entry_desc
        }

    def open_add_product_dialog(self):
        """Modal dialog to create a new F&B product."""
        dialog = BaseDialog(self, title="Add F&B Menu Item", width=500, height=480)
        form = self._build_product_form(dialog)

        def save():
            name = form["name"].get().strip()
            cat = form["category"].get()
            desc = form["description"].get("1.0", "end-1c").strip()
            
            try:
                price = Decimal(form["price"].get().strip())
            except Exception:
                price = Decimal("0.00")

            if name and price > 0:
                ProductService.create_product(name, cat, price, desc, is_available=True)
                dialog.close()
                self.load_products()

        dialog.add_action_buttons(confirm_text="Add Menu Item", on_confirm=save)

    def open_edit_product_dialog(self, product: Product):
        """Modal dialog to modify existing product information."""
        dialog = BaseDialog(self, title=f"Edit Item: {product.name}", width=500, height=480)
        form = self._build_product_form(dialog, product=product)

        def update():
            product.name = form["name"].get().strip()
            product.category = form["category"].get()
            product.description = form["description"].get("1.0", "end-1c").strip()

            try:
                product.price = Decimal(form["price"].get().strip())
            except Exception:
                pass

            ProductService.update_product(product)
            dialog.close()
            self.load_products()

        dialog.add_action_buttons(confirm_text="Save Changes", on_confirm=update)

    def toggle_product_status(self, product_id: str):
        """Quickly toggle availability flag."""
        ProductService.toggle_availability(product_id)
        self.load_products()

    def confirm_delete_product(self, product_id: str, product_name: str):
        """Confirmation dialog before deleting a menu item."""
        dialog = BaseDialog(self, title="Confirm Deletion", width=400, height=220)
        
        msg = ctk.CTkLabel(
            dialog.container,
            text=f"Are you sure you want to delete\n'{product_name}'?",
            text_color=Theme.TEXT_PRIMARY,
            font=ctk.CTkFont(size=13),
            justify="center"
        )
        msg.grid(row=2, column=0, padx=20, pady=20)

        def delete():
            ProductService.delete_product(product_id)
            dialog.close()
            self.load_products()

        dialog.add_action_buttons(confirm_text="Delete Item", on_confirm=delete, confirm_color="#A93226")