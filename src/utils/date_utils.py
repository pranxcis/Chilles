# src/utils/date_utils.py module
# src/utils/date_utils.py
from datetime import datetime

def get_current_timestamp() -> str:
    """Return standard ISO-like timestamp string for database records."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def format_date_readable(date_str: str) -> str:
    """Convert a standard date string into a user-friendly readable format."""
    try:
        dt = datetime.strptime(date_str.split(".")[0], "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%b %d, %Y - %I:%M %p")
    except (TypeError, ValueError):
        return date_str