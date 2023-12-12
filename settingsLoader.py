import json

# Singleton Settings Loader
class SettingsLoader:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SettingsLoader, cls).__new__(cls)
            cls._instance.load_settings()
        return cls._instance
    
    def load_settings(self):
        try:
            with open("config.json", "r") as file:
                self.settings = json.load(file)
        except:
            print("Error loading settings file")
            self.settings = {}

    def get_setting(self, key):
        value = self.settings.get(key)
        if value is not None:
            try:
                if isinstance(value, str):
                    return value
                elif isinstance(value, int):
                    return int(value)
                elif isinstance(value, float):
                    return float(value)
                elif isinstance(value, bool):
                    return bool(value)
                elif isinstance(value, list):
                    return value
                else:
                    return value
            except ValueError:
                return value
        return None