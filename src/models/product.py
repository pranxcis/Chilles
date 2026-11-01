# src/models/product.py
from decimal import Decimal

class Product:
    """Model representing a Food or Beverage menu item without stock/inventory tracking."""
    def __init__(
        self, 
        product_id: str, 
        name: str, 
        category: str, 
        price: float | Decimal, 
        description: str = "", 
        is_available: bool = True,
        image_path: str = ""
    ):
        self.product_id = product_id
        self.name = name
        self.category = category            # e.g., "Snacks and Appetizers", "Soft Drinks"
        self.price = Decimal(str(price))
        self.description = description
        self.is_available = is_available
        self.image_path = image_path

    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "category": self.category,
            "price": str(self.price),
            "description": self.description,
            "is_available": self.is_available,
            "image_path": self.image_path
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            product_id=data.get("product_id"),
            name=data.get("name", ""),
            category=data.get("category", "General"),
            price=Decimal(data.get("price", "0.00")),
            description=data.get("description", ""),
            is_available=data.get("is_available", True),
            image_path=data.get("image_path", "")
        )