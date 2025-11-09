"""
Módulo para la vista de Configuración.
"""
import customtkinter as ctk
from tkinter import messagebox

class SettingsView(ctk.CTkFrame):
    """Clase para la vista de configuración."""

    def __init__(self, master, main_window, config_service, task_service, export_service):
        super().__init__(master, fg_color="transparent")
        self.main_window = main_window
        self.config_service = config_service
        self.task_service = task_service
        self.export_service = export_service

        # Mapeo para la vista de inicio
        self.start_view_map = {
            "Dashboard": "dashboard",
            "Tareas": "tasks",
            "Estadisticas": "stats"
        }
        self.start_view_map_rev = {v: k for k, v in self.start_view_map.items()}

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Crea los widgets de la vista de configuración."""
        ctk.CTkLabel(self, text="Configuración", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20, anchor="w")

        # --- Apariencia ---
        ctk.CTkLabel(self, text="Apariencia", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5), anchor="w")
        
        # Tema (Claro/Oscuro)
        appearance_frame = ctk.CTkFrame(self, fg_color="transparent")
        appearance_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(appearance_frame, text="Tema:").pack(side="left")
        appearance_mode_var = ctk.StringVar(value=self.config_service.get("appearance_mode"))
        ctk.CTkOptionMenu(appearance_frame, values=["Dark", "Light"], variable=appearance_mode_var, command=self._change_appearance_mode).pack(side="left", padx=10)

        # Color de Acento
        color_theme_var = ctk.StringVar(value=self.config_service.get("color_theme"))
        ctk.CTkLabel(appearance_frame, text="Color de acento:").pack(side="left")
        ctk.CTkOptionMenu(appearance_frame, values=["blue", "dark-blue", "green"], variable=color_theme_var, command=self._change_color_theme).pack(side="left", padx=10)
        ctk.CTkLabel(appearance_frame, text="*requiere reinicio", font=ctk.CTkFont(size=10, slant="italic")).pack(side="left", padx=5)

        # --- Comportamiento ---
        ctk.CTkLabel(self, text="Comportamiento", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 5), anchor="w")
        
        behavior_frame = ctk.CTkFrame(self, fg_color="transparent")
        behavior_frame.pack(fill="x", pady=5)
        # Vista de Inicio
        current_display_view = self.start_view_map_rev.get(self.config_service.get("start_view"), "Dashboard")
        start_view_var = ctk.StringVar(value=current_display_view)
        ctk.CTkLabel(behavior_frame, text="Vista de inicio:").pack(side="left")
        ctk.CTkOptionMenu(behavior_frame, values=list(self.start_view_map.keys()), variable=start_view_var, command=self._set_start_view).pack(side="left", padx=10)

        # Tareas por página
        tasks_per_page_var = ctk.StringVar(value=str(self.config_service.get("tasks_per_page")))
        ctk.CTkLabel(behavior_frame, text="Tareas por página:").pack(side="left")
        ctk.CTkOptionMenu(behavior_frame, values=["5", "8", "10", "15"], variable=tasks_per_page_var, command=self._set_tasks_per_page).pack(side="left", padx=10)

        # --- Gestión de datos ---
        ctk.CTkLabel(self, text="Gestión de datos", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 5), anchor="w")
        
        data_frame = ctk.CTkFrame(self, fg_color="transparent")
        data_frame.pack(fill="x", pady=5)
        ctk.CTkButton(data_frame, text="Eliminar todas las tareas", command=self._delete_all_tasks, fg_color="#e74c3c", hover_color="#c0392b").pack(side="left", padx=5)

        # Botón para guardar cambios
        ctk.CTkButton(self, text="Guardar cambios", command=self._save_config).pack(pady=(40, 20), anchor="w")

        # --- Acerca de ---
        ctk.CTkLabel(self, text="Acerca de", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 5), anchor="w")
        about_frame = ctk.CTkFrame(self, fg_color="transparent")
        about_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(about_frame, text="Gestor de Tareas v1.0").pack(anchor="w")
        ctk.CTkLabel(about_frame, text="Creado por Ezequiel Selis y Rocio Diaz para Ingeniería de Software IFTS 24.").pack(anchor="w")

    def _change_appearance_mode(self, mode: str):
        ctk.set_appearance_mode(mode.lower())
        self.config_service.set("appearance_mode", mode)

    def _change_color_theme(self, color: str):
        ctk.set_default_color_theme(color)
        self.config_service.set("color_theme", color)
        messagebox.showinfo("Reinicio Necesario", "El cambio de color de acento requiere reiniciar la aplicación para verse completamente.", parent=self)

    def _set_start_view(self, display_name: str):
        internal_name = self.start_view_map.get(display_name, "dashboard")
        self.config_service.set("start_view", internal_name)

    def _set_tasks_per_page(self, num: str):
        self.config_service.set("tasks_per_page", int(num))


    def _delete_all_tasks(self):
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres eliminar todas las tareas? Esta acción no se puede deshacer.", icon="warning", parent=self):
            self.task_service.delete_all_tasks()
            self.main_window._refresh_tasks_view()
            messagebox.showinfo("Completado", "Todas las tareas han sido eliminadas.", parent=self)

    def _save_config(self):
        self.config_service.save_config()
        messagebox.showinfo("Guardado", "La configuración ha sido guardada.", parent=self)
