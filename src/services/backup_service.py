# src/services/backup_service.py module
import shutil
import os
from src.config.constants import DATA_DIR, BACKUP_DIR
from src.utils.file_utils import ensure_directories_exist
from datetime import datetime

class BackupService:
    @staticmethod
    def create_backup() -> str:
        ensure_directories_exist(BACKUP_DIR)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"backup_{timestamp}")
        
        if os.path.exists(DATA_DIR):
            shutil.copytree(DATA_DIR, backup_path)
            return backup_path
        return ""