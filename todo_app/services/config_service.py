"""
Módulo para gestionar la configuración de la aplicación.
"""
import json
import os

class ConfigService:
    """Servicio para cargar y guardar la configuración de la aplicación."""
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self._load_defaults()
        self._load_config()

    def _load_defaults(self) -> dict:
        """Carga la configuración por defecto."""
        return {
            "appearance_mode": "Dark",
            "color_theme": "blue",
            "start_view": "dashboard",
            "tasks_per_page": 8
        }

    def _load_config(self) -> None:
        """Carga la configuración desde el archivo JSON."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    self.config.update(user_config)
            except (json.JSONDecodeError, IOError):
                # Si hay un error, se usan los valores por defecto
                pass

    def get(self, key: str):
        """Obtiene un valor de la configuración."""
        return self.config.get(key)

    def set(self, key: str, value) -> None:
        """Establece un valor en la configuración y lo guarda."""
        self.config[key] = value
        self.save_config()

    def save_config(self) -> None:
        """Guarda la configuración actual en el archivo JSON."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
        except IOError as e:
            print(f"Error al guardar la configuración: {e}")
