# src/config/app_config.py module

class AppConfig:
    @staticmethod
    def get_business_info() -> dict:
        return {
            "business_name": "Chilles",
            "branch": "Main Branch",
            "currency": "₱"
        }