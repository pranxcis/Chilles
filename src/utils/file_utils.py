# src/utils/file_utils.py
import os

def ensure_directories_exist(*dirs):
    """Ensure that all provided directory paths exist on disk, creating them if necessary."""
    for d in dirs:
        if d and not os.path.exists(d):
            os.makedirs(d, exist_ok=True)