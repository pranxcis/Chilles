# src/services/room_service.py
from src.repositories.room_repository import RoomRepository
from src.models.room import Room
from src.utils.id_generator import generate_id
from src.services.activity_log_service import ActivityLogService
from src.core.state_manager import StateManager

class RoomService:
    @staticmethod
    def get_all_rooms() -> list[Room]:
        return RoomRepository.get_all()

    @staticmethod
    def get_room_by_id(room_id: str) -> Room | None:
        return RoomRepository.get_by_id(room_id)

    @staticmethod
    def create_room(name: str, room_type: str, capacity: int, hourly_rate: float, status: str = "Available", description: str = "", facilities: list = None) -> Room:
        room_id = generate_id("RM")
        room = Room(
            room_id=room_id,
            name=name,
            room_type=room_type,
            capacity=capacity,
            hourly_rate=hourly_rate,
            status=status,
            description=description,
            facilities=facilities or []
        )
        RoomRepository.save(room)
        
        user = StateManager.get("current_user", "Administrator")
        ActivityLogService.log_action(user, f"Created new KTV room: {name} ({room_type})")
        return room

    @staticmethod
    def update_room(room: Room) -> bool:
        success = RoomRepository.save(room)
        if success:
            user = StateManager.get("current_user", "Administrator")
            ActivityLogService.log_action(user, f"Updated room details for: {room.name}")
        return success

    @staticmethod
    def update_room_status(room_id: str, status: str) -> bool:
        room = RoomRepository.get_by_id(room_id)
        if room:
            room.status = status
            success = RoomRepository.save(room)
            if success:
                user = StateManager.get("current_user", "Administrator")
                ActivityLogService.log_action(user, f"Changed status of {room.name} to {status}")
            return success
        return False

    @staticmethod
    def delete_room(room_id: str) -> tuple[bool, str]:
        room = RoomRepository.get_by_id(room_id)
        if not room:
            return False, "Room not found."
        
        if room.status == "Occupied":
            return False, "Cannot delete or archive an occupied room!"

        success = RoomRepository.delete(room_id)
        if success:
            user = StateManager.get("current_user", "Administrator")
            ActivityLogService.log_action(user, f"Archived/Deleted room: {room.name}")
            return True, "Room deleted successfully."
        return False, "Failed to delete room."