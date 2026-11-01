# src/views/packages/package_management_view.py
import customtkinter as ctk
from decimal import Decimal
from src.theme.theme import Theme
from src.components.dialogs import BaseDialog
from src.repositories.package_repository import PackageRepository
from src.services.package_service import PackageService
from src.models.package import Package
from src.utils.formatters import format_currency

class PackageManagementView(ctk.CTkFrame):
    """Packages and Promotions view for managing room-only and room + food promo bundles."""
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=Theme.BG_DARK, corner_radius=0, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Main Scrollable Shell Frame
        self.main_container = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.main_container.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=25, pady=20)
        self.main_container.grid_columnconfigure(0, weight=1)

        # 1. Header Control Bar
        self._init_header_controls()

        # 2. Packages Grid Frame
        self.grid_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.grid_container.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        self.grid_container.grid_columnconfigure((0, 1, 2), weight=1, uniform="pkg_col")

        self.load_packages()

    def _init_header_controls(self):
        """Header bar with search bar, category dropdown, and new package button."""
        header_card = ctk.CTkFrame(self.main_container, fg_color=Theme.BG_CARD, corner_radius=12, border_width=1, border_color=Theme.BORDER_COLOR)
        header_card.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        header_card.grid_columnconfigure(1, weight=1)

        self.search_entry = ctk.CTkEntry(
            header_card,
            placeholder_text="🔍 Search promo packages...",
            width=280,
            height=40,
            corner_radius=8,
            fg_color=Theme.BG_DARK,
            border_color=Theme.BORDER_COLOR,
            text_color=Theme.TEXT_PRIMARY
        )
        self.search_entry.grid(row=0, column=0, padx=(16, 8), pady=14, sticky="w")
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_packages())

        self.combo_cat = ctk.CTkComboBox(
            header_card,
            values=["All Categories", "Standard", "Medium", "Grand", "VIP", "VVIP"],
            height=40,
            width=200,
            corner_radius=8,
            command=lambda v: self.load_packages()
        )
        self.combo_cat.grid(row=0, column=1, padx=8, pady=14, sticky="w")
        self.combo_cat.set("All Categories")

        self.add_btn = ctk.CTkButton(
            header_card,
            text="+ Add Promo Package",
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=Theme.ACCENT_TEAL,
            hover_color=Theme.ACCENT_HOVER if hasattr(Theme, 'ACCENT_HOVER') else "#21867A",
            command=self.open_add_package_dialog
        )
        self.add_btn.grid(row=0, column=2, padx=16, pady=14, sticky="e")

    def load_packages(self):
        """Load and render promo cards with filter rules applied."""
        for widget in self.grid_container.winfo_children():
            widget.destroy()

        packages = PackageRepository.get_all()
        query = self.search_entry.get().strip().lower()
        cat_filter = self.combo_cat.get()

        if cat_filter and cat_filter != "All Categories":
            packages = [p for p in packages if p.category == cat_filter]

        if query:
            packages = [p for p in packages if query in p.name.lower() or query in p.category.lower()]

        if not packages:
            empty_frame = ctk.CTkFrame(self.grid_container, fg_color=Theme.BG_CARD, corner_radius=12)
            empty_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=40, padx=10)
            empty_frame.grid_columnconfigure(0, weight=1)

            empty_lbl = ctk.CTkLabel(
                empty_frame,
                text="No promotional packages found matching your query.",
                text_color=Theme.TEXT_MUTED,
                font=ctk.CTkFont(size=14)
            )
            empty_lbl.grid(row=0, column=0, pady=35)
            return

        for idx, pkg in enumerate(packages):
            row = idx // 3
            col = idx % 3
            
            card = self._create_package_card(self.grid_container, pkg)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

    def _create_package_card(self, master, pkg: Package) -> ctk.CTkFrame:
        """Construct a package card showing duration, pricing, category, food inclusions, and actions."""
        card = ctk.CTkFrame(
            master, 
            fg_color=Theme.BG_CARD, 
            corner_radius=12,
            border_width=1,
            border_color=Theme.BORDER_COLOR
        )
        card.grid_columnconfigure(0, weight=1)

        # Header: Name & Type Pill
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 6))
        header_frame.grid_columnconfigure(0, weight=1)

        name_lbl = ctk.CTkLabel(
            header_frame,
            text=pkg.name,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        name_lbl.grid(row=0, column=0, sticky="w")

        type_text = "Room + Food" if pkg.includes_food else "Room Only"
        type_color = "#3498DB" if pkg.includes_food else Theme.ACCENT_TEAL
        
        type_pill = ctk.CTkFrame(header_frame, fg_color=Theme.BG_HOVER, corner_radius=6)
        type_pill.grid(row=0, column=1, sticky="e")
        ctk.CTkLabel(
            type_pill, 
            text=type_text, 
            font=ctk.CTkFont(size=10, weight="bold"), 
            text_color=type_color
        ).pack(padx=6, pady=3)

        # Category, Duration, & Price Panel
        info_frame = ctk.CTkFrame(card, fg_color=Theme.BG_HOVER, corner_radius=8)
        info_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=6)
        info_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            info_frame,
            text=f"Cat: {pkg.category} ({pkg.duration_hours:.0f} hrs)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        ).grid(row=0, column=0, padx=12, pady=10, sticky="w")

        ctk.CTkLabel(
            info_frame,
            text=format_currency(float(pkg.price)),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=Theme.ACCENT_TEAL
        ).grid(row=0, column=1, padx=12, pady=10, sticky="e")

        # Inclusions or Description Note
        if pkg.includes_food and pkg.inclusions:
            inc_str = ", ".join([f"{i.get('product_name')} (x{i.get('quantity', 1)})" for i in pkg.inclusions])
            note_text = f"Includes: {inc_str}"
        else:
            note_text = pkg.description or "Includes room rental for specified duration."

        ctk.CTkLabel(
            card,
            text=note_text,
            font=ctk.CTkFont(size=11),
            text_color=Theme.TEXT_MUTED,
            wraplength=260,
            justify="left"
        ).grid(row=2, column=0, padx=16, pady=(4, 12), sticky="w")

        # Action Buttons Row
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
            command=lambda p=pkg: self.open_edit_package_dialog(p)
        )
        btn_edit.grid(row=0, column=0, padx=2, sticky="ew")

        toggle_txt = "Disable" if pkg.is_active else "Enable"
        btn_toggle = ctk.CTkButton(
            action_frame,
            text=toggle_txt,
            height=32,
            corner_radius=6,
            fg_color=Theme.BG_HOVER,
            hover_color=Theme.ACCENT_SAGE,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda pid=pkg.package_id: self.toggle_package_status(pid)
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
            command=lambda pid=pkg.package_id, pname=pkg.name: self.confirm_delete_package(pid, pname)
        )
        btn_delete.grid(row=0, column=2, padx=2, sticky="ew")

        return card

    def _build_package_form(self, dialog, package=None):
        """Build form fields inside modal dialog."""
        scroll_form = ctk.CTkScrollableFrame(dialog.container, fg_color="transparent")
        scroll_form.grid(row=2, column=0, sticky="nsew", padx=20, pady=(10, 10))
        scroll_form.grid_columnconfigure((0, 1), weight=1)

        # Name & Category
        ctk.CTkLabel(scroll_form, text="Package Name *", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, padx=(0, 8), pady=(5, 2), sticky="w")
        entry_name = ctk.CTkEntry(scroll_form, placeholder_text="e.g. VIP Party Bundle", height=38)
        entry_name.grid(row=1, column=0, padx=(0, 8), pady=(0, 12), sticky="ew")

        ctk.CTkLabel(scroll_form, text="Room Category *", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=1, padx=(8, 0), pady=(5, 2), sticky="w")
        combo_cat = ctk.CTkComboBox(scroll_form, values=["Standard", "Medium", "Grand", "VIP", "VVIP"], height=38)
        combo_cat.grid(row=1, column=1, padx=(8, 0), pady=(0, 12), sticky="ew")

        # Duration & Price
        ctk.CTkLabel(scroll_form, text="Duration (Hours) *", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=2, column=0, padx=(0, 8), pady=(5, 2), sticky="w")
        entry_dur = ctk.CTkEntry(scroll_form, placeholder_text="e.g. 3", height=38)
        entry_dur.grid(row=3, column=0, padx=(0, 8), pady=(0, 12), sticky="ew")

        ctk.CTkLabel(scroll_form, text="Package Price (₱) *", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=2, column=1, padx=(8, 0), pady=(5, 2), sticky="w")
        entry_price = ctk.CTkEntry(scroll_form, placeholder_text="e.g. 1500.00", height=38)
        entry_price.grid(row=3, column=1, padx=(8, 0), pady=(0, 12), sticky="ew")

        # Package Type Checkbox
        chk_food_var = ctk.BooleanVar(value=False)
        chk_food = ctk.CTkCheckBox(scroll_form, text="Includes Food & Beverage Items", variable=chk_food_var, font=ctk.CTkFont(size=12, weight="bold"))
        chk_food.grid(row=4, column=0, columnspan=2, pady=(8, 12), sticky="w")

        # Inclusions / Notes
        ctk.CTkLabel(scroll_form, text="Description / Inclusions Summary", text_color=Theme.TEXT_MUTED, font=ctk.CTkFont(size=12, weight="bold")).grid(row=5, column=0, columnspan=2, pady=(5, 2), sticky="w")
        entry_desc = ctk.CTkTextbox(scroll_form, height=65, corner_radius=8, border_width=1, border_color=Theme.BORDER_COLOR, fg_color=Theme.BG_DARK)
        entry_desc.grid(row=6, column=0, columnspan=2, pady=(0, 15), sticky="ew")

        if package:
            entry_name.insert(0, package.name)
            combo_cat.set(package.category)
            entry_dur.insert(0, str(package.duration_hours))
            entry_price.insert(0, str(package.price))
            chk_food_var.set(package.includes_food)
            if package.description:
                entry_desc.insert("1.0", package.description)
        else:
            combo_cat.set("Standard")
            entry_dur.insert(0, "3")
            entry_price.insert(0, "1000.00")

        return {
            "name": entry_name,
            "category": combo_cat,
            "duration": entry_dur,
            "price": entry_price,
            "food_var": chk_food_var,
            "description": entry_desc
        }

    def open_add_package_dialog(self):
        """Modal dialog to create a new promotional package."""
        dialog = BaseDialog(self, title="Add Promo Package", width=520, height=520)
        form = self._build_package_form(dialog)

        def save():
            name = form["name"].get().strip()
            cat = form["category"].get()
            desc = form["description"].get("1.0", "end-1c").strip()
            includes_food = form["food_var"].get()

            try:
                dur = float(form["duration"].get().strip())
                price = Decimal(form["price"].get().strip())
            except Exception:
                dur, price = 3.0, Decimal("1000.00")

            if name and price > 0:
                PackageService.create_package(
                    name=name,
                    category=cat,
                    duration_hours=dur,
                    price=price,
                    includes_food=includes_food,
                    description=desc
                )
                dialog.close()
                self.load_packages()

        dialog.add_action_buttons(confirm_text="Create Package", on_confirm=save)

    def open_edit_package_dialog(self, package: Package):
        """Modal dialog to edit existing package settings."""
        dialog = BaseDialog(self, title=f"Edit Package: {package.name}", width=520, height=520)
        form = self._build_package_form(dialog, package=package)

        def update():
            package.name = form["name"].get().strip()
            package.category = form["category"].get()
            package.includes_food = form["food_var"].get()
            package.description = form["description"].get("1.0", "end-1c").strip()

            try:
                package.duration_hours = float(form["duration"].get().strip())
                package.price = Decimal(form["price"].get().strip())
            except Exception:
                pass

            PackageService.update_package(package)
            dialog.close()
            self.load_packages()

        dialog.add_action_buttons(confirm_text="Save Changes", on_confirm=update)

    def toggle_package_status(self, package_id: str):
        """Quickly toggle package active status."""
        PackageService.toggle_active(package_id)
        self.load_packages()

    def confirm_delete_package(self, package_id: str, package_name: str):
        """Confirmation dialog before deleting a package."""
        dialog = BaseDialog(self, title="Confirm Deletion", width=400, height=220)
        
        msg = ctk.CTkLabel(
            dialog.container,
            text=f"Are you sure you want to delete\n'{package_name}'?",
            text_color=Theme.TEXT_PRIMARY,
            font=ctk.CTkFont(size=13),
            justify="center"
        )
        msg.grid(row=2, column=0, padx=20, pady=20)

        def delete():
            PackageService.delete_package(package_id)
            dialog.close()
            self.load_packages()

        dialog.add_action_buttons(confirm_text="Delete Package", on_confirm=delete, confirm_color="#A93226")