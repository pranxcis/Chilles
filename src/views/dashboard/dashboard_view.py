# src/views/dashboard/dashboard_view.py
import customtkinter as ctk
from datetime import datetime
from decimal import Decimal
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for safe embedding
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.theme.theme import Theme
from src.components.cards import MetricCard
from src.services.room_service import RoomService
from src.repositories.transaction_repository import TransactionRepository
from src.repositories.payment_repository import PaymentRepository
from src.repositories.session_repository import SessionRepository
from src.repositories.order_repository import OrderRepository
from src.utils.formatters import format_currency

class DashboardView(ctk.CTkFrame):
    """Command Center Dashboard featuring live operational stats, revenue metrics, and embedded Matplotlib analytics."""
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=Theme.BG_DARK, corner_radius=0, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main Scrollable Command Center Container
        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.scroll_container.grid(row=0, column=0, sticky="nsew", padx=25, pady=20)
        self.scroll_container.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.refresh_dashboard()

    def refresh_dashboard(self):
        """Gather real-time data from repositories and render dashboard modules."""
        for widget in self.scroll_container.winfo_children():
            widget.destroy()

        # 1. Gather Data Metrics
        rooms = RoomService.get_all_rooms()
        total_rooms = len(rooms)
        occupied_rooms = sum(1 for r in rooms if r.status == "Occupied")
        maint_rooms = sum(1 for r in rooms if r.status == "Maintenance")
        available_rooms = total_rooms - occupied_rooms - maint_rooms

        sessions = SessionRepository.get_all()
        active_sessions = [s for s in sessions if s.status == "Active"]
        today_str = datetime.now().strftime("%Y-%m-%d")

        # Financials from actual collected payments / transactions today
        transactions = TransactionRepository.get_all()
        today_txns = [t for t in transactions if t.timestamp.startswith(today_str)]
        today_revenue = sum(Decimal(str(t.total_paid)) for t in today_txns)

        orders = OrderRepository.get_all()
        pending_orders = sum(1 for o in orders if o.status == "Pending")

        # 2. Top Metric Summary Cards Row
        card_rooms = MetricCard(self.scroll_container, title="Active Rooms", value=f"{occupied_rooms} / {total_rooms}")
        card_rooms.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")

        card_revenue = MetricCard(self.scroll_container, title="Today's Collected Revenue", value=format_currency(float(today_revenue)))
        card_revenue.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")

        card_sessions = MetricCard(self.scroll_container, title="Active Sessions", value=str(len(active_sessions)))
        card_sessions.grid(row=0, column=2, padx=8, pady=8, sticky="nsew")

        card_orders = MetricCard(self.scroll_container, title="Pending Orders", value=str(pending_orders))
        card_orders.grid(row=0, column=3, padx=8, pady=8, sticky="nsew")

        # 3. Middle Section: Room Status Distribution & Quick Actions
        mid_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        mid_frame.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(12, 8))
        mid_frame.grid_columnconfigure(0, weight=2)
        mid_frame.grid_columnconfigure(1, weight=1)

        # Room Status Breakdown Card
        status_card = ctk.CTkFrame(mid_frame, fg_color=Theme.BG_CARD, corner_radius=12, border_width=1, border_color=Theme.BORDER_COLOR)
        status_card.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        status_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            status_card, 
            text="Room Operational Breakdown", 
            font=ctk.CTkFont(size=15, weight="bold"), 
            text_color=Theme.TEXT_PRIMARY
        ).grid(row=0, column=0, padx=20, pady=(16, 12), sticky="w")

        breakdown_inner = ctk.CTkFrame(status_card, fg_color="transparent")
        breakdown_inner.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 16))
        breakdown_inner.grid_columnconfigure((0, 1, 2), weight=1)

        self._create_status_pill(breakdown_inner, "Available", available_rooms, Theme.STATUS_AVAILABLE, 0)
        self._create_status_pill(breakdown_inner, "Occupied", occupied_rooms, Theme.STATUS_OCCUPIED, 1)
        self._create_status_pill(breakdown_inner, "Maintenance", maint_rooms, Theme.STATUS_MAINTENANCE, 2)

        # Quick Actions Card
        actions_card = ctk.CTkFrame(mid_frame, fg_color=Theme.BG_CARD, corner_radius=12, border_width=1, border_color=Theme.BORDER_COLOR)
        actions_card.grid(row=0, column=1, padx=(8, 0), sticky="nsew")
        actions_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            actions_card, 
            text="Quick System Actions", 
            font=ctk.CTkFont(size=15, weight="bold"), 
            text_color=Theme.TEXT_PRIMARY
        ).grid(row=0, column=0, padx=20, pady=(16, 12), sticky="w")

        btn_refresh = ctk.CTkButton(
            actions_card,
            text="🔄 Refresh Metrics",
            height=38,
            corner_radius=8,
            fg_color=Theme.BG_HOVER,
            hover_color=Theme.ACCENT_TEAL,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.refresh_dashboard
        )
        btn_refresh.grid(row=1, column=0, padx=20, pady=(0, 16), sticky="ew")

        # 4. Analytics Section: Embedded Matplotlib Charts
        analytics_frame = ctk.CTkFrame(self.scroll_container, fg_color=Theme.BG_CARD, corner_radius=12, border_width=1, border_color=Theme.BORDER_COLOR)
        analytics_frame.grid(row=2, column=0, columnspan=4, sticky="nsew", pady=(10, 10))
        analytics_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            analytics_frame,
            text="Revenue & Payment Distribution Analytics",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        ).grid(row=0, column=0, padx=20, pady=(16, 10), sticky="w")

        chart_container = ctk.CTkFrame(analytics_frame, fg_color="transparent")
        chart_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        chart_container.grid_columnconfigure((0, 1), weight=1)

        self._render_matplotlib_charts(chart_container)

        # 5. Bottom Section: Activity Feed
        recent_frame = ctk.CTkFrame(self.scroll_container, fg_color=Theme.BG_CARD, corner_radius=12, border_width=1, border_color=Theme.BORDER_COLOR)
        recent_frame.grid(row=3, column=0, columnspan=4, sticky="nsew", pady=(10, 10))
        recent_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            recent_frame,
            text="Recent Activity Log Feed",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        ).grid(row=0, column=0, padx=20, pady=(16, 10), sticky="w")

        log_lines = self._load_recent_logs()
        if log_lines:
            for idx, log_text in enumerate(log_lines):
                ctk.CTkLabel(
                    recent_frame,
                    text=log_text,
                    font=ctk.CTkFont(size=12),
                    text_color=Theme.TEXT_MUTED
                ).grid(row=idx + 1, column=0, padx=20, pady=3, sticky="w")
        else:
            ctk.CTkLabel(
                recent_frame,
                text="No recent system activities recorded yet.",
                font=ctk.CTkFont(size=12),
                text_color=Theme.TEXT_MUTED
            ).grid(row=1, column=0, padx=20, pady=(0, 16), sticky="w")

        ctk.CTkLabel(self.scroll_container, text="").grid(row=4, column=0)

    def _create_status_pill(self, master, label: str, count: int, color: str, col_idx: int):
        """Helper to build status distribution cards."""
        pill = ctk.CTkFrame(master, fg_color=Theme.BG_HOVER, corner_radius=8)
        pill.grid(row=0, column=col_idx, padx=4, sticky="nsew")
        pill.grid_columnconfigure(0, weight=1)

        dot = ctk.CTkFrame(pill, width=8, height=8, corner_radius=4, fg_color=color)
        dot.grid(row=0, column=0, padx=12, pady=(10, 2), sticky="w")

        ctk.CTkLabel(pill, text=label, font=ctk.CTkFont(size=11, weight="bold"), text_color=Theme.TEXT_MUTED).grid(row=1, column=0, padx=12, pady=(0, 2), sticky="w")
        ctk.CTkLabel(pill, text=str(count), font=ctk.CTkFont(size=20, weight="bold"), text_color=Theme.TEXT_PRIMARY).grid(row=2, column=0, padx=12, pady=(0, 10), sticky="w")

    def _render_matplotlib_charts(self, master):
        """Embed Matplotlib analytics charts into CustomTkinter container."""
        try:
            # Setup dark theme styling for matplotlib
            plt.style.use("dark_background")
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.5), facecolor="#1E222B")
            
            for ax in (ax1, ax2):
                ax.set_facecolor("#161920")
                ax.tick_params(colors="#8A92A6", labelsize=9)
                ax.spines["bottom"].set_color("#2C3240")
                ax.spines["top"].set_color("#2C3240")
                ax.spines["left"].set_color("#2C3240")
                ax.spines["right"].set_color("#2C3240")

            # Chart 1: Daily Revenue Trend (Placeholder data / real repository aggregation)
            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            revenues = [1200, 1900, 1500, 2200, 3400, 4800, 4100]
            ax1.plot(days, revenues, color="#1ABC9C", marker="o", linewidth=2)
            ax1.set_title("Weekly Revenue Trend", fontsize=11, color="#F0F2F5", fontweight="bold")
            ax1.set_ylabel("PHP (₱)", fontsize=9, color="#8A92A6")

            # Chart 2: Payment Method Distribution
            methods = ["Cash", "GCash", "Maya", "Card"]
            shares = [45, 30, 15, 10]
            colors = ["#1ABC9C", "#2ECC71", "#3498DB", "#9B59B6"]
            ax2.pie(shares, labels=methods, colors=colors, autopct="%1.0f%%", textprops={"color": "#F0F2F5", "fontsize": 9})
            ax2.set_title("Payment Methods Share", fontsize=11, color="#F0F2F5", fontweight="bold")

            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=master)
            canvas.draw()
            canvas.get_tk_widget().grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        except Exception as e:
            fallback_lbl = ctk.CTkLabel(master, text=f"Analytics charts unavailable: {str(e)}", text_color=Theme.TEXT_MUTED)
            fallback_lbl.grid(row=0, column=0, pady=20)

    def _load_recent_logs(self) -> list[str]:
        """Safely fetch the last 4 activity log entries from JSON."""
        from src.services.activity_log_service import ActivityLogService
        try:
            logs = ActivityLogService.get_formatted_logs()
            if logs:
                return logs[-4:][::-1]  # Get last 4 entries, newest first
        except Exception:
            pass
        return []