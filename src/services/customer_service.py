# src/services/customer_service.py
from decimal import Decimal
from src.repositories.customer_repository import CustomerRepository
from src.repositories.transaction_repository import TransactionRepository
from src.repositories.session_repository import SessionRepository
from src.models.customer import Customer
from src.utils.id_generator import generate_id
from src.services.activity_log_service import ActivityLogService
from src.core.state_manager import StateManager

class CustomerService:
    @staticmethod
    def get_all_customers() -> list[Customer]:
        return CustomerRepository.get_all()

    @staticmethod
    def create_customer(
        first_name: str, 
        last_name: str, 
        phone: str, 
        middle_name: str = "", 
        email: str = "", 
        address: str = "", 
        notes: str = "", 
        loyalty_points: int = 0
    ) -> tuple[Customer | None, str]:
        # Duplicate Phone Validation
        if CustomerRepository.get_by_phone(phone):
            return None, f"Contact number '{phone}' is already registered to another guest."

        customer_id = generate_id("CUST")
        customer = Customer(
            customer_id=customer_id,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            middle_name=middle_name,
            email=email,
            address=address,
            notes=notes,
            loyalty_points=loyalty_points
        )
        CustomerRepository.save(customer)
        
        user = StateManager.get("current_user", "Administrator")
        ActivityLogService.log_action(user, f"Registered new guest: {customer.full_name} ({phone})")
        return customer, "Guest registered successfully."

    @staticmethod
    def update_customer(customer: Customer) -> tuple[bool, str]:
        existing = CustomerRepository.get_by_phone(customer.phone)
        if existing and existing.customer_id != customer.customer_id:
            return False, f"Contact number '{customer.phone}' is already in use by another guest."

        success = CustomerRepository.save(customer)
        if success:
            user = StateManager.get("current_user", "Administrator")
            ActivityLogService.log_action(user, f"Updated profile for guest: {customer.full_name}")
            return True, "Guest details updated successfully."
        return False, "Failed to update guest details."

    @staticmethod
    def delete_customer(customer_id: str) -> bool:
        customer = CustomerRepository.get_by_id(customer_id)
        success = CustomerRepository.delete(customer_id)
        if success and customer:
            user = StateManager.get("current_user", "Administrator")
            ActivityLogService.log_action(user, f"Deleted guest record: {customer.full_name}")
        return success

    @staticmethod
    def get_customer_stats(customer_id: str) -> dict:
        """Calculate historical visit count and total spending using Decimal arithmetic."""
        sessions = SessionRepository.get_all()
        transactions = TransactionRepository.get_all()

        visit_count = sum(1 for s in sessions if s.customer_id == customer_id)
        total_spent = sum(
            Decimal(str(t.total_paid)) for t in transactions if t.customer_id == customer_id
        )

        return {
            "visit_count": visit_count,
            "total_spent": total_spent
        }