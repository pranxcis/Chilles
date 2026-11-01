# src/models/order.py
from datetime import datetime
from decimal import Decimal

class Order:
    """Model representing an F&B order ticket with cart items and payment tracking."""
    def __init__(
        self,
        order_id: str,
        session_id: str,
        customer_id: str,
        items: list = None,               # [{"product_id": str, "name": str, "price": str, "quantity": int, "subtotal": str}]
        status: str = "Pending",          # "Pending", "Preparing", "Served", "Cancelled"
        payment_mode: str = "Tab",        # "Tab" (Pay at room checkout) or "Upfront" (Paid immediately)
        payment_status: str = "Unpaid",   # "Unpaid" or "Paid"
        total_amount: float | Decimal = 0.00,
        timestamp: str = None
    ):
        self.order_id = order_id
        self.session_id = session_id
        self.customer_id = customer_id
        self.items = items or []
        self.status = status
        self.payment_mode = payment_mode
        self.payment_status = payment_status
        self.total_amount = Decimal(str(total_amount))
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def compute_total(self):
        self.total_amount = sum(Decimal(str(i.get("subtotal", "0.00"))) for i in self.items)

    def to_dict(self) -> dict:
        self.compute_total()
        return {
            "order_id": self.order_id,
            "session_id": self.session_id,
            "customer_id": self.customer_id,
            "items": self.items,
            "status": self.status,
            "payment_mode": self.payment_mode,
            "payment_status": self.payment_status,
            "total_amount": str(self.total_amount),
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            order_id=data.get("order_id"),
            session_id=data.get("session_id", ""),
            customer_id=data.get("customer_id", ""),
            items=data.get("items", []),
            status=data.get("status", "Pending"),
            payment_mode=data.get("payment_mode", "Tab"),
            payment_status=data.get("payment_status", "Unpaid"),
            total_amount=Decimal(data.get("total_amount", "0.00")),
            timestamp=data.get("timestamp")
        )