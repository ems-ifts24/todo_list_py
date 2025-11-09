"""
Módulo para la vista de Configuración.
"""
import customtkinter as ctk

class SettingsView(ctk.CTkFrame):
    """Clase para la vista de configuración."""

    def __init__(self, master, main_window):
        super().__init__(master, fg_color="transparent")
        self.main_window = main_window

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Crea los widgets de la vista de configuración."""
        label = ctk.CTkLabel(
            self,
            text="Configuración",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        label.pack(pady=20)

        # Selector de tema
        theme_frame = ctk.CTkFrame(self, fg_color="transparent")
        theme_frame.pack(pady=10)

        ctk.CTkLabel(
            theme_frame,
            text="Tema:",
            font=ctk.CTkFont(weight="bold")
        ).pack(side="left", padx=(0, 10))

        theme_var = ctk.StringVar(value=ctk.get_appearance_mode().capitalize())
        theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            values=["Oscuro", "Claro"],
            variable=theme_var,
            command=self.main_window._change_theme,
            fg_color=("gray70", "gray30"),
            button_color=("gray60", "gray40"),
            button_hover_color=("gray50", "gray50")
        )
        theme_menu.pack(side="left")
