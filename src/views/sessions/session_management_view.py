# src/views/sessions/session_management_view.py
import customtkinter as ctk
from decimal import Decimal
from src.theme.theme import Theme
from src.components.dialogs import BaseDialog
from src.components.status_badges import StatusBadge
from src.services.room_service import RoomService
from src.services.customer_service import CustomerService
from src.services.package_service import PackageService
from src.services.session_service import SessionService
from src.services.billing_service import BillingService
from src.services.receipt_service import ReceiptService
from src.repositories.session_repository import SessionRepository
from src.repositories.room_repository import RoomRepository
from src.repositories.customer_repository import CustomerRepository
from src.core.state_manager import StateManager
from src.utils.formatters import format_currency

class SessionsView(ctk.CTkFrame):
    """Master-Detail Room Console with session lifecycle management, package rates, and receipt preview checkout."""
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=Theme.BG_DARK, corner_radius=0, **kwargs)
        
        self.selected_session_id = None
        self.selected_room_id = None

        self.grid_columnconfigure(0, weight=3)  # Left: Room Master Grid
        self.grid_columnconfigure(1, weight=2)  # Right: Session Workspace & Checkout
        self.grid_rowconfigure(0, weight=1)

        # =========================================================================
        # LEFT PANEL: Room Master Status Grid
        # =========================================================================
        self.left_container = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.left_container.grid(row=0, column=0, sticky="nsew", padx=(24, 12), pady=20)
        self.left_container.grid_columnconfigure(0, weight=1)

        self._build_master_room_header()
        
        self.rooms_grid = ctk.CTkFrame(self.left_container, fg_color="transparent")
        self.rooms_grid.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        self.rooms_grid.grid_columnconfigure((0, 1), weight=1, uniform="room_col")

        # =========================================================================
        # RIGHT PANEL: Session Workspace Terminal
        # =========================================================================
        self.right_container = ctk.CTkFrame(self, fg_color="transparent")
        self.right_container.grid(row=0, column=1, sticky="nsew", padx=(12, 24), pady=20)
        self.right_container.grid_columnconfigure(0, weight=1)
        self.right_container.grid_rowconfigure(0, weight=1)

        self._build_session_workspace_panel()
        self.load_rooms_master_grid()

    def _build_master_room_header(self):
        header_card = ctk.CTkFrame(self.left_container, fg_color=Theme.BG_CARD, corner_radius=12, border_width=1, border_color=Theme.BORDER_COLOR)
        header_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header_card,
            text="ROOM MONITORING CONSOLE",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=Theme.TEXT_MUTED
        ).grid(row=0, column=0, padx=16, pady=14, sticky="w")

        self.combo_filter = ctk.CTkComboBox(
            header_card,
            values=["All Rooms", "Occupied", "Available"],
            height=34,
            width=130,
            font=ctk.CTkFont(size=11),
            command=lambda v: self.load_rooms_master_grid()
        )
        self.combo_filter.grid(row=0, column=1, padx=8, pady=14, sticky="e")
        self.combo_filter.set("All Rooms")

        btn_launch = ctk.CTkButton(
            header_card,
            text="+ Launch",
            height=34,
            width=80,
            corner_radius=6,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=Theme.ACCENT_TEAL,
            hover_color=Theme.ACCENT_HOVER if hasattr(Theme, 'ACCENT_HOVER') else "#21867A",
            command=self.open_launch_session_dialog
        )
        btn_launch.grid(row=0, column=2, padx=16, pady=14, sticky="e")

    def load_rooms_master_grid(self):
        for widget in self.rooms_grid.winfo_children():
            widget.destroy()

        rooms = RoomService.get_all_rooms()
        filter_val = self.combo_filter.get()

        if filter_val == "Occupied":
            rooms = [r for r in rooms if r.status == "Occupied"]
        elif filter_val == "Available":
            rooms = [r for r in rooms if r.status == "Available"]

        if not rooms:
            ctk.CTkLabel(self.rooms_grid, text="No rooms found.", text_color=Theme.TEXT_MUTED).grid(row=0, column=0, pady=30)
            return

        for idx, room in enumerate(rooms):
            row = idx // 2
            col = idx % 2
            
            is_selected = (room.room_id == self.selected_room_id)
            border_c = Theme.ACCENT_TEAL if is_selected else Theme.BORDER_COLOR

            card = ctk.CTkFrame(self.rooms_grid, fg_color=Theme.BG_CARD, corner_radius=10, border_width=2 if is_selected else 1, border_color=border_c)
            card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
            card.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(card, text=room.name, font=ctk.CTkFont(size=13, weight="bold"), text_color=Theme.TEXT_PRIMARY).grid(row=0, column=0, padx=12, pady=(10, 2), sticky="w")
            StatusBadge(card, status=room.status).grid(row=0, column=1, padx=12, pady=(10, 2), sticky="e")

            ctk.CTkLabel(card, text=f"{room.room_type} • {format_currency(room.hourly_rate)}/hr", font=ctk.CTkFont(size=11), text_color=Theme.TEXT_MUTED).grid(row=1, column=0, columnspan=2, padx=12, pady=(0, 8), sticky="w")

            btn_inspect = ctk.CTkButton(
                card,
                text="Manage Room",
                height=28,
                corner_radius=6,
                font=ctk.CTkFont(size=10, weight="bold"),
                fg_color=Theme.ACCENT_TEAL if is_selected else Theme.BG_HOVER,
                hover_color=Theme.ACCENT_HOVER if hasattr(Theme, 'ACCENT_HOVER') else "#21867A",
                command=lambda r=room: self.select_room_for_workspace(r)
            )
            btn_inspect.grid(row=2, column=0, columnspan=2, padx=12, pady=(0, 10), sticky="ew")

    def select_room_for_workspace(self, room):
        self.selected_room_id = room.room_id
        session = SessionRepository.get_active_by_room(room.room_id)
        self.selected_session_id = session.session_id if session else None
        
        self.load_rooms_master_grid()
        self.load_session_workspace()

    def _build_session_workspace_panel(self):
        self.workspace_card = ctk.CTkFrame(self.right_container, fg_color=Theme.BG_CARD, corner_radius=12, border_width=1, border_color=Theme.BORDER_COLOR)
        self.workspace_card.grid(row=0, column=0, sticky="nsew")
        self.workspace_card.grid_columnconfigure(0, weight=1)
        self.workspace_card.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self.workspace_card,
            text="SESSION CONTROL & WORKSPACE",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=Theme.TEXT_MUTED
        ).grid(row=0, column=0, padx=20, pady=(16, 8), sticky="w")

        self.workspace_content = ctk.CTkScrollableFrame(self.workspace_card, fg_color="transparent")
        self.workspace_content.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.workspace_content.grid_columnconfigure(0, weight=1)

        self.load_session_workspace()

    def load_session_workspace(self):
        for widget in self.workspace_content.winfo_children():
            widget.destroy()

        if not self.selected_room_id:
            ctk.CTkLabel(
                self.workspace_content,
                text="Select a room on the left to inspect session details, manage tabs, or process bill-out.",
                text_color=Theme.TEXT_MUTED,
                font=ctk.CTkFont(size=12)
            ).pack(pady=60)
            return

        room = RoomRepository.get_by_id(self.selected_room_id)
        session = SessionRepository.get_active_by_room(self.selected_room_id) if room and room.status == "Occupied" else None

        r_info = ctk.CTkFrame(self.workspace_content, fg_color=Theme.BG_HOVER, corner_radius=8)
        r_info.pack(fill="x", pady=(0, 10), padx=4)
        r_info.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(r_info, text=room.name, font=ctk.CTkFont(size=14, weight="bold"), text_color=Theme.TEXT_PRIMARY).grid(row=0, column=0, padx=12, pady=(10, 2), sticky="w")
        StatusBadge(r_info, status=room.status).grid(row=0, column=1, padx=12, pady=(10, 2), sticky="e")
        ctk.CTkLabel(r_info, text=f"Type: {room.room_type} • Rate: {format_currency(room.hourly_rate)}/hr", font=ctk.CTkFont(size=11), text_color=Theme.TEXT_MUTED).grid(row=1, column=0, columnspan=2, padx=12, pady=(0, 10), sticky="w")

        if room.status == "Occupied" and session:
            cust = CustomerRepository.get_by_id(session.customer_id)
            c_name = cust.full_name if cust else "Guest"
            status_calc = SessionService.calculate_live_status(session)
            session.compute_totals()

            s_box = ctk.CTkFrame(self.workspace_content, fg_color=Theme.BG_HOVER, corner_radius=8)
            s_box.pack(fill="x", pady=6, padx=4)
            s_box.grid_columnconfigure((0, 1), weight=1)

            ctk.CTkLabel(s_box, text=f"Guest: {c_name}", font=ctk.CTkFont(size=11, weight="bold"), text_color=Theme.TEXT_PRIMARY).grid(row=0, column=0, padx=12, pady=(8, 2), sticky="w")
            
            timer_color = "#E74C3C" if status_calc["is_overtime"] else Theme.ACCENT_TEAL
            timer_text = f"Overtime: {status_calc['time_remaining_str']}" if status_calc["is_overtime"] else f"Left: {status_calc['time_remaining_str']}"
            ctk.CTkLabel(s_box, text=timer_text, font=ctk.CTkFont(size=11, weight="bold"), text_color=timer_color).grid(row=0, column=1, padx=12, pady=(8, 2), sticky="e")

            ctk.CTkLabel(s_box, text=f"Rental: {format_currency(float(session.rental_amount))}", font=ctk.CTkFont(size=11), text_color=Theme.TEXT_MUTED).grid(row=1, column=0, padx=12, pady=2, sticky="w")
            ctk.CTkLabel(s_box, text=f"F&B Tab: {format_currency(float(session.food_amount))}", font=ctk.CTkFont(size=11), text_color=Theme.TEXT_MUTED).grid(row=1, column=1, padx=12, pady=2, sticky="e")

            # Action Buttons Row (+ Order, Extend, Transfer, End Session)
            act_frame = ctk.CTkFrame(self.workspace_content, fg_color="transparent")
            act_frame.pack(fill="x", pady=8, padx=4)
            act_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

            ctk.CTkButton(act_frame, text="+ Order", height=32, fg_color=Theme.BG_HOVER, hover_color=Theme.ACCENT_TEAL, font=ctk.CTkFont(size=11, weight="bold"), command=lambda sid=session.session_id: self.go_to_orders(sid)).grid(row=0, column=0, padx=2, sticky="ew")
            ctk.CTkButton(act_frame, text="Extend", height=32, fg_color=Theme.BG_HOVER, hover_color="#27AE60", font=ctk.CTkFont(size=11, weight="bold"), command=lambda sid=session.session_id: self.extend_session_quick(sid)).grid(row=0, column=1, padx=2, sticky="ew")
            ctk.CTkButton(act_frame, text="Move", height=32, fg_color=Theme.BG_HOVER, hover_color="#3498DB", font=ctk.CTkFont(size=11, weight="bold"), command=lambda sid=session.session_id, rid=room.room_id: self.open_transfer_dialog(sid, rid)).grid(row=0, column=2, padx=2, sticky="ew")
            ctk.CTkButton(act_frame, text="End Session", height=32, fg_color="#C0392B", hover_color="#E74C3C", text_color="#FFFFFF", font=ctk.CTkFont(size=11, weight="bold"), command=lambda sid=session.session_id: self.open_checkout_preview_dialog(sid)).grid(row=0, column=3, padx=2, sticky="ew")

        else:
            ctk.CTkLabel(self.workspace_content, text="Room is currently available.", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=11)).pack(pady=20)
            
            btn_launch_here = ctk.CTkButton(
                self.workspace_content,
                text="▶ Launch Session in this Room",
                height=38,
                corner_radius=8,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=Theme.ACCENT_TEAL,
                hover_color=Theme.ACCENT_HOVER if hasattr(Theme, 'ACCENT_HOVER') else "#21867A",
                command=lambda rid=room.room_id: self.open_launch_session_dialog(preselected_room_id=rid)
            )
            btn_launch_here.pack(fill="x", pady=10, padx=4)

    def go_to_orders(self, session_id: str):
        StateManager.set("target_session_id", session_id)
        top = self.winfo_toplevel()
        if hasattr(top, "load_view"):
            top.load_view("Order Management")

    def extend_session_quick(self, session_id: str):
        SessionService.extend_session(session_id, 1.0)
        self.load_rooms_master_grid()
        self.load_session_workspace()

    def open_checkout_preview_dialog(self, session_id: str):
        """Opens checkout modal with receipt preview and payment processing before final completion."""
        session = SessionRepository.get_by_id(session_id)
        room = RoomRepository.get_by_id(session.room_id)
        if not session or not room:
            return

        dialog = BaseDialog(self, title="Checkout & Receipt Preview", width=520, height=580)
        
        form = ctk.CTkScrollableFrame(dialog.container, fg_color="transparent")
        form.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        form.grid_columnconfigure(0, weight=1)

        # Payment Controls
        pay_card = ctk.CTkFrame(form, fg_color=Theme.BG_HOVER, corner_radius=8)
        pay_card.pack(fill="x", pady=(0, 12), padx=2)
        pay_card.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(pay_card, text="Payment Method *", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, padx=12, pady=(10, 2), sticky="w")
        combo_pay = ctk.CTkComboBox(pay_card, values=["Cash", "GCash", "Credit Card", "Debit Card"], height=34)
        combo_pay.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="ew")
        combo_pay.set("Cash")

        ctk.CTkLabel(pay_card, text="Discount (₱)", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=1, padx=12, pady=(10, 2), sticky="w")
        entry_disc = ctk.CTkEntry(pay_card, placeholder_text="0.00", height=34)
        entry_disc.grid(row=1, column=1, padx=12, pady=(0, 10), sticky="ew")
        entry_disc.insert(0, "0.00")

        # Receipt Preview Textbox
        ctk.CTkLabel(form, text="Live Invoice / Receipt Preview", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", pady=(4, 2))
        
        receipt_box = ctk.CTkTextbox(form, height=220, fg_color=Theme.BG_DARK, text_color=Theme.TEXT_PRIMARY, font=ctk.CTkFont(family="Courier", size=11))
        receipt_box.pack(fill="x", pady=(0, 10))

        def update_preview(*args):
            try:
                disc = float(entry_disc.get().strip() or "0.0")
            except Exception:
                disc = 0.0
            
            bill_summary = BillingService.generate_final_bill(session, disc)
            # Generate temporary receipt preview text
            dummy_txn_id = "TXN-PREVIEW"
            preview_text = f"""
========================================
           CHILLES KTV SYSTEM          
         OFFICIAL SALES RECEIPT        
========================================
Txn ID      : {dummy_txn_id} (Preview)
Room        : {room.name} ({room.room_type})
Session ID  : {session.session_id}
----------------------------------------
Rental Amount   : ₱{float(bill_summary['rental_amount']):.2f}
F&B Tab         : ₱{float(bill_summary['food_amount']):.2f}
Overtime Fee    : ₱{float(bill_summary['overtime_fee']):.2f}
Discount        : -₱{float(bill_summary['discount_amount']):.2f}
----------------------------------------
TOTAL PAYABLE   : ₱{float(bill_summary['net_payable']):.2f}
Payment Method  : {combo_pay.get()}
========================================
        """
            receipt_box.delete("0.0", "end")
            receipt_box.insert("0.0", preview_text.strip())

        entry_disc.bind("<KeyRelease>", update_preview)
        combo_pay.configure(command=update_preview)
        update_preview()

        def confirm_checkout():
            try:
                disc = float(entry_disc.get().strip() or "0.0")
            except Exception:
                disc = 0.0
            pm = combo_pay.get()

            SessionService.complete_session_checkout(session_id, payment_method=pm, discount_amount=disc)
            dialog.close()
            self.selected_room_id = None
            self.selected_session_id = None
            self.load_rooms_master_grid()
            self.load_session_workspace()

        dialog.add_action_buttons(confirm_text="Confirm Payment & Close Session", on_confirm=confirm_checkout, confirm_color="#1E8449")

    def open_launch_session_dialog(self, preselected_room_id=None):
        dialog = BaseDialog(self, title="Launch Room Session", width=500, height=500)
        
        form_frame = ctk.CTkScrollableFrame(dialog.container, fg_color="transparent")
        form_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        form_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(form_frame, text="Select Room *", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(5, 2))
        rooms = [f"{r.room_id} - {r.name} ({r.room_type})" for r in RoomService.get_all_rooms() if r.status == "Available"]
        combo_room = ctk.CTkComboBox(form_frame, values=rooms, height=38)
        combo_room.pack(fill="x", pady=(0, 12))
        if preselected_room_id:
            match = next((r for r in rooms if r.startswith(preselected_room_id)), None)
            if match:
                combo_room.set(match)
        elif rooms:
            combo_room.set(rooms[0])

        ctk.CTkLabel(form_frame, text="Select Guest *", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(5, 2))
        customers = [f"{c.customer_id} - {c.full_name} ({c.phone})" for c in CustomerService.get_all_customers()]
        if not customers:
            customers = ["CUST001 - Walk-in Guest (09000000000)"]
        combo_cust = ctk.CTkComboBox(form_frame, values=customers, height=38)
        combo_cust.pack(fill="x", pady=(0, 12))
        combo_cust.set(customers[0])

        ctk.CTkLabel(form_frame, text="Promotional Package (Optional)", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(5, 2))
        packages = PackageService.get_all_packages()
        pkg_options = ["None (Standard Room Hourly Rate)"] + [f"{p.package_id} - {p.name} ({format_currency(float(p.price))})" for p in packages]
        combo_pkg = ctk.CTkComboBox(form_frame, values=pkg_options, height=38)
        combo_pkg.pack(fill="x", pady=(0, 12))
        combo_pkg.set(pkg_options[0])

        ctk.CTkLabel(form_frame, text="Duration (Hours) *", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(5, 2))
        entry_dur = ctk.CTkEntry(form_frame, height=38)
        entry_dur.pack(fill="x", pady=(0, 15))
        entry_dur.insert(0, "3.0")

        def save():
            if not rooms:
                dialog.close()
                return
            room_id = combo_room.get().split(" - ")[0]
            cust_id = combo_cust.get().split(" - ")[0]
            pkg_sel = combo_pkg.get()
            pkg_id = pkg_sel.split(" - ")[0] if not pkg_sel.startswith("None") else ""

            try:
                dur = float(entry_dur.get().strip())
            except Exception:
                dur = 3.0

            room_obj = RoomService.get_room_by_id(room_id)
            rate = float(room_obj.hourly_rate) if room_obj else 250.0

            SessionService.start_session(room_id, cust_id, dur, rate, package_id=pkg_id)
            dialog.close()
            self.load_rooms_master_grid()

        dialog.add_action_buttons(confirm_text="Launch Session", on_confirm=save)

    def open_transfer_dialog(self, session_id: str, current_room_id: str):
        dialog = BaseDialog(self, title="Transfer Room", width=400, height=260)
        
        form = ctk.CTkFrame(dialog.container, fg_color="transparent")
        form.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        form.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(form, text="Target Available Room *", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(5, 2))
        avail_rooms = [f"{r.room_id} - {r.name} ({r.room_type})" for r in RoomService.get_all_rooms() if r.status == "Available"]
        combo_target = ctk.CTkComboBox(form, values=avail_rooms, height=38)
        combo_target.pack(fill="x", pady=(0, 15))
        if avail_rooms:
            combo_target.set(avail_rooms[0])

        def transfer():
            if not avail_rooms:
                dialog.close()
                return
            target_id = combo_target.get().split(" - ")[0]
            SessionService.transfer_room(session_id, target_id)
            dialog.close()
            self.load_rooms_master_grid()
            self.load_session_workspace()

        dialog.add_action_buttons(confirm_text="Confirm Transfer", on_confirm=transfer)