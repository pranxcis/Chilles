# src/utils/id_generator.py module
# src/utils/id_generator.py
import uuid
from datetime import datetime

def generate_id(prefix: str = "CH") -> str:
    """Generate a unique human-readable ID with timestamp and short UUID hash."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_suffix = uuid.uuid4().hex[:4].upper()
    return f"{prefix}-{timestamp}-{unique_suffix}"