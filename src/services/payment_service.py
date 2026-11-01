# src/services/payment_service.py
from src.models.payment import Payment
from src.repositories.payment_repository import PaymentRepository
from src.utils.id_generator import generate_id

class PaymentService:
    @staticmethod
    def process_payment(session_id: str, amount, method: str = "Cash") -> Payment:
        payment = Payment(
            payment_id=generate_id("PAY"),
            session_id=session_id,
            amount=amount,
            method=method
        )
        PaymentRepository.save(payment)
        return payment