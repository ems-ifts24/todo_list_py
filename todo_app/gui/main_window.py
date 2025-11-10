"""
Ventana principal de la aplicación de tareas.
"""
import customtkinter as ctk
from typing import Optional
from .simulation_view import SimulationView

from ..models.task import Task, Status
from ..services.task_service import TaskService
from ..services.config_service import ConfigService
from .tasks_view import TasksView
from .dashboard_view import DashboardView
from .stats_view import StatsView
from .settings_view import SettingsView
from .task_dialog import TaskDialog

class MainWindow(ctk.CTk):
    """Clase principal de la ventana de la aplicación."""
    
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana
        self.title("Gestor de Tareas")
        self.minsize(800, 600)    # Tamaño mínimo permitido
        
        # Tamaño deseado de la ventana
        self.width = 1100
        self.height = 600
        
        # Mostrar dimensiones al redimensionar
        self.bind("<Configure>", self._on_window_resize)
        
        # Configurar geometría inicial con el tamaño correcto
        # La posición se establecerá en _center_window
        self.geometry(f"{self.width}x{self.height}+0+0")
        
        # Centrar la ventana después de que esté completamente creada
        self.after(100, self._center_window)

        # Configurar el grid principal
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Inicializar servicios
        self.config_service = ConfigService()
        self.task_service = TaskService()

        # Aplicar configuración inicial
        self._apply_initial_config()
        
        # Inicializar servicio de exportación (importación diferida para evitar dependencia circular)
        from ..services.export_service import ExportService
        self.export_service = ExportService()
        
        # Inicializar variables de estado
        self.current_view = self.config_service.get("start_view")
        self.nav_buttons = {}
        self.views = {}  # Cache para las vistas
        
        
        # Crear la interfaz
        self._create_sidebar()
        self._create_main_content()
        
        # Configurar estilos (después de crear los widgets)
        self._setup_styles()
        
        # Carga inicial de datos
        self._initial_load()
    
    def _initial_load(self):
        """Realiza la carga inicial de tareas y luego muestra la vista principal."""
        # Muestra un indicador de carga mientras se obtienen los datos
        loading_label = ctk.CTkLabel(self.main_content, text="Cargando datos...", font=ctk.CTkFont(size=18))
        loading_label.pack(pady=50)

        def on_tasks_loaded(tasks):
            # Esta función se ejecuta cuando las tareas han sido cargadas
            loading_label.destroy()
            self.display_view(self.current_view)

        # Inicia la carga asíncrona de tareas
        self.task_service.load_tasks_async(on_tasks_loaded)

    def _center_window(self):
        """Centra la ventana en la pantalla."""
        # Asegurar que la ventana tenga el tamaño correcto
        self.geometry(f"{self.width}x{self.height}")
        
        # Actualizar la ventana para asegurar que los cálculos sean precisos
        self.update_idletasks()
        
        # Obtener dimensiones de la pantalla
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calcular posición x, y para centrar la ventana
        x = (screen_width // 2) - (self.width // 2)
        y = max(30, (screen_height // 2) - (self.height // 2))  # Mínimo 30 píxeles desde el borde superior
        
        # Aplicar la posición centrada
        self.geometry(f"{self.width}x{self.height}+{x}+{y}")
        self.minsize(800, 600)  # Asegurar tamaño mínimo
        
    def _on_window_resize(self, event):
        """Muestra las dimensiones actuales de la ventana en la barra de título."""
        # Comentado temporalmente para ocultar la resolución
        # if self.winfo_toplevel() == self:  # Solo si es la ventana principal
        #     width = self.winfo_width()
        #     height = self.winfo_height()
        #     self.title(f"Gestor de Tareas - {width}x{height}")
    
    def _setup_window_resize_handler(self, window, base_title):
        """Configura el manejador de redimensionamiento para una ventana."""
        # Comentado temporalmente para ocultar la resolución
        # def on_resize(event):
        #     width = window.winfo_width()
        #     height = window.winfo_height()
        #     window.title(f"{base_title} - {width}x{height}")
        # 
        # window.bind("<Configure>", on_resize)
        # # Actualizar título con tamaño inicial
        # window.update_idletasks()
        # window.title(f"{base_title} - {window.winfo_width()}x{window.winfo_height()}")
        window.title(base_title)  # Solo mostramos el título base
    
    def _confirm_delete_task(self, task: Task) -> None:
        """Muestra un diálogo de confirmación para eliminar una tarea."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirmar Eliminación")
        dialog.resizable(True, True)  # Hacer redimensionable
        dialog.minsize(450, 200)  # Tamaño mínimo
        dialog.geometry("550x220")  # Tamaño inicial
        self._setup_window_resize_handler(dialog, "Confirmar Eliminación")
        dialog.grab_set()  # Hace que el diálogo sea modal
        
        # Centrar el diálogo en la pantalla
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Contenido del diálogo
        ctk.CTkLabel(
            dialog,
            text=f"¿Estás seguro de que deseas eliminar la tarea?",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=20)
        
        ctk.CTkLabel(
            dialog,
            text=f"\"{task.name}\"",
            font=ctk.CTkFont(size=14)
        ).pack(pady=(0, 30))
        
        # Botones
        buttons_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        buttons_frame.pack(pady=10)
        
        def delete():
            try:
                if self.task_service.delete_task(task.id):
                    self._load_tasks()  # Recargar la lista de tareas
            except Exception as e:
                print(f"Error al eliminar la tarea: {e}")
            finally:
                dialog.destroy()
        
        ctk.CTkButton(
            buttons_frame,
            text="Eliminar",
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=delete
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            buttons_frame,
            text="Cancelar",
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            command=dialog.destroy
        ).pack(side="left", padx=10)
    
    def _create_main_content(self) -> None:
        """Crea el área de contenido principal."""
        # Área de contenido principal
        self.main_content = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_content.grid_rowconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)
    
    def _setup_styles(self) -> None:
        """Configura los estilos de la aplicación."""
        # Asegurarse de que nav_buttons existe
        if not hasattr(self, 'nav_buttons') or not self.nav_buttons:
            return
            
        # Configurar colores para los botones de navegación activos/inactivos
        active_color = ("gray75", "gray25")  # Color para el botón activo
        
        # Aplicar estilos a los botones de navegación
        for view_name, btn in self.nav_buttons.items():
            is_active = view_name == self.current_view
            btn.configure(
                fg_color=active_color if is_active else "transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30")
            )
            
    def display_view(self, view_name: str, filter_status: str = None) -> None:
        """Muestra la vista especificada, usando un sistema de cache."""
        # Ocultar la vista actual
        if self.current_view in self.views:
            self.views[self.current_view].pack_forget()

        self.current_view = view_name

        # Si la vista no está en cache, crearla
        if view_name not in self.views:
            if view_name == "dashboard":
                self.views[view_name] = DashboardView(self.main_content, self.task_service, self)
            elif view_name == "tasks":
                self.views[view_name] = TasksView(self.main_content, self.task_service, self, self.config_service)
            elif view_name == "simulation":
                self.views[view_name] = SimulationView(self.main_content, self)
            elif view_name == "stats":
                self.views[view_name] = StatsView(self.main_content, self.task_service, self)
            elif view_name == "settings":
                self.views[view_name] = SettingsView(self.main_content, self, self.config_service, self.task_service, self.export_service)

        # Mostrar la nueva vista
        current_view_widget = self.views[view_name]
        current_view_widget.pack(fill="both", expand=True)

        # Actualizar configuraciones específicas de la vista si es necesario
        if view_name == "tasks":
            current_view_widget.update_config()
            if filter_status:
                current_view_widget.set_status_filter(filter_status)

        # Actualizar el estilo de los botones de navegación
        self._setup_styles()

    
    def _refresh_tasks_view(self):
        """Recarga la vista de tareas desde el cache."""
        if "tasks" in self.views:
            self.views["tasks"]._load_tasks()

    def _apply_initial_config(self):
        """Aplica la configuración guardada al iniciar la aplicación."""
        ctk.set_appearance_mode(self.config_service.get("appearance_mode").lower())
        ctk.set_default_color_theme(self.config_service.get("color_theme"))


    
    def _complete_task(self, dialog, task: Task) -> None:
        """Marca una tarea como completada."""
        try:
            self.task_service.update_task(
                task_id=task.id,
                status=Status.COMPLETED
            )
            dialog.destroy()  # Cerrar el diálogo
            self._load_tasks()  # Recargar la lista de tareas
        except Exception as e:
            print(f"Error al marcar la tarea como completada: {e}")
            dialog.destroy()  # Cerrar el diálogo en caso de error
    
    def _create_sidebar(self) -> None:
        """Crea la barra lateral de navegación."""
        # Crear frame de la barra lateral
        self.sidebar = ctk.CTkFrame(self, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=4, sticky="nsew")
        
        # Configurar el grid de la barra lateral
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(5, weight=1)  # Cambiado de 3 a 5 para que el espacio esté después del selector de tema
        
        # Título de la aplicación
        self.logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="Gestor de Tareas",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("gray10", "gray90")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Botones de navegación
        nav_items = [
            ("📊 Dashboard", "dashboard"),
            ("📋 Tareas", "tasks"),
            ("🧪 Simulación", "simulation"),
            ("📊 Estadísticas", "stats")
        ]
        
        # Crear botones de navegación
        for i, (text, view_name) in enumerate(nav_items, 1):
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=lambda v=view_name: self.display_view(v),
                fg_color="transparent",
                text_color=("gray10", "gray90"),  
                hover_color=("gray70", "gray30"),  
                anchor="w",
                font=ctk.CTkFont(weight="bold")
            )
            btn.grid(row=i, column=0, padx=20, pady=2, sticky="ew")  # Reducido el pady de 5 a 2
            self.nav_buttons[view_name] = btn
            
        
        # Botón de Configuración
        settings_btn = ctk.CTkButton(
            self.sidebar,
            text="⚙️ Configuración",
            command=lambda: self.display_view("settings"),
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            font=ctk.CTkFont(weight="bold")
        )
        settings_btn.grid(row=9, column=0, padx=20, pady=2, sticky="ew")
        self.nav_buttons["settings"] = settings_btn

        # Botón de salir
        exit_btn = ctk.CTkButton(
            self.sidebar,
            text="🚪 Salir",
            font=ctk.CTkFont(weight="bold"),
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=self.quit
        )
        exit_btn.grid(row=10, column=0, padx=20, pady=(10, 20), sticky="ew")
    
    def _create_main_content(self) -> None:
        """Crea el área de contenido principal."""
        # Área de contenido principal
        self.main_content = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
    
    def _setup_styles(self) -> None:
        """Configura los estilos de la aplicación."""
        # Asegurarse de que nav_buttons existe
        if not hasattr(self, 'nav_buttons') or not self.nav_buttons:
            return

        # Obtener el color de acento del tema actual de forma segura
        temp_button = ctk.CTkButton(self)
        accent_color = temp_button.cget("fg_color")
        temp_button.destroy()

        # Aplicar estilos a los botones de navegación
        for view_name, btn in self.nav_buttons.items():
            is_active = view_name == self.current_view
            btn.configure(
                fg_color=accent_color if is_active else "transparent",
                hover_color=accent_color  # Usar también para el hover
            )
            
    
    def _show_task_dialog(self, task: Optional[Task] = None) -> None:
        """Muestra el diálogo para crear o editar una tarea."""
        dialog = TaskDialog(master=self, task_service=self.task_service, on_save=self._refresh_tasks_view, task=task)
        dialog.mainloop()

    
    
    def show_settings_view(self) -> None:
        """Muestra la vista de configuración."""
        label = ctk.CTkLabel(
            self.main_content,
            text="Configuración",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        label.pack(pady=20)
        
        # Aquí irán las opciones de configuración
        # TODO: Implementar la configuración
    
    def change_appearance_mode(self, new_appearance_mode: str) -> None:
        """Cambia el tema de la aplicación."""
        mode_map = {
            "Claro": "light",
            "Oscuro": "dark"
        }
        
        # Actualizar el tema
        mode = mode_map.get(new_appearance_mode, "dark")
        ctk.set_appearance_mode(mode)
        
        # Actualizar colores de la barra lateral según el tema
        if mode == "light":
            self.sidebar.configure(fg_color="gray90")
        else:
            self.sidebar.configure(fg_color=("gray16", "gray16"))


def run_gui() -> None:
    """Inicia la aplicación de escritorio."""
    # Configuración global de CustomTkinter
    ctk.set_appearance_mode("dark")  # Tema oscuro por defecto
    ctk.set_default_color_theme("blue")  # Tema de color azul
    
    # Crear y ejecutar la aplicación
    app = MainWindow()
    
    # Centrar la ventana en la pantalla
    app.update_idletasks()
    width = app.winfo_width()
    height = app.winfo_height()
    x = (app.winfo_screenwidth() // 2) - (width // 2)
    y = (app.winfo_screenheight() // 2) - (height // 2)
    app.geometry(f'{width}x{height}+{x}+{y}')
    
    app.mainloop()
