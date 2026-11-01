# src/models/package.py
from decimal import Decimal

class Package:
    """Model representing promotional room bundles or room + food packages."""
    def __init__(
        self,
        package_id: str,
        name: str,
        category: str,               # "Standard", "Medium", "Grand", "VIP", "VVIP"
        duration_hours: float,
        price: float | Decimal,
        includes_food: bool = False,
        inclusions: list = None,     # List of dicts, e.g., [{"product_name": "Loaded Nachos", "quantity": 1}]
        description: str = "",
        is_active: bool = True
    ):
        self.package_id = package_id
        self.name = name
        self.category = category
        self.duration_hours = float(duration_hours)
        self.price = Decimal(str(price))
        self.includes_food = includes_food
        self.inclusions = inclusions or []
        self.description = description
        self.is_active = is_active

    def to_dict(self) -> dict:
        return {
            "package_id": self.package_id,
            "name": self.name,
            "category": self.category,
            "duration_hours": self.duration_hours,
            "price": str(self.price),
            "includes_food": self.includes_food,
            "inclusions": self.inclusions,
            "description": self.description,
            "is_active": self.is_active
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            package_id=data.get("package_id"),
            name=data.get("name", ""),
            category=data.get("category", "Standard"),
            duration_hours=data.get("duration_hours", 3.0),
            price=Decimal(data.get("price", "0.00")),
            includes_food=data.get("includes_food", False),
            inclusions=data.get("inclusions", []),
            description=data.get("description", ""),
            is_active=data.get("is_active", True)
        )