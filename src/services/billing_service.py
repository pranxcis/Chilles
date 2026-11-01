# src/services/billing_service.py
from datetime import datetime
from decimal import Decimal

class BillingService:
    GRACE_PERIOD_MINUTES = 5

    @staticmethod
    def calculate_session_status(session) -> dict:
        now = datetime.now()
        try:
            end_dt = datetime.strptime(session.end_time, "%Y-%m-%d %H:%M:%S")
        except Exception:
            end_dt = now

        diff_seconds = (end_dt - now).total_seconds()
        
        if diff_seconds >= 0:
            hrs = int(diff_seconds // 3600)
            mins = int((diff_seconds % 3600) // 60)
            secs = int(diff_seconds % 60)
            time_str = f"{hrs:02d}:{mins:02d}:{secs:02d}"
            is_overtime = False
            overtime_mins = 0
            overtime_fee = Decimal("0.00")
        else:
            abs_secs = abs(diff_seconds)
            overtime_mins = int(abs_secs // 60)
            hrs = int(abs_secs // 3600)
            mins = int((abs_secs % 3600) // 60)
            secs = int(abs_secs % 60)
            time_str = f"+{hrs:02d}:{mins:02d}:{secs:02d}"
            
            if overtime_mins > BillingService.GRACE_PERIOD_MINUTES:
                is_overtime = True
                rate_per_min = session.hourly_rate / Decimal("60.0")
                overtime_fee = rate_per_min * Decimal(str(overtime_mins))
            else:
                is_overtime = False
                overtime_fee = Decimal("0.00")

        return {
            "time_remaining_str": time_str,
            "is_overtime": is_overtime,
            "overtime_minutes": overtime_mins,
            "overtime_fee": overtime_fee
        }

    @staticmethod
    def generate_final_bill(session, discount_amount: float = 0.0) -> dict:
        status_info = BillingService.calculate_session_status(session)
        session.compute_totals()
        
        overtime_fee = status_info["overtime_fee"]
        gross_total = session.total_amount + overtime_fee
        discount = Decimal(str(discount_amount))
        net_payable = max(Decimal("0.00"), gross_total - discount)

        return {
            "rental_amount": session.rental_amount,
            "food_amount": session.food_amount,
            "overtime_minutes": status_info["overtime_minutes"],
            "overtime_fee": overtime_fee,
            "gross_total": gross_total,
            "discount_amount": discount,
            "net_payable": net_payable
        }