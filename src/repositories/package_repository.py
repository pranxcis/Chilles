# src/repositories/package_repository.py
from decimal import Decimal
from src.repositories.json_repository import JSONRepository
from src.models.package import Package
from src.utils.id_generator import generate_id

class PackageRepository:
    FILENAME = "packages.json"

    @classmethod
    def _seed_default_packages(cls) -> list[Package]:
        """Generate default promotional packages from Section 4D of the spec."""
        defaults = [
            # Room-Only Packages
            ("Standard Saver", "Standard", 3.0, "650.00", False, [], "3-hour room rental bundle for Standard rooms"),
            ("Medium Barkada", "Medium", 3.0, "900.00", False, [], "3-hour room rental bundle for Medium rooms"),
            ("Grand Session", "Grand", 3.0, "1350.00", False, [], "3-hour room rental bundle for Grand rooms"),
            ("VIP Experience", "VIP", 4.0, "2500.00", False, [], "4-hour luxury room rental bundle for VIP rooms"),
            ("VVIP Experience", "VVIP", 4.0, "3600.00", False, [], "4-hour ultra-luxury room bundle for VVIP rooms"),
            
            # Room + Food Packages
            ("Barkada Bundle", "Standard", 3.0, "1000.00", True, [{"product_name": "French Fries Platter", "quantity": 1}, {"product_name": "Coke (330ml Can)", "quantity": 4}], "3h Standard room + fries & drinks"),
            ("Friends Bundle", "Medium", 3.0, "1400.00", True, [{"product_name": "Loaded Nachos", "quantity": 1}, {"product_name": "Iced Lemon Tea", "quantity": 1}], "3h Medium room + nachos & pitcher of iced tea"),
            ("Grand Feast", "Grand", 3.0, "2000.00", True, [{"product_name": "Sizzling Pork Sisig", "quantity": 2}, {"product_name": "Spaghetti Bolognese", "quantity": 1}, {"product_name": "Coke (330ml Can)", "quantity": 6}], "3h Grand room + feast meals & drinks"),
            ("VIP Celebration", "VIP", 4.0, "3000.00", True, [{"product_name": "Loaded Nachos", "quantity": 2}, {"product_name": "Carbonara Platter", "quantity": 1}, {"product_name": "Iced Lemon Tea", "quantity": 2}], "4h VIP room + party platters"),
            ("VVIP Party", "VVIP", 4.0, "4500.00", True, [{"product_name": "Loaded Nachos", "quantity": 2}, {"product_name": "Sizzling Pork Sisig", "quantity": 3}, {"product_name": "Carbonara Platter", "quantity": 2}], "4h VVIP room + complete banquet spread")
        ]

        seeded = []
        for name, category, dur, price, food, inc, desc in defaults:
            p = Package(
                package_id=generate_id("PKG"),
                name=name,
                category=category,
                duration_hours=dur,
                price=Decimal(price),
                includes_food=food,
                inclusions=inc,
                description=desc,
                is_active=True
            )
            seeded.append(p)

        JSONRepository.save_data(cls.FILENAME, [p.to_dict() for p in seeded])
        return seeded

    @classmethod
    def get_all(cls) -> list[Package]:
        data = JSONRepository.load_data(cls.FILENAME)
        if not data:
            return cls._seed_default_packages()
        return [Package.from_dict(item) for item in data]

    @classmethod
    def get_by_id(cls, package_id: str) -> Package | None:
        packages = cls.get_all()
        for p in packages:
            if p.package_id == package_id:
                return p
        return None

    @classmethod
    def save(cls, package: Package) -> bool:
        packages = cls.get_all()
        index = next((i for i, p in enumerate(packages) if p.package_id == package.package_id), -1)
        
        if index >= 0:
            packages[index] = package
        else:
            packages.append(package)
            
        return JSONRepository.save_data(cls.FILENAME, [p.to_dict() for p in packages])

    @classmethod
    def delete(cls, package_id: str) -> bool:
        packages = cls.get_all()
        updated = [p for p in packages if p.package_id != package_id]
        return JSONRepository.save_data(cls.FILENAME, [p.to_dict() for p in updated])