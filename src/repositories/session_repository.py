# src/repositories/session_repository.py
from src.repositories.json_repository import JSONRepository
from src.models.session import RoomSession

class SessionRepository:
    FILENAME = "room_sessions.json"

    @classmethod
    def get_all(cls) -> list[RoomSession]:
        data = JSONRepository.load_data(cls.FILENAME)
        return [RoomSession.from_dict(item) for item in data]

    @classmethod
    def get_by_id(cls, session_id: str) -> RoomSession | None:
        sessions = cls.get_all()
        for s in sessions:
            if s.session_id == session_id:
                return s
        return None

    @classmethod
    def get_active_by_room(cls, room_id: str) -> RoomSession | None:
        sessions = cls.get_all()
        for s in sessions:
            if s.room_id == room_id and s.status in ("Active", "Extended"):
                return s
        return None

    @classmethod
    def save(cls, session: RoomSession) -> bool:
        sessions = cls.get_all()
        index = next((i for i, s in enumerate(sessions) if s.session_id == session.session_id), -1)
        
        session.compute_totals()
        if index >= 0:
            sessions[index] = session
        else:
            sessions.append(session)
            
        return JSONRepository.save_data(cls.FILENAME, [s.to_dict() for s in sessions])

    @classmethod
    def delete(cls, session_id: str) -> bool:
        sessions = cls.get_all()
        updated = [s for s in sessions if s.session_id != session_id]
        return JSONRepository.save_data(cls.FILENAME, [s.to_dict() for s in updated])