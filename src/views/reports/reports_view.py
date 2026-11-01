# src/views/reports/reports_view.py
import csv
import os
import customtkinter as ctk
from datetime import datetime, timedelta
from decimal import Decimal
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.theme.theme import Theme
from src.components.dialogs import BaseDialog
from src.repositories.transaction_repository import TransactionRepository
from src.repositories.order_repository import OrderRepository
from src.utils.formatters import format_currency

class ReportsView(ctk.CTkFrame):
    """Analytics and Reports module with date filtering, Matplotlib charts, and CSV export capabilities."""
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=Theme.BG_DARK, corner_radius=0, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_container = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=25, pady=20)
        self.main_container.grid_columnconfigure(0, weight=1)

        self.selected_period = "Today"
        self._init_header_controls()

        # Analytics Shell Container
        self.content_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_container.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        self.content_container.grid_columnconfigure(0, weight=1)

        self.load_report_data()

    def _init_header_controls(self):
        """Header card with period selector and export buttons."""
        header_card = ctk.CTkFrame(self.main_container, fg_color=Theme.BG_CARD, corner_radius=12, border_width=1, border_color=Theme.BORDER_COLOR)
        header_card.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        header_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header_card, 
            text="Sales & Room Analytics", 
            font=ctk.CTkFont(size=18, weight="bold"), 
            text_color=Theme.TEXT_PRIMARY
        ).grid(row=0, column=0, padx=16, pady=14, sticky="w")

        # Period Filter Segmented Button
        self.period_selector = ctk.CTkSegmentedButton(
            header_card,
            values=["Today", "This Week", "This Month", "All Time"],
            command=self._on_period_changed,
            selected_color=Theme.ACCENT_TEAL,
            unselected_color=Theme.BG_DARK
        )
        self.period_selector.grid(row=0, column=1, padx=10, pady=14, sticky="w")
        self.period_selector.set("Today")

        # CSV Export Button
        btn_export = ctk.CTkButton(
            header_card,
            text="📊 Export CSV Report",
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=Theme.BG_HOVER,
            hover_color=Theme.ACCENT_TEAL,
            command=self.export_csv_report
        )
        btn_export.grid(row=0, column=2, padx=16, pady=14, sticky="e")

    def _on_period_changed(self, value: str):
        self.selected_period = value
        self.load_report_data()

    def _filter_transactions_by_period(self, transactions: list) -> list:
        now = datetime.now()
        filtered = []

        for t in transactions:
            try:
                t_date = datetime.strptime(t.timestamp[:10], "%Y-%m-%d")
            except Exception:
                continue

            if self.selected_period == "Today":
                if t_date.date() == now.date():
                    filtered.append(t)
            elif self.selected_period == "This Week":
                start_week = now.date() - timedelta(days=now.weekday())
                if t_date.date() >= start_week:
                    filtered.append(t)
            elif self.selected_period == "This Month":
                if t_date.year == now.year and t_date.month == now.month:
                    filtered.append(t)
            else:  # All Time
                filtered.append(t)

        return filtered

    def load_report_data(self):
        """Fetch transactions, compute aggregates, and embed Matplotlib charts."""
        for widget in self.content_container.winfo_children():
            widget.destroy()

        raw_txns = TransactionRepository.get_all()
        transactions = self._filter_transactions_by_period(raw_txns)

        # Totals computation
        total_revenue = sum(Decimal(str(t.total_paid)) for t in transactions)
        room_revenue = sum(Decimal(str(t.rental_amount)) for t in transactions)
        food_revenue = sum(Decimal(str(t.food_amount)) for t in transactions)
        total_txns = len(transactions)

        # 1. Metric Summary Cards
        summary_frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        summary_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        summary_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._create_metric_box(summary_frame, "Total Revenue", format_currency(float(total_revenue)), 0)
        self._create_metric_box(summary_frame, "Room Rental Sales", format_currency(float(room_revenue)), 1)
        self._create_metric_box(summary_frame, "Food & Beverage Sales", format_currency(float(food_revenue)), 2)
        self._create_metric_box(summary_frame, "Completed Txns", str(total_txns), 3)

        # 2. Charts Container
        chart_card = ctk.CTkFrame(self.content_container, fg_color=Theme.BG_CARD, corner_radius=12, border_width=1, border_color=Theme.BORDER_COLOR)
        chart_card.grid(row=1, column=0, sticky="nsew", pady=(0, 15))
        chart_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            chart_card, 
            text=f"Revenue Distribution & Breakdown ({self.selected_period})", 
            font=ctk.CTkFont(size=15, weight="bold"), 
            text_color=Theme.TEXT_PRIMARY
        ).grid(row=0, column=0, padx=20, pady=(16, 10), sticky="w")

        self._render_charts(chart_card, room_revenue, food_revenue, transactions)

    def _create_metric_box(self, master, title: str, value: str, col: int):
        box = ctk.CTkFrame(master, fg_color=Theme.BG_CARD, corner_radius=12, border_width=1, border_color=Theme.BORDER_COLOR)
        box.grid(row=0, column=col, padx=6, sticky="nsew")
        box.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(box, text=title, font=ctk.CTkFont(size=11, weight="bold"), text_color=Theme.TEXT_MUTED).grid(row=0, column=0, padx=16, pady=(14, 2), sticky="w")
        ctk.CTkLabel(box, text=value, font=ctk.CTkFont(size=18, weight="bold"), text_color=Theme.ACCENT_TEAL).grid(row=1, column=0, padx=16, pady=(0, 14), sticky="w")

    def _render_charts(self, master, room_rev: Decimal, food_rev: Decimal, transactions: list):
        try:
            plt.style.use("dark_background")
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.5), facecolor="#1E222B")

            for ax in (ax1, ax2):
                ax.set_facecolor("#161920")
                ax.tick_params(colors="#8A92A6", labelsize=9)

            # Chart 1: Revenue Channels Split
            channels = ["Room Rental", "Food & Beverage"]
            amounts = [float(room_rev), float(food_rev)]
            colors = ["#1ABC9C", "#3498DB"]

            if sum(amounts) > 0:
                ax1.pie(amounts, labels=channels, colors=colors, autopct="%1.1f%%", textprops={"color": "#F0F2F5", "fontsize": 9})
            else:
                ax1.text(0.5, 0.5, "No revenue data for period", color="#8A92A6", ha="center", va="center")
            ax1.set_title("Revenue Split by Category", fontsize=11, color="#F0F2F5", fontweight="bold")

            # Chart 2: Payment Method Breakdown
            method_counts = {}
            for t in transactions:
                method = getattr(t, "payment_method", "Cash") or "Cash"
                method_counts[method] = method_counts.get(method, 0) + float(t.total_paid)

            if method_counts:
                methods = list(method_counts.keys())
                vals = list(method_counts.values())
                ax2.bar(methods, vals, color="#2ECC71", width=0.5)
            else:
                ax2.text(0.5, 0.5, "No transactions recorded", color="#8A92A6", ha="center", va="center")
            ax2.set_title("Collected Revenue by Payment Method", fontsize=11, color="#F0F2F5", fontweight="bold")

            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=master)
            canvas.draw()
            canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        except Exception as e:
            ctk.CTkLabel(master, text=f"Unable to render charts: {str(e)}", text_color=Theme.TEXT_MUTED).grid(row=1, column=0, pady=20)

    def export_csv_report(self):
        """Export current filtered transaction report to reports/ directory in CSV format."""
        raw_txns = TransactionRepository.get_all()
        transactions = self._filter_transactions_by_period(raw_txns)

        reports_dir = "reports"
        os.makedirs(reports_dir, exist_ok=True)
        filename = f"sales_report_{self.selected_period.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(reports_dir, filename)

        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Transaction ID", "Session/Order ID", "Customer ID", "Timestamp", "Rental Amount", "Food Amount", "Discount", "Total Paid", "Payment Method"])
                for t in transactions:
                    writer.writerow([
                        t.transaction_id,
                        t.session_id or t.order_id,
                        t.customer_id,
                        t.timestamp,
                        f"{t.rental_amount:.2f}",
                        f"{t.food_amount:.2f}",
                        f"{t.discount_amount:.2f}",
                        f"{t.total_paid:.2f}",
                        getattr(t, "payment_method", "Cash")
                    ])

            dialog = BaseDialog(self, title="Export Successful", width=420, height=200)
            ctk.CTkLabel(dialog.container, text=f"Report exported successfully to:\n{filepath}", text_color=Theme.TEXT_PRIMARY, font=ctk.CTkFont(size=12), justify="center").grid(row=2, column=0, padx=20, pady=20)
            dialog.add_action_buttons(confirm_text="OK", on_confirm=dialog.close, cancel_text=None)
        except Exception as e:
            dialog = BaseDialog(self, title="Export Failed", width=400, height=200)
            ctk.CTkLabel(dialog.container, text=f"Failed to export CSV: {str(e)}", text_color="#E74C3C", font=ctk.CTkFont(size=12)).grid(row=2, column=0, padx=20, pady=20)
            dialog.add_action_buttons(confirm_text="OK", on_confirm=dialog.close, cancel_text=None)