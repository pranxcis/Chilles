# src/views/rooms/room_management_view.py
import customtkinter as ctk
from src.theme.theme import Theme
from src.components.dialogs import BaseDialog
from src.components.status_badges import StatusBadge
from src.services.room_service import RoomService
from src.utils.formatters import format_currency

class RoomManagementView(ctk.CTkFrame):
    """KTV Room Management view supporting category filtering, facility lists, and full CRUD."""
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=Theme.BG_DARK, corner_radius=0, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Main Scrollable Shell Frame
        self.main_container = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.main_container.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=25, pady=20)
        self.main_container.grid_columnconfigure(0, weight=1)

        # 1. Top Control Bar (Search & Add)
        self._init_header_controls()

        # 2. Rooms Grid Container
        self.grid_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.grid_container.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        self.grid_container.grid_columnconfigure((0, 1, 2), weight=1, uniform="room_col")

        self.load_rooms()

    def _init_header_controls(self):
        """Header card with live search filter and add button."""
        header_card = ctk.CTkFrame(self.main_container, fg_color=Theme.BG_CARD, corner_radius=12, border_width=1, border_color=Theme.BORDER_COLOR)
        header_card.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        header_card.grid_columnconfigure(1, weight=1)

        self.search_entry = ctk.CTkEntry(
            header_card,
            placeholder_text="🔍 Search rooms by name, category, or status...",
            width=360,
            height=40,
            corner_radius=8,
            fg_color=Theme.BG_DARK,
            border_color=Theme.BORDER_COLOR,
            text_color=Theme.TEXT_PRIMARY
        )
        self.search_entry.grid(row=0, column=0, padx=16, pady=14, sticky="w")
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_rooms())

        self.add_btn = ctk.CTkButton(
            header_card,
            text="+ Add New Room",
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=Theme.ACCENT_TEAL,
            hover_color=Theme.ACCENT_HOVER if hasattr(Theme, 'ACCENT_HOVER') else "#21867A",
            command=self.open_add_room_dialog
        )
        self.add_btn.grid(row=0, column=2, padx=16, pady=14, sticky="e")

    def load_rooms(self):
        """Load and render room model objects in structured 3-column cards."""
        for widget in self.grid_container.winfo_children():
            widget.destroy()

        rooms = RoomService.get_all_rooms()
        query = self.search_entry.get().strip().lower()

        if query:
            rooms = [r for r in rooms if query in r.name.lower() or query in r.room_type.lower() or query in r.status.lower()]

        if not rooms:
            empty_frame = ctk.CTkFrame(self.grid_container, fg_color=Theme.BG_CARD, corner_radius=12)
            empty_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=40, padx=10)
            empty_frame.grid_columnconfigure(0, weight=1)

            empty_lbl = ctk.CTkLabel(
                empty_frame,
                text="No rooms found matching your search criteria.",
                text_color=Theme.TEXT_MUTED,
                font=ctk.CTkFont(size=14)
            )
            empty_lbl.grid(row=0, column=0, pady=35)
            return

        for idx, room in enumerate(rooms):
            row = idx // 3
            col = idx % 3
            
            card = self._create_room_card(self.grid_container, room)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

    def _create_room_card(self, master, room) -> ctk.CTkFrame:
        """Construct a room card displaying category, capacity, hourly rate, and facilities."""
        card = ctk.CTkFrame(
            master, 
            fg_color=Theme.BG_CARD, 
            corner_radius=12,
            border_width=1,
            border_color=Theme.BORDER_COLOR
        )
        card.grid_columnconfigure(0, weight=1)

        # 1. Card Header
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        header_frame.grid_columnconfigure(0, weight=1)

        name_lbl = ctk.CTkLabel(
            header_frame,
            text=room.name,
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        name_lbl.grid(row=0, column=0, sticky="w")

        badge = StatusBadge(header_frame, status=room.status)
        badge.grid(row=0, column=1, sticky="e")

        # 2. Info Panel
        info_frame = ctk.CTkFrame(card, fg_color=Theme.BG_HOVER, corner_radius=8)
        info_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=4)
        info_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            info_frame,
            text=f"Category: {room.room_type}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        ).grid(row=0, column=0, padx=12, pady=(10, 2), sticky="w")

        ctk.CTkLabel(
            info_frame,
            text=f"Capacity: Up to {room.capacity} pax",
            font=ctk.CTkFont(size=11),
            text_color=Theme.TEXT_MUTED
        ).grid(row=1, column=0, padx=12, pady=(0, 10), sticky="w")

        ctk.CTkLabel(
            info_frame,
            text=format_currency(room.hourly_rate),
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=Theme.ACCENT_TEAL
        ).grid(row=0, column=1, padx=12, pady=(10, 2), sticky="e")

        ctk.CTkLabel(
            info_frame,
            text="per hour",
            font=ctk.CTkFont(size=11),
            text_color=Theme.TEXT_MUTED
        ).grid(row=1, column=1, padx=12, pady=(0, 10), sticky="e")

        # Facilities Summary Note
        fac_str = ", ".join(room.facilities[:3]) if room.facilities else "Standard amenities"
        ctk.CTkLabel(
            card,
            text=f"Facilities: {fac_str}{'...' if len(room.facilities) > 3 else ''}",
            font=ctk.CTkFont(size=11),
            text_color=Theme.TEXT_MUTED,
            wraplength=260,
            justify="left"
        ).grid(row=2, column=0, padx=16, pady=(6, 10), sticky="w")

        # 3. Action Buttons Row
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
            command=lambda r=room: self.open_edit_room_dialog(r)
        )
        btn_edit.grid(row=0, column=0, padx=2, sticky="ew")

        toggle_text = "Maint." if room.status == "Available" else "Avail."
        toggle_status = "Maintenance" if room.status == "Available" else "Available"
        
        btn_status = ctk.CTkButton(
            action_frame,
            text=toggle_text,
            height=32,
            corner_radius=6,
            fg_color=Theme.BG_HOVER,
            hover_color=Theme.ACCENT_SAGE,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda rid=room.room_id, stat=toggle_status: self.toggle_room_status(rid, stat)
        )
        btn_status.grid(row=0, column=1, padx=2, sticky="ew")

        btn_delete = ctk.CTkButton(
            action_frame,
            text="Delete",
            height=32,
            corner_radius=6,
            fg_color="#2A1B1B",
            hover_color="#A93226",
            text_color="#F0F2F5",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda rid=room.room_id, rname=room.name: self.confirm_delete_room(rid, rname)
        )
        btn_delete.grid(row=0, column=2, padx=2, sticky="ew")

        return card

    def _build_room_form(self, dialog, room=None):
        """Construct spacious form fields inside modal dialog."""
        scroll_form = ctk.CTkScrollableFrame(dialog.container, fg_color="transparent")
        scroll_form.grid(row=2, column=0, sticky="nsew", padx=20, pady=(10, 10))
        scroll_form.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(scroll_form, text="Room Name / Number *", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, padx=(0, 10), pady=(5, 2), sticky="w")
        entry_name = ctk.CTkEntry(scroll_form, placeholder_text="e.g. VIP Room 01", height=38)
        entry_name.grid(row=1, column=0, padx=(0, 10), pady=(0, 12), sticky="ew")

        ctk.CTkLabel(scroll_form, text="Room Category *", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=1, padx=(10, 0), pady=(5, 2), sticky="w")
        combo_type = ctk.CTkComboBox(scroll_form, values=["Standard", "Medium", "Grand", "VIP", "VVIP"], height=38)
        combo_type.grid(row=1, column=1, padx=(10, 0), pady=(0, 12), sticky="ew")

        ctk.CTkLabel(scroll_form, text="Capacity (Max Persons) *", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=2, column=0, padx=(0, 10), pady=(5, 2), sticky="w")
        entry_cap = ctk.CTkEntry(scroll_form, placeholder_text="e.g. 12", height=38)
        entry_cap.grid(row=3, column=0, padx=(0, 10), pady=(0, 12), sticky="ew")

        ctk.CTkLabel(scroll_form, text="Hourly Rate (₱) *", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=2, column=1, padx=(10, 0), pady=(5, 2), sticky="w")
        entry_rate = ctk.CTkEntry(scroll_form, placeholder_text="e.g. 700.00", height=38)
        entry_rate.grid(row=3, column=1, padx=(10, 0), pady=(0, 12), sticky="ew")

        ctk.CTkLabel(scroll_form, text="Status", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=4, column=0, columnspan=2, pady=(5, 2), sticky="w")
        combo_status = ctk.CTkComboBox(scroll_form, values=["Available", "Maintenance", "Occupied"], height=38)
        combo_status.grid(row=5, column=0, columnspan=2, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(scroll_form, text="Facilities (comma separated)", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=6, column=0, columnspan=2, pady=(5, 2), sticky="w")
        entry_fac = ctk.CTkEntry(scroll_form, placeholder_text="TV, Karaoke, Microphones, Aircon", height=38)
        entry_fac.grid(row=7, column=0, columnspan=2, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(scroll_form, text="Description", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=8, column=0, columnspan=2, pady=(5, 2), sticky="w")
        entry_desc = ctk.CTkTextbox(scroll_form, height=65, corner_radius=8, border_width=1, border_color=Theme.BORDER_COLOR, fg_color=Theme.BG_DARK)
        entry_desc.grid(row=9, column=0, columnspan=2, pady=(0, 15), sticky="ew")

        if room:
            entry_name.insert(0, room.name)
            combo_type.set(room.room_type)
            entry_cap.insert(0, str(room.capacity))
            entry_rate.insert(0, str(room.hourly_rate))
            combo_status.set(room.status)
            entry_fac.insert(0, ", ".join(room.facilities))
            if room.description:
                entry_desc.insert("1.0", room.description)
        else:
            combo_type.set("Standard")
            entry_cap.insert(0, "4")
            entry_rate.insert(0, "250.0")
            combo_status.set("Available")
            entry_fac.insert(0, "TV, Karaoke, Microphones, Air Conditioning")

        return {
            "name": entry_name,
            "type": combo_type,
            "capacity": entry_cap,
            "rate": entry_rate,
            "status": combo_status,
            "facilities": entry_fac,
            "description": entry_desc
        }

    def open_add_room_dialog(self):
        """Modal window to create a new room."""
        dialog = BaseDialog(self, title="Add New KTV Room", width=540, height=560)
        form = self._build_room_form(dialog)

        def save():
            name = form["name"].get().strip()
            rtype = form["type"].get()
            status = form["status"].get()
            desc = form["description"].get("1.0", "end-1c").strip()
            fac_raw = form["facilities"].get().strip()
            facilities = [f.strip() for f in fac_raw.split(",") if f.strip()]
            
            try:
                cap = int(form["capacity"].get().strip())
                rate = float(form["rate"].get().strip())
            except ValueError:
                cap, rate = 4, 250.0

            if name:
                RoomService.create_room(
                    name=name,
                    room_type=rtype,
                    capacity=cap,
                    hourly_rate=rate,
                    status=status,
                    description=desc,
                    facilities=facilities
                )
                dialog.close()
                self.load_rooms()

        dialog.add_action_buttons(confirm_text="Create Room", on_confirm=save)

    def open_edit_room_dialog(self, room):
        """Modal window to update an existing room."""
        dialog = BaseDialog(self, title=f"Edit Room: {room.name}", width=540, height=560)
        form = self._build_room_form(dialog, room=room)

        def update():
            room.name = form["name"].get().strip()
            room.room_type = form["type"].get()
            room.status = form["status"].get()
            room.description = form["description"].get("1.0", "end-1c").strip()
            fac_raw = form["facilities"].get().strip()
            room.facilities = [f.strip() for f in fac_raw.split(",") if f.strip()]

            try:
                room.capacity = int(form["capacity"].get().strip())
                room.hourly_rate = float(form["rate"].get().strip())
            except ValueError:
                pass

            RoomService.update_room(room)
            dialog.close()
            self.load_rooms()

        dialog.add_action_buttons(confirm_text="Save Changes", on_confirm=update)

    def toggle_room_status(self, room_id: str, new_status: str):
        """Quickly toggle status between Available and Maintenance."""
        RoomService.update_room_status(room_id, new_status)
        self.load_rooms()

    def confirm_delete_room(self, room_id: str, room_name: str):
        """Prompt confirmation before deleting a room, respecting occupancy rules."""
        dialog = BaseDialog(self, title="Confirm Deletion", width=420, height=240)
        
        msg = ctk.CTkLabel(
            dialog.container,
            text=f"Are you sure you want to archive/delete\n'{room_name}'?\nThis cannot be done if the room is occupied.",
            text_color=Theme.TEXT_PRIMARY,
            font=ctk.CTkFont(size=13),
            justify="center"
        )
        msg.grid(row=2, column=0, padx=20, pady=20)

        def delete():
            success, message = RoomService.delete_room(room_id)
            dialog.close()
            if not success:
                # Show simple error dialog if occupied
                err_dlg = BaseDialog(self, title="Action Denied", width=380, height=200)
                ctk.CTkLabel(err_dlg.container, text=message, text_color="#E74C3C", font=ctk.CTkFont(size=13)).grid(row=2, column=0, padx=20, pady=20)
                err_dlg.add_action_buttons(confirm_text="OK", on_confirm=err_dlg.close, cancel_text=None)
            self.load_rooms()

        dialog.add_action_buttons(confirm_text="Delete Room", on_confirm=delete, confirm_color="#A93226")