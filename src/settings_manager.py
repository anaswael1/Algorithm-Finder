class SettingsManager:
    def __init__(self):
        self.contest_mode = False
        self.restrictions = {
            "exact_name_only": True,
            "hide_tags": True,
            "hide_complexity": True
        }

    def toggle_contest_mode(self, status):
        self.contest_mode = status