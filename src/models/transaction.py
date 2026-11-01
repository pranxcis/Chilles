# src/models/transaction.py
from datetime import datetime
from decimal import Decimal

class Transaction:
    """Model representing a completed financial transaction record for room rentals and F&B sales."""
    def __init__(
        self,
        transaction_id: str,
        session_id: str,
        customer_id: str,
        timestamp: str,
        rental_amount: float | Decimal = 0.00,
        food_amount: float | Decimal = 0.00,
        overtime_amount: float | Decimal = 0.00,
        discount_amount: float | Decimal = 0.00,
        total_paid: float | Decimal = 0.00,
        payment_method: str = "Cash"
    ):
        self.transaction_id = transaction_id
        self.session_id = session_id
        self.customer_id = customer_id
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.rental_amount = Decimal(str(rental_amount))
        self.food_amount = Decimal(str(food_amount))
        self.overtime_amount = Decimal(str(overtime_amount))
        self.discount_amount = Decimal(str(discount_amount))
        self.total_paid = Decimal(str(total_paid))
        self.payment_method = payment_method

    def to_dict(self) -> dict:
        return {
            "transaction_id": self.transaction_id,
            "session_id": self.session_id,
            "customer_id": self.customer_id,
            "timestamp": self.timestamp,
            "rental_amount": str(self.rental_amount),
            "food_amount": str(self.food_amount),
            "overtime_amount": str(self.overtime_amount),
            "discount_amount": str(self.discount_amount),
            "total_paid": str(self.total_paid),
            "payment_method": self.payment_method
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            transaction_id=data.get("transaction_id"),
            session_id=data.get("session_id", ""),
            customer_id=data.get("customer_id", ""),
            timestamp=data.get("timestamp"),
            rental_amount=Decimal(data.get("rental_amount", "0.00")),
            food_amount=Decimal(data.get("food_amount", "0.00")),
            overtime_amount=Decimal(data.get("overtime_amount", "0.00")),
            discount_amount=Decimal(data.get("discount_amount", "0.00")),
            total_paid=Decimal(data.get("total_paid", "0.00")),
            payment_method=data.get("payment_method", "Cash")
        )