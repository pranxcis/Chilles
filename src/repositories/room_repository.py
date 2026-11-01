# src/repositories/room_repository.py
from src.repositories.json_repository import JSONRepository
from src.models.room import Room
from src.utils.id_generator import generate_id

class RoomRepository:
    FILENAME = "rooms.json"

    @classmethod
    def _seed_default_rooms(cls) -> list[Room]:
        """Generate the initial 25 rooms (5 rooms per category) as specified."""
        categories_config = [
            {"type": "Standard", "cap": "2-4", "rate": 250.0, "fac": ["TV", "Karaoke System", "2 Microphones", "Air Conditioning", "Seating"]},
            {"type": "Medium", "cap": "5-8", "rate": 350.0, "fac": ["TV", "Karaoke System", "4 Microphones", "Surround Speakers", "Air Conditioning", "Seating"]},
            {"type": "Grand", "cap": "9-12", "rate": 500.0, "fac": ["Large TV", "Professional Karaoke", "4 Microphones", "Premium Speakers", "Air Conditioning", "Lounge Seating"]},
            {"type": "VIP", "cap": "13-18", "rate": 700.0, "fac": ["Ultra HD Screen", "Premium Karaoke", "6 Microphones", "Stage Lighting", "Air Conditioning", "Private Restroom"]},
            {"type": "VVIP", "cap": "19-25", "rate": 1000.0, "fac": ["Theater Display", "Master Audio Suite", "6 Wireless Mics", "Lighting System", "Refrigerator", "Private Restroom"]}
        ]

        seeded_rooms = []
        room_counter = 1

        for cat in categories_config:
            for i in range(1, 6):
                name = f"{cat['type']} Room {i:02d}"
                # Extract max capacity value for integer storage
                max_cap = int(cat["cap"].split("-")[1])
                room = Room(
                    room_id=generate_id("RM"),
                    name=name,
                    room_type=cat["type"],
                    capacity=max_cap,
                    hourly_rate=cat["rate"],
                    status="Available",
                    description=f"Spacious {cat['type']} category room equipped for up to {cat['cap']} guests.",
                    facilities=cat["fac"]
                )
                seeded_rooms.append(room)
                room_counter += 1

        # Save default seed data
        JSONRepository.save_data(cls.FILENAME, [r.to_dict() for r in seeded_rooms])
        return seeded_rooms

    @classmethod
    def get_all(cls) -> list[Room]:
        data = JSONRepository.load_data(cls.FILENAME)
        if not data:
            return cls._seed_default_rooms()
        return [Room.from_dict(item) for item in data]

    @classmethod
    def get_by_id(cls, room_id: str) -> Room | None:
        rooms = cls.get_all()
        for r in rooms:
            if r.room_id == room_id:
                return r
        return None

    @classmethod
    def save(cls, room: Room) -> bool:
        rooms = cls.get_all()
        existing_index = next((i for i, r in enumerate(rooms) if r.room_id == room.room_id), -1)
        
        if existing_index >= 0:
            rooms[existing_index] = room
        else:
            rooms.append(room)
            
        return JSONRepository.save_data(cls.FILENAME, [r.to_dict() for r in rooms])

    @classmethod
    def delete(cls, room_id: str) -> bool:
        rooms = cls.get_all()
        # Enforce data integrity: Prevent archiving/deleting if occupied
        target = next((r for r in rooms if r.room_id == room_id), None)
        if target and target.status == "Occupied":
            return False  # Cannot delete/archive occupied rooms

        updated_rooms = [r for r in rooms if r.room_id != room_id]
        return JSONRepository.save_data(cls.FILENAME, [r.to_dict() for r in updated_rooms])