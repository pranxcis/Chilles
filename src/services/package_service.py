# src/services/package_service.py
from decimal import Decimal
from src.repositories.package_repository import PackageRepository
from src.models.package import Package
from src.utils.id_generator import generate_id
from src.services.activity_log_service import ActivityLogService
from src.core.state_manager import StateManager

class PackageService:
    @staticmethod
    def get_all_packages() -> list[Package]:
        return PackageRepository.get_all()

    @staticmethod
    def create_package(
        name: str,
        category: str,
        duration_hours: float,
        price: float | str | Decimal,
        includes_food: bool = False,
        inclusions: list = None,
        description: str = ""
    ) -> Package:
        package_id = generate_id("PKG")
        package = Package(
            package_id=package_id,
            name=name,
            category=category,
            duration_hours=duration_hours,
            price=Decimal(str(price)),
            includes_food=includes_food,
            inclusions=inclusions or [],
            description=description,
            is_active=True
        )
        PackageRepository.save(package)
        
        user = StateManager.get("current_user", "Administrator")
        ActivityLogService.log_action(user, f"Created promotional package: {name} ({category})")
        return package

    @staticmethod
    def update_package(package: Package) -> bool:
        success = PackageRepository.save(package)
        if success:
            user = StateManager.get("current_user", "Administrator")
            ActivityLogService.log_action(user, f"Updated promo package: {package.name}")
        return success

    @staticmethod
    def toggle_active(package_id: str) -> bool:
        pkg = PackageRepository.get_by_id(package_id)
        if pkg:
            pkg.is_active = not pkg.is_active
            success = PackageRepository.save(pkg)
            if success:
                user = StateManager.get("current_user", "Administrator")
                status_str = "Active" if pkg.is_active else "Inactive"
                ActivityLogService.log_action(user, f"Set package {pkg.name} status to {status_str}")
            return success
        return False

    @staticmethod
    def delete_package(package_id: str) -> bool:
        pkg = PackageRepository.get_by_id(package_id)
        success = PackageRepository.delete(package_id)
        if success and pkg:
            user = StateManager.get("current_user", "Administrator")
            ActivityLogService.log_action(user, f"Deleted promo package: {pkg.name}")
        return success