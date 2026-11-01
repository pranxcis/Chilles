# src/core/state_manager.py module
# src/core/state_manager.py

class StateManager:
    """Singleton-style centralized state manager for cross-module app data."""
    _state = {
        "current_user": "Administrator",
        "active_session": None,
        "selected_room": None,
        "active_filters": {}
    }

    @classmethod
    def get(cls, key: str, default=None):
        return cls._state.get(key, default)

    @classmethod
    def set(cls, key: str, value):
        cls._state[key] = value

    @classmethod
    def update(cls, data: dict):
        cls._state.update(data)

    @classmethod
    def clear(cls):
        cls._state = {
            "current_user": "Administrator",
            "active_session": None,
            "selected_room": None,
            "active_filters": {}
        }