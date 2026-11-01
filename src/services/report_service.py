# src/services/report_service.py module
from src.repositories.transaction_repository import TransactionRepository

class ReportService:
    @staticmethod
    def get_sales_summary() -> dict:
        txns = TransactionRepository.get_all()
        total_revenue = sum(t.total_paid for t in txns)
        total_transactions = len(txns)

        return {
            "total_revenue": total_revenue,
            "total_transactions": total_transactions
        }