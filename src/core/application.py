import customtkinter as ctk
from src.theme.theme import Theme
from src.config.app_config import AppConfig

from src.repositories.json_repository import JSONRepository

from src.components.sidebar import Sidebar
from src.components.header import Header

from src.views.dashboard.dashboard_view import DashboardView
from src.views.rooms.room_management_view import RoomManagementView
from src.views.sessions.session_management_view import SessionsView
from src.views.customers.customer_management_view import CustomerManagementView
from src.views.products.product_management_view import ProductManagementView
from src.views.packages.package_management_view import PackageManagementView
from src.views.orders.order_management_view import OrderManagementView
from src.views.transactions.transaction_management_view import TransactionManagementView
from src.views.reports.reports_view import ReportsView
from src.views.settings.settings_view import SettingsView

from src.utils.file_utils import ensure_directories_exist
from src.config.constants import BACKUP_DIR, RECEIPT_DIR, REPORT_DIR, ASSETS_DIR

class Chilles(ctk.CTk):
    """Main application window container for the KTV Management System."""
    def __init__(self):
        super().__init__()
        
        ensure_directories_exist(BACKUP_DIR, RECEIPT_DIR, REPORT_DIR, ASSETS_DIR)
        JSONRepository.load_data("business_info.json")
        
        biz = AppConfig.get_business_info()
        self.title(f"{biz.get('business_name', 'KTV System')} Management Console")
        self.geometry("1280x850")
        self.minsize(1100, 650)
        
        Theme.apply_theme()
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.sidebar = Sidebar(self, on_navigate=self.load_view)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.right_container = ctk.CTkFrame(self, fg_color=Theme.BG_DARK, corner_radius=0)
        self.right_container.grid(row=0, column=1, sticky="nsew")
        self.right_container.grid_columnconfigure(0, weight=1)
        self.right_container.grid_rowconfigure(1, weight=1)
        
        self.header = Header(self.right_container)
        self.header.grid(row=0, column=0, sticky="ew")
        
        self.content_area = ctk.CTkFrame(self.right_container, fg_color=Theme.BG_DARK, corner_radius=0)
        self.content_area.grid(row=1, column=0, sticky="nsew")
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)
        
        self.current_view_widget = None
        self.load_view("Dashboard")

    def load_view(self, view_name: str):
        if not view_name:
            return
            
        if self.current_view_widget is not None:
            self.current_view_widget.destroy()
            
        self.header.update_title(view_name)
        
        if view_name == "Dashboard":
            self.current_view_widget = DashboardView(self.content_area)
        elif view_name in ("Room Management", "Rooms"):
            self.current_view_widget = RoomManagementView(self.content_area)
        elif view_name in ("Sessions", "Room Sessions"):
            self.current_view_widget = SessionsView(self.content_area)
        elif view_name == "Customer Management" or view_name == "Customers":
            self.current_view_widget = CustomerManagementView(self.content_area)
        elif view_name in ("Food & Beverage Menu", "Products"):
            self.current_view_widget = ProductManagementView(self.content_area)
        elif view_name in ("Packages & Promos", "Packages"):
            self.current_view_widget = PackageManagementView(self.content_area)
        elif view_name in ("Order Management", "Orders"):
            self.current_view_widget = OrderManagementView(self.content_area)
        elif view_name in ("Transactions & Payments", "Transactions"):
            self.current_view_widget = TransactionManagementView(self.content_area)
        elif view_name in ("Sales Reports", "Room Analytics", "Reports"):
            self.current_view_widget = ReportsView(self.content_area)
        elif view_name in ("Business Profile", "Application Settings", "Backup & Restore", "Activity Logs", "Settings"):
            self.current_view_widget = SettingsView(self.content_area)
        else:
            self.current_view_widget = DashboardView(self.content_area)
            
        self.current_view_widget.grid(row=0, column=0, sticky="nsew")

    def run(self):
        self.mainloop()