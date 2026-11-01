# src/repositories/product_repository.py
from decimal import Decimal
from src.repositories.json_repository import JSONRepository
from src.models.product import Product
from src.utils.id_generator import generate_id

class ProductRepository:
    FILENAME = "products.json"

    @classmethod
    def _seed_default_products(cls) -> list[Product]:
        """Generate initial sample menu items as per the master specification."""
        defaults = [
            ("French Fries Platter", "Snacks and Appetizers", "180.00", "Crispy golden potato fries with cheese dip"),
            ("Loaded Nachos", "Snacks and Appetizers", "250.00", "Tortilla chips with ground beef, cheese sauce, and salsa"),
            ("Sizzling Pork Sisig", "Rice Meals", "220.00", "Served with steamed rice and fried egg"),
            ("Chicken Tenders with Rice", "Rice Meals", "200.00", "Breaded chicken strips with gravy and rice"),
            ("Spaghetti Bolognese", "Pasta and Sharing", "280.00", "Classic beef bolognese pasta for sharing"),
            ("Carbonara Platter", "Pasta and Sharing", "320.00", "Creamy bacon and mushroom pasta"),
            ("Assorted Potato Chips", "Packaged Snacks", "80.00", "Choice of salted or sour cream chips"),
            ("Coke (330ml Can)", "Soft Drinks", "60.00", "Chilled soda can"),
            ("Sprite (330ml Can)", "Soft Drinks", "60.00", "Chilled lemon-lime soda"),
            ("Iced Lemon Tea", "Juices and Water", "75.00", "Refreshing iced tea pitcher"),
            ("Bottled Mineral Water", "Juices and Water", "35.00", "500ml purified drinking water"),
            ("Iced Americano", "Coffee and Specialty Drinks", "110.00", "Espresso over ice"),
            ("Classic Milk Tea", "Coffee and Specialty Drinks", "130.00", "With tapioca pearls"),
            ("Chocolate Sundae", "Desserts", "120.00", "Vanilla ice cream with rich chocolate syrup")
        ]

        seeded = []
        for name, category, price, desc in defaults:
            p = Product(
                product_id=generate_id("PRD"),
                name=name,
                category=category,
                price=Decimal(price),
                description=desc,
                is_available=True
            )
            seeded.append(p)

        JSONRepository.save_data(cls.FILENAME, [p.to_dict() for p in seeded])
        return seeded

    @classmethod
    def get_all(cls) -> list[Product]:
        data = JSONRepository.load_data(cls.FILENAME)
        if not data:
            return cls._seed_default_products()
        return [Product.from_dict(item) for item in data]

    @classmethod
    def get_by_id(cls, product_id: str) -> Product | None:
        products = cls.get_all()
        for p in products:
            if p.product_id == product_id:
                return p
        return None

    @classmethod
    def save(cls, product: Product) -> bool:
        products = cls.get_all()
        index = next((i for i, p in enumerate(products) if p.product_id == product.product_id), -1)
        
        if index >= 0:
            products[index] = product
        else:
            products.append(product)
            
        return JSONRepository.save_data(cls.FILENAME, [p.to_dict() for p in products])

    @classmethod
    def delete(cls, product_id: str) -> bool:
        products = cls.get_all()
        updated = [p for p in products if p.product_id != product_id]
        return JSONRepository.save_data(cls.FILENAME, [p.to_dict() for p in updated])