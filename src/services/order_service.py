# src/services/order_service.py
from datetime import datetime
from decimal import Decimal
from src.repositories.order_repository import OrderRepository
from src.repositories.session_repository import SessionRepository
from src.repositories.transaction_repository import TransactionRepository
from src.repositories.room_repository import RoomRepository
from src.models.order import Order
from src.models.transaction import Transaction
from src.utils.id_generator import generate_id
from src.services.activity_log_service import ActivityLogService
from src.services.receipt_service import ReceiptService
from src.core.state_manager import StateManager

class OrderService:
    @staticmethod
    def get_all_orders() -> list[Order]:
        return OrderRepository.get_all()

    @staticmethod
    def place_cart_order(session_id: str, cart_items: list[dict], payment_mode: str = "Tab") -> tuple[Order | None, str, str | None]:
        """
        Process bulk order:
        - payment_mode: "Tab" (appended to room session tab) or "Upfront" (paid immediately, logs transaction & generates receipt)
        Returns: (order_obj, message, receipt_text)
        """
        session = SessionRepository.get_by_id(session_id)
        if not session or session.status not in ("Active", "Extended"):
            return None, "Target room session is not active.", None

        if not cart_items:
            return None, "Cart is empty.", None

        payment_status = "Paid" if payment_mode == "Upfront" else "Unpaid"
        order_id = generate_id("ORD")
        
        order = Order(
            order_id=order_id,
            session_id=session.session_id,
            customer_id=session.customer_id,
            items=cart_items,
            status="Pending",
            payment_mode=payment_mode,
            payment_status=payment_status
        )
        order.compute_total()
        OrderRepository.save(order)

        receipt_text = None

        if payment_mode == "Tab":
            # Append to session tab
            for item in cart_items:
                session.orders.append(item)
            session.compute_totals()
            SessionRepository.save(session)
        else:
            # Immediate Upfront Payment: Log transaction and generate receipt
            txn = Transaction(
                transaction_id=generate_id("TXN"),
                session_id=session.session_id,
                customer_id=session.customer_id,
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                rental_amount=0.0,
                food_amount=float(order.total_amount),
                discount_amount=0.0,
                total_paid=float(order.total_amount),
                payment_method="Cash"
            )
            TransactionRepository.save(txn)

            room = RoomRepository.get_by_id(session.room_id)
            receipt_text = ReceiptService.generate_receipt(txn, session, room)

        user = StateManager.get("current_user", "Administrator")
        ActivityLogService.log_action(user, f"Placed bulk order {order_id} ({payment_mode}) for session {session_id}")
        return order, "Order placed successfully.", receipt_text