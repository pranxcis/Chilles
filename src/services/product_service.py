# src/services/product_service.py
from decimal import Decimal
from src.repositories.product_repository import ProductRepository
from src.models.product import Product
from src.utils.id_generator import generate_id
from src.services.activity_log_service import ActivityLogService
from src.core.state_manager import StateManager

class ProductService:
    CATEGORIES = [
        "All Categories",
        "Snacks and Appetizers",
        "Rice Meals",
        "Pasta and Sharing",
        "Packaged Snacks",
        "Soft Drinks",
        "Juices and Water",
        "Coffee and Specialty Drinks",
        "Desserts"
    ]

    @staticmethod
    def get_all_products() -> list[Product]:
        return ProductRepository.get_all()

    @staticmethod
    def create_product(name: str, category: str, price: float | str | Decimal, description: str = "", is_available: bool = True) -> Product:
        product_id = generate_id("PRD")
        product = Product(
            product_id=product_id,
            name=name,
            category=category,
            price=Decimal(str(price)),
            description=description,
            is_available=is_available
        )
        ProductRepository.save(product)
        
        user = StateManager.get("current_user", "Administrator")
        ActivityLogService.log_action(user, f"Created menu item: {name} ({category})")
        return product

    @staticmethod
    def update_product(product: Product) -> bool:
        success = ProductRepository.save(product)
        if success:
            user = StateManager.get("current_user", "Administrator")
            ActivityLogService.log_action(user, f"Updated product item: {product.name}")
        return success

    @staticmethod
    def toggle_availability(product_id: str) -> bool:
        product = ProductRepository.get_by_id(product_id)
        if product:
            product.is_available = not product.is_available
            success = ProductRepository.save(product)
            if success:
                user = StateManager.get("current_user", "Administrator")
                status_str = "Available" if product.is_available else "Unavailable"
                ActivityLogService.log_action(user, f"Set product {product.name} to {status_str}")
            return success
        return False

    @staticmethod
    def delete_product(product_id: str) -> bool:
        product = ProductRepository.get_by_id(product_id)
        success = ProductRepository.delete(product_id)
        if success and product:
            user = StateManager.get("current_user", "Administrator")
            ActivityLogService.log_action(user, f"Deleted menu product: {product.name}")
        return success