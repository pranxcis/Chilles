# src/models/customer.py
from datetime import datetime

class Customer:
    """Model representing a KTV guest with full contact, profile, and loyalty attributes."""
    def __init__(
        self, 
        customer_id: str, 
        first_name: str, 
        last_name: str, 
        phone: str, 
        registration_date: str = None, 
        middle_name: str = "", 
        email: str = "", 
        address: str = "", 
        notes: str = "", 
        loyalty_points: int = 0
    ):
        self.customer_id = customer_id
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.registration_date = registration_date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.middle_name = middle_name
        self.email = email
        self.address = address
        self.notes = notes
        self.loyalty_points = int(loyalty_points)

    @property
    def full_name(self) -> str:
        """Formatted full name representation."""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name[0]}. {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    def to_dict(self) -> dict:
        return {
            "customer_id": self.customer_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "middle_name": self.middle_name,
            "phone": self.phone,
            "registration_date": self.registration_date,
            "email": self.email,
            "address": self.address,
            "notes": self.notes,
            "loyalty_points": self.loyalty_points
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            customer_id=data.get("customer_id"),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            phone=data.get("phone", ""),
            registration_date=data.get("registration_date"),
            middle_name=data.get("middle_name", ""),
            email=data.get("email", ""),
            address=data.get("address", ""),
            notes=data.get("notes", ""),
            loyalty_points=data.get("loyalty_points", 0)
        )