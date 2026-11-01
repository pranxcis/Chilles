# src/core/navigation.py module
# src/core/navigation.py

class NavigationManager:
    """Handles view routing history, stack management, and active navigation state."""
    def __init__(self, on_view_change=None):
        self.on_view_change = on_view_change
        self.history = []
        self.current_view = None

    def navigate_to(self, view_name: str, push_history: bool = True):
        if not view_name or view_name == self.current_view:
            return

        if self.current_view and push_history:
            self.history.append(self.current_view)

        self.current_view = view_name
        if self.on_view_change:
            self.on_view_change(view_name)

    def go_back(self):
        if self.history:
            previous_view = self.history.pop()
            self.current_view = previous_view
            if self.on_view_change:
                self.on_view_change(previous_view, is_back=True)
            return previous_view
        return None

    def clear_history(self):
        self.history.clear()