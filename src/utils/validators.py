# src/utils/validators.py module
# src/utils/validators.py
import re

def is_valid_phone(phone: str) -> bool:
    """Validate Philippine mobile number formats (e.g., 09XXXXXXXXX or +639XXXXXXXXX)."""
    pattern = r"^(09|\+639)\d{9}$"
    return bool(re.match(pattern, phone))

def is_valid_email(email: str) -> bool:
    """Basic email pattern validation check."""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email))

def is_non_empty_string(value: str) -> bool:
    """Check if string is not empty or just whitespace."""
    return bool(value and value.strip())

def is_valid_positive_number(value) -> bool:
    """Verify if value can be parsed as a positive number/float."""
    try:
        num = float(value)
        return num >= 0
    except (TypeError, ValueError):
        return False