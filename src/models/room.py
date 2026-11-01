# src/models/room.py
from datetime import datetime

class Room:
    """Model representing a KTV room with complete category, pricing, and facility attributes."""
    def __init__(self, room_id: str, name: str, room_type: str, capacity: int, hourly_rate: float, status: str = "Available", description: str = "", facilities: list = None, created_at: str = None):
        self.room_id = room_id
        self.name = name
        self.room_type = room_type          # "Standard", "Medium", "Grand", "VIP", "VVIP"
        self.capacity = int(capacity)
        self.hourly_rate = float(hourly_rate)
        self.status = status                # "Available", "Occupied", "Maintenance"
        self.description = description
        self.facilities = facilities or []
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> dict:
        return {
            "room_id": self.room_id,
            "name": self.name,
            "room_type": self.room_type,
            "capacity": self.capacity,
            "hourly_rate": self.hourly_rate,
            "status": self.status,
            "description": self.description,
            "facilities": self.facilities,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            room_id=data.get("room_id"),
            name=data.get("name"),
            room_type=data.get("room_type", "Standard"),
            capacity=data.get("capacity", 4),
            hourly_rate=data.get("hourly_rate", 250.0),
            status=data.get("status", "Available"),
            description=data.get("description", ""),
            facilities=data.get("facilities", []),
            created_at=data.get("created_at")
        )