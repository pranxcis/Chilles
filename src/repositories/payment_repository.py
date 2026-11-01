# src/repositories/payment_repository.py
from src.repositories.json_repository import JSONRepository
from src.models.payment import Payment

class PaymentRepository:
    FILENAME = "payments.json"

    @classmethod
    def get_all(cls) -> list[Payment]:
        data = JSONRepository.load_data(cls.FILENAME)
        return [Payment.from_dict(item) for item in data]

    @classmethod
    def save(cls, payment: Payment) -> bool:
        payments = cls.get_all()
        payments.append(payment)
        return JSONRepository.save_data(cls.FILENAME, [p.to_dict() for p in payments])