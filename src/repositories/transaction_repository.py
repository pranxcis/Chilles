from src.repositories.json_repository import JSONRepository
from src.models.transaction import Transaction

class TransactionRepository:
    FILENAME = "transactions.json"

    @classmethod
    def get_all(cls) -> list[Transaction]:
        data = JSONRepository.load_data(cls.FILENAME)
        return [Transaction.from_dict(item) for item in data]

    @classmethod
    def save(cls, transaction: Transaction) -> bool:
        transactions = cls.get_all()
        transactions.append(transaction)
        return JSONRepository.save_data(cls.FILENAME, [t.to_dict() for t in transactions])