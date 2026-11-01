# src/services/session_service.py
from datetime import datetime, timedelta
from decimal import Decimal
from src.repositories.session_repository import SessionRepository
from src.repositories.room_repository import RoomRepository
from src.repositories.transaction_repository import TransactionRepository
from src.models.session import RoomSession
from src.models.transaction import Transaction
from src.utils.id_generator import generate_id
from src.services.activity_log_service import ActivityLogService
from src.services.package_service import PackageService
from src.services.billing_service import BillingService
from src.services.payment_service import PaymentService
from src.services.receipt_service import ReceiptService
from src.core.state_manager import StateManager

class SessionService:
    @staticmethod
    def get_active_sessions() -> list[RoomSession]:
        return [s for s in SessionRepository.get_all() if s.status in ("Active", "Extended")]

    @staticmethod
    def start_session(room_id: str, customer_id: str, duration_hours: float, hourly_rate: float, package_id: str = "") -> tuple[RoomSession | None, str]:
        room = RoomRepository.get_by_id(room_id)
        if not room or room.status == "Occupied":
            return None, "Room is unavailable or already occupied."

        now = datetime.now()
        end_time = now + timedelta(hours=float(duration_hours))

        # Check package application via PackageService if provided
        effective_rate = hourly_rate
        if package_id:
            pkg = PackageService.get_package_by_id(package_id)
            if pkg:
                # If package has a fixed price or promotional rate adjustment
                effective_rate = float(pkg.price) / duration_hours if duration_hours > 0 else hourly_rate

        session_id = generate_id("SES")
        session = RoomSession(
            session_id=session_id,
            room_id=room_id,
            customer_id=customer_id,
            start_time=now.strftime("%Y-%m-%d %H:%M:%S"),
            duration_hours=duration_hours,
            end_time=end_time.strftime("%Y-%m-%d %H:%M:%S"),
            hourly_rate=effective_rate,
            package_id=package_id,
            status="Active"
        )
        session.compute_totals()
        SessionRepository.save(session)

        room.status = "Occupied"
        RoomRepository.save(room)

        user = StateManager.get("current_user", "Administrator")
        ActivityLogService.log_action(user, f"Launched session {session_id} for room {room.name}")
        return session, "Room session launched successfully."

    @staticmethod
    def calculate_live_status(session: RoomSession) -> dict:
        """Delegates real-time overtime and billing calculations to BillingService."""
        return BillingService.calculate_session_status(session)

    @staticmethod
    def extend_session(session_id: str, additional_hours: float) -> tuple[bool, str]:
        session = SessionRepository.get_by_id(session_id)
        if not session:
            return False, "Session not found."

        try:
            current_end = datetime.strptime(session.end_time, "%Y-%m-%d %H:%M:%S")
        except Exception:
            current_end = datetime.now()

        new_end = current_end + timedelta(hours=float(additional_hours))
        session.duration_hours += float(additional_hours)
        session.end_time = new_end.strftime("%Y-%m-%d %H:%M:%S")
        session.status = "Extended"
        session.compute_totals()
        SessionRepository.save(session)

        user = StateManager.get("current_user", "Administrator")
        ActivityLogService.log_action(user, f"Extended session {session_id} by {additional_hours} hrs")
        return True, "Session extended successfully."

    @staticmethod
    def transfer_room(session_id: str, new_room_id: str) -> tuple[bool, str]:
        session = SessionRepository.get_by_id(session_id)
        if not session:
            return False, "Session not found."

        new_room = RoomRepository.get_by_id(new_room_id)
        if not new_room or new_room.status != "Available":
            return False, "Target room is not available."

        old_room = RoomRepository.get_by_id(session.room_id)
        if old_room:
            old_room.status = "Available"
            RoomRepository.save(old_room)

        new_room.status = "Occupied"
        RoomRepository.save(new_room)

        session.room_id = new_room_id
        session.hourly_rate = float(new_room.hourly_rate)
        session.compute_totals()
        SessionRepository.save(session)

        user = StateManager.get("current_user", "Administrator")
        ActivityLogService.log_action(user, f"Transferred session {session_id} to room {new_room.name}")
        return True, f"Session transferred to {new_room.name} successfully."

    @staticmethod
    def complete_session_checkout(session_id: str, payment_method: str = "Cash", discount_amount: float = 0.0) -> tuple[bool, str]:
        """
        Executes full bill-out sequence:
        1. Calculates final totals via BillingService.
        2. Records payment via PaymentService.
        3. Frees room & saves session.
        4. Generates receipt via ReceiptService.
        """
        session = SessionRepository.get_by_id(session_id)
        if not session or session.status not in ("Active", "Extended"):
            return False, "Active session not found."

        # 1. Compute final bill breakdown via BillingService
        bill_summary = BillingService.generate_final_bill(session, discount_amount)
        
        session.overtime_minutes = bill_summary["overtime_minutes"]
        session.overtime_amount = bill_summary["overtime_fee"]
        session.status = "Completed"
        session.compute_totals()
        SessionRepository.save(session)

        # 2. Free up room
        room = RoomRepository.get_by_id(session.room_id)
        if room:
            room.status = "Available"
            RoomRepository.save(room)

        # 3. Process payment through PaymentService & TransactionRepository
        net_payable = bill_summary["net_payable"]
        PaymentService.process_payment(session.session_id, net_payable, payment_method)

        txn = Transaction(
            transaction_id=generate_id("TXN"),
            session_id=session.session_id,
            customer_id=session.customer_id,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            rental_amount=float(session.rental_amount),
            food_amount=float(session.food_amount),
            overtime_amount=float(session.overtime_amount),
            discount_amount=float(discount_amount),
            total_paid=float(net_payable),
            payment_method=payment_method
        )
        TransactionRepository.save(txn)

        # 4. Generate receipt via ReceiptService
        ReceiptService.generate_receipt(txn, session, room)

        user = StateManager.get("current_user", "Administrator")
        ActivityLogService.log_action(user, f"Completed checkout & bill-out for session {session_id} (Paid: {net_payable})")
        return True, "Session checked out, paid, and receipt generated successfully."