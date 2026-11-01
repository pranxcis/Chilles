# src/services/activity_log_service.py module
from src.repositories.json_repository import JSONRepository
from src.utils.date_utils import get_current_timestamp

class ActivityLogService:
    FILENAME = "activity_logs.json"

    @staticmethod
    def log_action(user: str, action: str):
        """Append a structured log entry to activity_logs.json."""
        logs = JSONRepository.load_data(ActivityLogService.FILENAME)
        if not isinstance(logs, list):
            logs = []
        
        timestamp = get_current_timestamp()
        log_entry = {
            "timestamp": timestamp,
            "user": user,
            "action": action
        }
        logs.append(log_entry)
        JSONRepository.save_data(ActivityLogService.FILENAME, logs)

    @staticmethod
    def get_all_logs() -> list[dict]:
        """Retrieve all activity log records."""
        logs = JSONRepository.load_data(ActivityLogService.FILENAME)
        return logs if isinstance(logs, list) else []

    @staticmethod
    def get_formatted_logs() -> list[str]:
        """Retrieve logs formatted as readable strings for UI display."""
        logs = ActivityLogService.get_all_logs()
        return [f"[{l.get('timestamp', '')}] {l.get('user', 'System')}: {l.get('action', '')}" for l in logs]