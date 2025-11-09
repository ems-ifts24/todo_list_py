"""
Módulo para la vista de Estadísticas.
"""
import customtkinter as ctk

class StatsView(ctk.CTkFrame):
    """Clase para la vista de estadísticas."""

    def __init__(self, master, task_service, main_window):
        super().__init__(master, fg_color="transparent")
        self.task_service = task_service
        self.main_window = main_window

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Crea los widgets de la vista de estadísticas."""
        label = ctk.CTkLabel(
            self,
            text="Estadísticas",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        label.pack(pady=20)

        # Mensaje provisional
        ctk.CTkLabel(
            self,
            text="Vista de estadísticas en desarrollo...",
            font=ctk.CTkFont(size=14)
        ).pack(pady=10)
