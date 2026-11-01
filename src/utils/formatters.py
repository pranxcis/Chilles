# src/utils/formatters.py

def format_currency(amount: float) -> str:
    """Format numeric value into Philippine Peso standard format."""
    try:
        return f"₱ {float(amount):,.2f}"
    except (TypeError, ValueError):
        return "₱ 0.00"

def format_duration(minutes: int) -> str:
    """Convert minutes into clean hours and minutes breakdown."""
    try:
        total_mins = int(minutes)
        hours = total_mins // 60
        mins = total_mins % 60
        if hours > 0:
            return f"{hours}h {mins}m"
        return f"{mins}m"
    except (TypeError, ValueError):
        return "0m"

def capitalize_words(text: str) -> str:
    """Capitalize words for clean names or labels."""
    if not text:
        return ""
    return " ".join([word.capitalize() for word in text.split()])