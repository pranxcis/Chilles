# src/views/orders/order_management_view.py
import customtkinter as ctk
from decimal import Decimal
from src.theme.theme import Theme
from src.components.dialogs import BaseDialog
from src.components.status_badges import StatusBadge
from src.services.order_service import OrderService
from src.services.session_service import SessionService
from src.services.product_service import ProductService
from src.repositories.session_repository import SessionRepository
from src.repositories.room_repository import RoomRepository
from src.repositories.customer_repository import CustomerRepository
from src.repositories.product_repository import ProductRepository
from src.core.state_manager import StateManager
from src.utils.formatters import format_currency

class OrderManagementView(ctk.CTkFrame):
    """Professional POS & Order Management Console with session binding, sorted category filtering, and upfront receipt previews."""
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=Theme.BG_DARK, corner_radius=0, **kwargs)
        
        self.cart_items = {}  # {product_id: {"product": obj, "quantity": int, "subtotal": Decimal}}
        self.selected_session_id = None
        self.selected_category = "All"

        self.grid_columnconfigure(0, weight=3)  # Left: Room Binder & Menu Catalog
        self.grid_columnconfigure(1, weight=2)  # Right: Cart Terminal & Tickets Feed
        self.grid_rowconfigure(0, weight=1)

        # =========================================================================
        # LEFT PANEL: Room Session Binder & Menu Catalog
        # =========================================================================
        self.left_container = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.left_container.grid(row=0, column=0, sticky="nsew", padx=(24, 12), pady=20)
        self.left_container.grid_columnconfigure(0, weight=1)

        self._build_session_binder_section()
        self._build_menu_catalog_section()

        # =========================================================================
        # RIGHT PANEL: Cart Terminal & Order Tickets Feed
        # =========================================================================
        self.right_container = ctk.CTkFrame(self, fg_color="transparent")
        self.right_container.grid(row=0, column=1, sticky="nsew", padx=(12, 24), pady=20)
        self.right_container.grid_columnconfigure(0, weight=1)
        self.right_container.grid_rowconfigure(0, weight=3)
        self.right_container.grid_rowconfigure(1, weight=2)

        self._build_cart_terminal()
        self._build_tickets_history_feed()

        # Initial Load State
        self.load_active_sessions()
        self.load_menu_products()
        self.load_recent_tickets()

        # Check for preselected target session passed via state navigation
        target_sid = StateManager.get("target_session_id")
        if target_sid:
            StateManager.set("target_session_id", None)
            self.select_session(target_sid)

    # -------------------------------------------------------------------------
    # 1. Active Room Session Binder Section
    # -------------------------------------------------------------------------
    def _build_session_binder_section(self):
        section_card = ctk.CTkFrame(self.left_container, fg_color=Theme.BG_CARD, corner_radius=12, border_width=1, border_color=Theme.BORDER_COLOR)
        section_card.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        section_card.grid_columnconfigure(0, weight=1)

        header_frame = ctk.CTkFrame(section_card, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 8))
        header_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header_frame, text="ROOM SESSION BINDER", font=ctk.CTkFont(size=12, weight="bold"), text_color=Theme.TEXT_MUTED).grid(row=0, column=0, sticky="w")
        
        self.lbl_active_session_badge = ctk.CTkLabel(header_frame, text="• No Room Selected", font=ctk.CTkFont(size=12, weight="bold"), text_color="#E74C3C")
        self.lbl_active_session_badge.grid(row=0, column=1, sticky="e")

        self.entry_room_search = ctk.CTkEntry(section_card, placeholder_text="🔍 Search active room or guest name...", height=38, font=ctk.CTkFont(size=12))
        self.entry_room_search.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 12))
        self.entry_room_search.bind("<KeyRelease>", lambda e: self.load_active_sessions())

        self.rooms_scroll_frame = ctk.CTkScrollableFrame(section_card, orientation="horizontal", height=110, fg_color=Theme.BG_HOVER, corner_radius=8)
        self.rooms_scroll_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 16))

    def load_active_sessions(self):
        for widget in self.rooms_scroll_frame.winfo_children():
            widget.destroy()

        query = self.entry_room_search.get().strip().lower()
        active_sessions = SessionService.get_active_sessions()

        filtered_sessions = []
        for s in active_sessions:
            room = RoomRepository.get_by_id(s.room_id)
            cust = CustomerRepository.get_by_id(s.customer_id)
            r_name = room.name if room else ""
            c_name = cust.full_name if cust else "Guest"
            
            if not query or query in r_name.lower() or query in c_name.lower():
                filtered_sessions.append((s, room, cust))

        if not filtered_sessions:
            ctk.CTkLabel(self.rooms_scroll_frame, text="No active room sessions currently running.", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12)).pack(padx=20, pady=35)
            return

        for session, room, cust in filtered_sessions:
            is_selected = (session.session_id == self.selected_session_id)
            border_c = Theme.ACCENT_TEAL if is_selected else Theme.BORDER_COLOR
            bg_c = Theme.BG_CARD if is_selected else Theme.BG_DARK

            card = ctk.CTkFrame(self.rooms_scroll_frame, fg_color=bg_c, width=190, corner_radius=10, border_width=2 if is_selected else 1, border_color=border_c)
            card.pack(side="left", padx=6, pady=6, fill="y")
            card.pack_propagate(False)

            r_title = room.name if room else "Room"
            c_title = cust.full_name if cust else "Guest"

            ctk.CTkLabel(card, text=r_title, font=ctk.CTkFont(size=13, weight="bold"), text_color=Theme.TEXT_PRIMARY).pack(anchor="w", padx=10, pady=(8, 0))
            ctk.CTkLabel(card, text=f"Guest: {c_title}", font=ctk.CTkFont(size=11), text_color=Theme.TEXT_MUTED).pack(anchor="w", padx=10, pady=(0, 4))

            btn_sel = ctk.CTkButton(
                card,
                text="LINKED" if is_selected else "Select Room",
                height=26,
                corner_radius=6,
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color=Theme.ACCENT_TEAL if is_selected else Theme.BG_HOVER,
                hover_color=Theme.ACCENT_HOVER if hasattr(Theme, 'ACCENT_HOVER') else "#21867A",
                command=lambda sid=session.session_id: self.select_session(sid)
            )
            btn_sel.pack(fill="x", padx=10, pady=(2, 8))

    def select_session(self, session_id: str):
        self.selected_session_id = session_id
        session = SessionRepository.get_by_id(session_id)
        if session:
            room = RoomRepository.get_by_id(session.room_id)
            r_name = room.name if room else "Room"
            self.lbl_active_session_badge.configure(text=f"✓ LINKED TO {r_name.upper()}", text_color=Theme.ACCENT_TEAL)
        else:
            self.lbl_active_session_badge.configure(text="• No Room Selected", text_color="#E74C3C")
        
        self.load_active_sessions()

    # -------------------------------------------------------------------------
    # 2. Food & Beverage Menu Catalog Section
    # -------------------------------------------------------------------------
    def _build_menu_catalog_section(self):
        catalog_card = ctk.CTkFrame(self.left_container, fg_color=Theme.BG_CARD, corner_radius=12, border_width=1, border_color=Theme.BORDER_COLOR)
        catalog_card.grid(row=1, column=0, sticky="nsew")
        catalog_card.grid_columnconfigure(0, weight=1)

        top_bar = ctk.CTkFrame(catalog_card, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 10))
        top_bar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(top_bar, text="MENU ITEMS CATALOG", font=ctk.CTkFont(size=12, weight="bold"), text_color=Theme.TEXT_MUTED).grid(row=0, column=0, sticky="w")
        
        self.entry_prod_search = ctk.CTkEntry(top_bar, placeholder_text="🔍 Search menu items...", width=220, height=36, font=ctk.CTkFont(size=12))
        self.entry_prod_search.grid(row=0, column=1, sticky="e")
        self.entry_prod_search.bind("<KeyRelease>", lambda e: self.load_menu_products())

        self.cats_bar = ctk.CTkScrollableFrame(catalog_card, orientation="horizontal", height=42, fg_color="transparent")
        self.cats_bar.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 12))

        self._render_category_pills()

        self.products_grid = ctk.CTkFrame(catalog_card, fg_color="transparent")
        self.products_grid.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 16))
        self.products_grid.grid_columnconfigure((0, 1, 2), weight=1, uniform="prod_col")

    def _render_category_pills(self):
        for widget in self.cats_bar.winfo_children():
            widget.destroy()

        official_categories = [
            "All",
            "Snacks and Appetizers",
            "Rice Meals",
            "Pasta and Sharing",
            "Packaged Snacks",
            "Soft Drinks",
            "Juices and Water",
            "Coffee and Specialty Drinks",
            "Desserts"
        ]

        for cat in official_categories:
            is_active = (self.selected_category == cat)
            btn_cat = ctk.CTkButton(
                self.cats_bar,
                text=cat,
                height=30,
                corner_radius=15,
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color=Theme.ACCENT_TEAL if is_active else Theme.BG_HOVER,
                hover_color=Theme.ACCENT_HOVER if hasattr(Theme, 'ACCENT_HOVER') else "#21867A",
                command=lambda c=cat: self.filter_category(c)
            )
            btn_cat.pack(side="left", padx=4)

    def filter_category(self, category: str):
        self.selected_category = category
        self._render_category_pills()
        self.load_menu_products()

    def load_menu_products(self):
        for widget in self.products_grid.winfo_children():
            widget.destroy()

        query = self.entry_prod_search.get().strip().lower()
        products = ProductService.get_all_products()
        
        filtered = []
        for p in products:
            if not p.is_available:
                continue
            p_cat = getattr(p, "category", "General")
            cat_match = (self.selected_category == "All" or p_cat.lower() == self.selected_category.lower())
            query_match = (not query or query in p.name.lower())
            if cat_match and query_match:
                filtered.append(p)

        if not filtered:
            ctk.CTkLabel(self.products_grid, text="No menu items available in this category.", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12)).grid(row=0, column=0, columnspan=3, pady=30)
            return

        for idx, prod in enumerate(filtered):
            row = idx // 3
            col = idx % 3

            card = ctk.CTkFrame(self.products_grid, fg_color=Theme.BG_HOVER, corner_radius=10, border_width=1, border_color=Theme.BORDER_COLOR)
            card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            card.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(card, text=prod.name, font=ctk.CTkFont(size=12, weight="bold"), text_color=Theme.TEXT_PRIMARY, wraplength=130).grid(row=0, column=0, padx=10, pady=(10, 2), sticky="w")
            ctk.CTkLabel(card, text=format_currency(float(prod.price)), font=ctk.CTkFont(size=12, weight="bold"), text_color=Theme.ACCENT_TEAL).grid(row=1, column=0, padx=10, pady=(0, 8), sticky="w")

            btn_add = ctk.CTkButton(
                card,
                text="+ Add to Cart",
                height=32,
                corner_radius=6,
                fg_color=Theme.ACCENT_TEAL,
                hover_color=Theme.ACCENT_HOVER if hasattr(Theme, 'ACCENT_HOVER') else "#21867A",
                font=ctk.CTkFont(size=11, weight="bold"),
                command=lambda p=prod: self.add_to_cart(p)
            )
            btn_add.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")

    # -------------------------------------------------------------------------
    # 3. POS Cart Terminal Section
    # -------------------------------------------------------------------------
    def _build_cart_terminal(self):
        cart_card = ctk.CTkFrame(self.right_container, fg_color=Theme.BG_CARD, corner_radius=12, border_width=1, border_color=Theme.BORDER_COLOR)
        cart_card.grid(row=0, column=0, sticky="nsew", pady=(0, 15))
        cart_card.grid_columnconfigure(0, weight=1)
        cart_card.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(cart_card, text="CURRENT ORDER TERMINAL", font=ctk.CTkFont(size=12, weight="bold"), text_color=Theme.TEXT_MUTED).grid(row=0, column=0, padx=20, pady=(16, 6), sticky="w")

        self.cart_items_frame = ctk.CTkScrollableFrame(cart_card, fg_color=Theme.BG_HOVER, corner_radius=8)
        self.cart_items_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=6)
        self.cart_items_frame.grid_columnconfigure(0, weight=1)

        pay_mode_frame = ctk.CTkFrame(cart_card, fg_color="transparent")
        pay_mode_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=8)
        pay_mode_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(pay_mode_frame, text="Payment Settlement Mode *", font=ctk.CTkFont(size=11, weight="bold"), text_color=Theme.TEXT_MUTED).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 4))

        self.payment_mode_var = ctk.StringVar(value="Tab")
        
        ctk.CTkRadioButton(pay_mode_frame, text="Room Tab (Bill at Checkout)", variable=self.payment_mode_var, value="Tab", font=ctk.CTkFont(size=11, weight="bold"), fg_color=Theme.ACCENT_TEAL, command=self._update_payment_mode_notice).grid(row=1, column=0, sticky="w", pady=2)
        ctk.CTkRadioButton(pay_mode_frame, text="Pay Upfront (Cash / GCash)", variable=self.payment_mode_var, value="Upfront", font=ctk.CTkFont(size=11, weight="bold"), fg_color=Theme.ACCENT_TEAL, command=self._update_payment_mode_notice).grid(row=1, column=1, sticky="w", pady=2)

        self.lbl_payment_notice = ctk.CTkLabel(pay_mode_frame, text="• Appends items directly to running room session tab.", font=ctk.CTkFont(size=10), text_color=Theme.TEXT_MUTED)
        self.lbl_payment_notice.grid(row=2, column=0, columnspan=2, sticky="w", pady=(2, 0))

        footer = ctk.CTkFrame(cart_card, fg_color="transparent")
        footer.grid(row=3, column=0, sticky="ew", padx=20, pady=(8, 16))
        footer.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(footer, text="Subtotal Payable:", font=ctk.CTkFont(size=13, weight="bold"), text_color=Theme.TEXT_PRIMARY).grid(row=0, column=0, sticky="w")
        self.lbl_cart_total = ctk.CTkLabel(footer, text="₱0.00", font=ctk.CTkFont(size=18, weight="bold"), text_color=Theme.ACCENT_TEAL)
        self.lbl_cart_total.grid(row=0, column=1, sticky="e")

        btn_place_order = ctk.CTkButton(
            footer,
            text="SUBMIT & DISPATCH ORDER TICKET",
            height=42,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=Theme.ACCENT_TEAL,
            hover_color=Theme.ACCENT_HOVER if hasattr(Theme, 'ACCENT_HOVER') else "#21867A",
            command=self.submit_cart_order
        )
        btn_place_order.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        self.refresh_cart_display()

    def _update_payment_mode_notice(self):
        mode = self.payment_mode_var.get()
        if mode == "Tab":
            self.lbl_payment_notice.configure(text="• Appends items directly to running room session tab.")
        else:
            self.lbl_payment_notice.configure(text="• Immediate payment collected. Generates a formal receipt & sales record.")

    def add_to_cart(self, product):
        p_id = product.product_id
        if p_id in self.cart_items:
            self.cart_items[p_id]["quantity"] += 1
            self.cart_items[p_id]["subtotal"] = Decimal(str(product.price)) * Decimal(str(self.cart_items[p_id]["quantity"]))
        else:
            self.cart_items[p_id] = {
                "product": product,
                "quantity": 1,
                "subtotal": Decimal(str(product.price))
            }
        self.refresh_cart_display()

    def update_cart_quantity(self, product_id: str, delta: int):
        if product_id in self.cart_items:
            self.cart_items[product_id]["quantity"] += delta
            if self.cart_items[product_id]["quantity"] <= 0:
                del self.cart_items[product_id]
            else:
                price = Decimal(str(self.cart_items[product_id]["product"].price))
                self.cart_items[product_id]["subtotal"] = price * Decimal(str(self.cart_items[product_id]["quantity"]))
        self.refresh_cart_display()

    def refresh_cart_display(self):
        for widget in self.cart_items_frame.winfo_children():
            widget.destroy()

        grand_total = Decimal("0.00")

        if not self.cart_items:
            ctk.CTkLabel(self.cart_items_frame, text="Cart is empty.\nClick '+ Add to Cart' on items from the menu catalog.", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12)).pack(pady=35)
            self.lbl_cart_total.configure(text="₱0.00")
            return

        for p_id, item_data in self.cart_items.items():
            prod = item_data["product"]
            qty = item_data["quantity"]
            sub = item_data["subtotal"]
            grand_total += sub

            row_card = ctk.CTkFrame(self.cart_items_frame, fg_color=Theme.BG_CARD, corner_radius=6)
            row_card.pack(fill="x", pady=4, padx=4)
            row_card.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(row_card, text=prod.name, font=ctk.CTkFont(size=12, weight="bold"), text_color=Theme.TEXT_PRIMARY).grid(row=0, column=0, padx=10, pady=(6, 2), sticky="w")
            ctk.CTkLabel(row_card, text=format_currency(float(sub)), font=ctk.CTkFont(size=12, weight="bold"), text_color=Theme.ACCENT_TEAL).grid(row=0, column=1, padx=10, pady=(6, 2), sticky="e")

            qty_frame = ctk.CTkFrame(row_card, fg_color="transparent")
            qty_frame.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 6))

            ctk.CTkButton(qty_frame, text="-", width=26, height=22, corner_radius=4, fg_color=Theme.BG_HOVER, hover_color="#A93226", font=ctk.CTkFont(size=11, weight="bold"), command=lambda pid=p_id: self.update_cart_quantity(pid, -1)).pack(side="left")
            ctk.CTkLabel(qty_frame, text=str(qty), font=ctk.CTkFont(size=12, weight="bold"), width=34).pack(side="left", padx=2)
            ctk.CTkButton(qty_frame, text="+", width=26, height=22, corner_radius=4, fg_color=Theme.BG_HOVER, hover_color=Theme.ACCENT_TEAL, font=ctk.CTkFont(size=11, weight="bold"), command=lambda pid=p_id: self.update_cart_quantity(pid, 1)).pack(side="left")

        self.lbl_cart_total.configure(text=format_currency(float(grand_total)))

    def submit_cart_order(self):
        if not self.cart_items:
            return
        if not self.selected_session_id:
            self.lbl_active_session_badge.configure(text="⚠ SELECT A ROOM FIRST!", text_color="#E74C3C")
            return

        formatted_items = []
        for p_id, data in self.cart_items.items():
            formatted_items.append({
                "product_id": p_id,
                "name": data["product"].name,
                "price": str(data["product"].price),
                "quantity": data["quantity"],
                "subtotal": str(data["subtotal"])
            })

        payment_mode = self.payment_mode_var.get()
        order, msg, receipt_text = OrderService.place_cart_order(self.selected_session_id, formatted_items, payment_mode=payment_mode)

        # Clear Cart & Refresh Panels
        self.cart_items = {}
        self.refresh_cart_display()
        self.load_recent_tickets()

        # If Paid Upfront, display the official receipt/invoice preview modal
        if payment_mode == "Upfront" and receipt_text:
            self.open_receipt_preview_dialog(receipt_text)

    def open_receipt_preview_dialog(self, receipt_text: str):
        """Displays an official receipt/invoice modal upon successful upfront payment."""
        dialog = BaseDialog(self, title="Official Sales Invoice & Receipt", width=440, height=480)
        
        box = ctk.CTkScrollableFrame(dialog.container, fg_color="transparent")
        box.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        box.grid_columnconfigure(0, weight=1)

        receipt_box = ctk.CTkTextbox(box, height=320, fg_color=Theme.BG_DARK, text_color=Theme.TEXT_PRIMARY, font=ctk.CTkFont(family="Courier", size=11))
        receipt_box.pack(fill="x", pady=(0, 10))
        receipt_box.insert("0.0", receipt_text)
        receipt_box.configure(state="disabled")

        dialog.add_action_buttons(confirm_text="Close & Print", on_confirm=dialog.close)

    # -------------------------------------------------------------------------
    # 4. Recent Order Tickets Feed Section
    # -------------------------------------------------------------------------
    def _build_tickets_history_feed(self):
        tickets_card = ctk.CTkFrame(self.right_container, fg_color=Theme.BG_CARD, corner_radius=12, border_width=1, border_color=Theme.BORDER_COLOR)
        tickets_card.grid(row=1, column=0, sticky="nsew")
        tickets_card.grid_columnconfigure(0, weight=1)
        tickets_card.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(tickets_card, text="RECENT DISPATCHED TICKETS", font=ctk.CTkFont(size=12, weight="bold"), text_color=Theme.TEXT_MUTED).grid(row=0, column=0, padx=20, pady=(14, 6), sticky="w")

        self.tickets_feed_frame = ctk.CTkScrollableFrame(tickets_card, fg_color="transparent")
        self.tickets_feed_frame.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 12))
        self.tickets_feed_frame.grid_columnconfigure(0, weight=1)

    def load_recent_tickets(self):
        for widget in self.tickets_feed_frame.winfo_children():
            widget.destroy()

        orders = OrderService.get_all_orders()
        if not orders:
            ctk.CTkLabel(self.tickets_feed_frame, text="No recent tickets dispatched.", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=11)).pack(pady=20)
            return

        for order in orders[::-1][:5]:
            session = SessionRepository.get_by_id(order.session_id)
            room_name = "Room"
            if session:
                room_obj = RoomRepository.get_by_id(session.room_id)
                if room_obj:
                    room_name = room_obj.name

            card = ctk.CTkFrame(self.tickets_feed_frame, fg_color=Theme.BG_HOVER, corner_radius=8)
            card.pack(fill="x", pady=4)
            card.grid_columnconfigure(0, weight=1)

            mode_tag = "ROOM TAB" if order.payment_mode == "Tab" else "PAID UPFRONT"
            ctk.CTkLabel(card, text=f"Ticket {order.order_id} ({room_name})", font=ctk.CTkFont(size=12, weight="bold"), text_color=Theme.TEXT_PRIMARY).grid(row=0, column=0, padx=10, pady=(6, 2), sticky="w")
            ctk.CTkLabel(card, text=f"{mode_tag} • {format_currency(float(order.total_amount))}", font=ctk.CTkFont(size=11, weight="bold"), text_color=Theme.ACCENT_TEAL).grid(row=1, column=0, padx=10, pady=(0, 6), sticky="w")