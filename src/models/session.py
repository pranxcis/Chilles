# src/models/session.py
from datetime import datetime
from decimal import Decimal

class RoomSession:
    """Model representing an active or completed KTV room rental session."""
    def __init__(
        self,
        session_id: str,
        room_id: str,
        customer_id: str,
        start_time: str,
        duration_hours: float,
        end_time: str,
        hourly_rate: float | Decimal,
        package_id: str = "",
        status: str = "Active",          # "Active", "Extended", "Completed", "Cancelled"
        orders: list = None,
        rental_amount: float | Decimal = 0.00,
        food_amount: float | Decimal = 0.00,
        overtime_minutes: int = 0,
        overtime_amount: float | Decimal = 0.00,
        total_amount: float | Decimal = 0.00
    ):
        self.session_id = session_id
        self.room_id = room_id
        self.customer_id = customer_id
        self.start_time = start_time
        self.duration_hours = float(duration_hours)
        self.end_time = end_time
        self.hourly_rate = Decimal(str(hourly_rate))
        self.package_id = package_id
        self.status = status
        self.orders = orders or []
        self.rental_amount = Decimal(str(rental_amount))
        self.food_amount = Decimal(str(food_amount))
        self.overtime_minutes = int(overtime_minutes)
        self.overtime_amount = Decimal(str(overtime_amount))
        self.total_amount = Decimal(str(total_amount))
        self.compute_totals()

    def compute_totals(self):
        self.rental_amount = self.hourly_rate * Decimal(str(self.duration_hours))
        self.food_amount = sum(Decimal(str(item.get("subtotal", "0.00"))) for item in self.orders)
        self.total_amount = self.rental_amount + self.food_amount + self.overtime_amount

    def to_dict(self) -> dict:
        self.compute_totals()
        return {
            "session_id": self.session_id,
            "room_id": self.room_id,
            "customer_id": self.customer_id,
            "start_time": self.start_time,
            "duration_hours": self.duration_hours,
            "end_time": self.end_time,
            "hourly_rate": str(self.hourly_rate),
            "package_id": self.package_id,
            "status": self.status,
            "orders": self.orders,
            "rental_amount": str(self.rental_amount),
            "food_amount": str(self.food_amount),
            "overtime_minutes": self.overtime_minutes,
            "overtime_amount": str(self.overtime_amount),
            "total_amount": str(self.total_amount)
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            session_id=data.get("session_id"),
            room_id=data.get("room_id"),
            customer_id=data.get("customer_id"),
            start_time=data.get("start_time"),
            duration_hours=data.get("duration_hours", 1.0),
            end_time=data.get("end_time"),
            hourly_rate=Decimal(data.get("hourly_rate", "0.00")),
            package_id=data.get("package_id", ""),
            status=data.get("status", "Active"),
            orders=data.get("orders", []),
            rental_amount=Decimal(data.get("rental_amount", "0.00")),
            food_amount=Decimal(data.get("food_amount", "0.00")),
            overtime_minutes=int(data.get("overtime_minutes", 0)),
            overtime_amount=Decimal(data.get("overtime_amount", "0.00")),
            total_amount=Decimal(data.get("total_amount", "0.00"))
        )