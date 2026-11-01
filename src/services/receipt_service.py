# src/services/receipt_service.py
import os

class ReceiptService:
    RECEIPTS_DIR = "receipts"

    @classmethod
    def _ensure_receipts_dir(cls):
        """Ensures the receipts directory exists before saving receipt files."""
        if not os.path.exists(cls.RECEIPTS_DIR):
            os.makedirs(cls.RECEIPTS_DIR, exist_ok=True)

    @staticmethod
    def generate_receipt(transaction, session, room) -> str:
        """Formats, logs, and saves a professional text receipt into the receipts folder."""
        ReceiptService._ensure_receipts_dir()

        receipt_text = f"""
========================================
           CHILLES KTV SYSTEM          
         OFFICIAL SALES RECEIPT        
========================================
Txn ID      : {transaction.transaction_id}
Date        : {transaction.timestamp}
Room        : {room.name} ({room.room_type})
Session ID  : {session.session_id}
----------------------------------------
Rental Amount   : ₱{float(transaction.rental_amount):.2f}
F&B Tab         : ₱{float(transaction.food_amount):.2f}
Overtime Fee    : ₱{float(transaction.overtime_amount):.2f}
Discount        : -₱{float(transaction.discount_amount):.2f}
----------------------------------------
TOTAL PAID      : ₱{float(transaction.total_paid):.2f}
Payment Method  : {transaction.payment_method}
========================================
         THANK YOU FOR SINGING!         
========================================
        """

        file_path = os.path.join(ReceiptService.RECEIPTS_DIR, f"receipt_{transaction.transaction_id}.txt")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(receipt_text.strip())
        except Exception:
            pass

        return receipt_text.strip()