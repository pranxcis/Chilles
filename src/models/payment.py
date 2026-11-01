# src/models/payment.py
from datetime import datetime
from decimal import Decimal

class Payment:
    """Model representing an executed payment transaction."""
    def __init__(self, payment_id: str, session_id: str, amount: float | Decimal, method: str = "Cash", timestamp: str = None):
        self.payment_id = payment_id
        self.session_id = session_id
        self.amount = Decimal(str(amount))
        self.method = method
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> dict:
        return {
            "payment_id": self.payment_id,
            "session_id": self.session_id,
            "amount": str(self.amount),
            "method": self.method,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            payment_id=data.get("payment_id"),
            session_id=data.get("session_id"),
            amount=Decimal(data.get("amount", "0.00")),
            method=data.get("method", "Cash"),
            timestamp=data.get("timestamp")
        )