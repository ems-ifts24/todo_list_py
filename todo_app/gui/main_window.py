"""
Ventana principal de la aplicación de tareas.
"""
import customtkinter as ctk
from typing import Dict, Callable, Any, Optional, List
from pathlib import Path
import os
from datetime import datetime

# Importar modelos y servicios
from ..models.task import Task, Priority, Status
from ..services.task_service import TaskService

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
        
        # Configurar tema por defecto en español
        self.current_theme = "Oscuro"  # Tema predeterminado en español
        ctk.set_appearance_mode("dark")
        
        # Configurar el grid principal
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Inicializar servicios
        self.task_service = TaskService()
        
        # Inicializar variables de estado
        self.current_view = "tasks"  # Vista por defecto
        self.nav_buttons = {}  # Diccionario para los botones de navegación
        self.current_task_id = None  # ID de la tarea actualmente seleccionada
        
        # Variables para el ordenamiento
        self.current_sort_column = "priority"  # Columna por defecto para ordenar
        self.sort_ascending = False        # Orden descendente por defecto
        
        # Variables para la paginación
        self.current_page = 1
        self.tasks_per_page = 8  # Número de tareas por página
        
        # Crear la interfaz
        self._create_sidebar()
        self._create_main_content()
        
        # Configurar estilos (después de crear los widgets)
        self._setup_styles()
        
        # Mostrar la vista de tareas por defecto
        self.show_view(self.current_view)
    
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
            
    def show_view(self, view_name: str) -> None:
        """Muestra la vista especificada."""
        self.current_view = view_name
        
        # Eliminar la vista actual
        for widget in self.main_content.winfo_children():
            widget.destroy()
        
        # Actualizar estado de los botones de navegación
        for name, btn in self.nav_buttons.items():
            if name == view_name:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color="transparent")
        
        # Mostrar la vista correspondiente
        if view_name == "tasks":
            self._show_tasks_view()
        elif view_name == "stats":
            self._show_stats_view()
        elif view_name == "settings":
            self._show_settings_view()
    
    def _show_stats_view(self) -> None:
        """Muestra la vista de estadísticas."""
        label = ctk.CTkLabel(
            self.main_content,
            text="Estadísticas",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        label.pack(pady=20)
        
        # Aquí iría el código para mostrar las estadísticas
        # Por ahora, solo mostramos un mensaje
        ctk.CTkLabel(
            self.main_content,
            text="Vista de estadísticas en desarrollo...",
            font=ctk.CTkFont(size=14)
        ).pack(pady=10)
    
    def _show_settings_view(self) -> None:
        """Muestra la vista de configuración."""
        label = ctk.CTkLabel(
            self.main_content,
            text="Configuración",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        label.pack(pady=20)
        
        # Selector de tema
        theme_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        theme_frame.pack(pady=10)
        
        ctk.CTkLabel(
            theme_frame,
            text="Tema:",
            font=ctk.CTkFont(weight="bold")
        ).pack(side="left", padx=(0, 10))
        
        self.theme_var = ctk.StringVar(value=ctk.get_appearance_mode().capitalize())
        theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            values=["Oscuro", "Claro"],
            variable=self.theme_var,
            command=self._change_theme,
            fg_color=("gray70", "gray30"),
            button_color=("gray60", "gray40"),
            button_hover_color=("gray50", "gray50")
        )
        theme_menu.pack(side="left")
    
    def _change_theme(self, new_theme: str) -> None:
        """Cambia el tema de la aplicación."""
        theme_map = {
            "Oscuro": "dark",
            "Claro": "light"
        }
        
        # Actualizar el tema
        mode = theme_map.get(new_theme, "dark")
        ctk.set_appearance_mode(mode)
        
        # Actualizar el tema actual
        self.current_theme = new_theme
        
        # Actualizar colores de la barra lateral según el tema
        if mode == "light":
            self.sidebar.configure(fg_color="gray90")
        else:
            self.sidebar.configure(fg_color=("gray16", "gray16"))
    
    def _show_tasks_view(self) -> None:
        """Muestra la vista de tareas."""
        # Título
        title_label = ctk.CTkLabel(
            self.main_content,
            text="📋 Mis Tareas",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 20), anchor="w")
        
        # Barra de búsqueda y botón de nueva tarea
        search_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 20))
        
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self._on_search_change)
        
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Buscar tareas...",
            width=300,
            textvariable=self.search_var
        )
        search_entry.pack(side="left", padx=(0, 10))
        
        new_task_btn = ctk.CTkButton(
            search_frame,
            text="➕ Nueva Tarea",
            command=self._show_new_task_dialog,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40")
        )
        new_task_btn.pack(side="left")
        
        # Contenedor para la lista de tareas
        self.tasks_container = ctk.CTkScrollableFrame(
            self.main_content,
            fg_color="transparent"
        )
        self.tasks_container.pack(fill="both", expand=True)
        
        # Crear encabezados de la tabla
        self._create_table_headers()
        
        # Variable para controlar el orden actual
        self.current_sort_column = "created_at"  # Columna por defecto para ordenar
        self.sort_ascending = True               # Orden ascendente por defecto (más antigua a más reciente)
        
        # Controles de paginación
        self.pagination_outer_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.pagination_outer_frame.pack(fill="x", pady=(10, 0))
        
        # Frame interno para centrar los controles
        self.pagination_frame = ctk.CTkFrame(self.pagination_outer_frame, fg_color="transparent")
        self.pagination_frame.pack(expand=True, pady=5)
        
        # Botones de paginación
        self.prev_btn = ctk.CTkButton(
            self.pagination_frame,
            text="⬅️ Anterior",
            command=self._prev_page,
            fg_color="transparent",
            hover_color=("gray70", "gray30"),
            state="disabled"
        )
        self.prev_btn.pack(side="left", padx=5)
        
        self.page_label = ctk.CTkLabel(
            self.pagination_frame,
            text="Página 1"
        )
        self.page_label.pack(side="left", padx=5)
        
        self.next_btn = ctk.CTkButton(
            self.pagination_frame,
            text="Siguiente ➡️",
            command=self._next_page,
            fg_color="transparent",
            hover_color=("gray70", "gray30")
        )
        self.next_btn.pack(side="left", padx=5)
        
        # Cargar tareas iniciales
        self._load_tasks()
    
    def _prev_page(self) -> None:
        """Navega a la página anterior."""
        if self.current_page > 1:
            self.current_page -= 1
            self._load_tasks()
    
    def _next_page(self) -> None:
        """Navega a la página siguiente."""
        self.current_page += 1
        self._load_tasks()
    
    def _on_search_change(self, *args) -> None:
        """Se ejecuta cuando cambia el texto de búsqueda."""
        # Volver a la primera página al buscar
        self.current_page = 1
        self._load_tasks()
    
    def _create_table_headers(self) -> None:
        """Crea los encabezados de la tabla con funcionalidad de ordenación."""
        # Frame para los encabezados
        header_frame = ctk.CTkFrame(self.tasks_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 5))
        
        # Configuración de las columnas
        columns = [
            ("name", "Nombre", 4),         # Nombre - 40% del ancho
            ("priority", "Prioridad", 2),   # Prioridad - 20% del ancho
            ("status", "Estado", 2),        # Estado - 20% del ancho
            ("created_at", "Fecha de creación", 2),  # Fecha de creación - 15% del ancho
            ("actions", "Acciones", 2)      # Acciones - 5% del ancho
        ]
        
        # Crear cada encabezado
        for col_id, col_name, weight in columns:
            # Configurar el grid para el frame de encabezados
            header_frame.columnconfigure(columns.index((col_id, col_name, weight)), weight=weight)
            
            # Frame para cada columna
            col_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
            col_frame.grid(row=0, column=columns.index((col_id, col_name, weight)), 
                         padx=2, pady=2, sticky="nsew")
            
            # No hacer clicable la columna de acciones
            if col_id == "actions":
                header = ctk.CTkLabel(
                    col_frame,
                    text=col_name,
                    font=ctk.CTkFont(weight="bold"),
                    anchor="w"
                )
                header.pack(fill="x", expand=True, anchor="w")
            else:
                header = ctk.CTkButton(
                    col_frame,
                    text=f"{col_name} ▼" if self.current_sort_column == col_id and not self.sort_ascending 
                         else f"{col_name} ▲" if self.current_sort_column == col_id and self.sort_ascending 
                         else col_name,
                    font=ctk.CTkFont(weight="bold"),
                    fg_color="transparent",
                    hover_color=("gray70", "gray30"),
                    text_color=("black", "white"),
                    anchor="w",
                    command=lambda c=col_id: self._sort_tasks(c)
                )
                header.pack(fill="x", expand=True, anchor="w")
    
    def _update_pagination_controls(self, total_pages: int) -> None:
        """Actualiza los controles de paginación."""
        # Actualizar etiqueta de página
        self.page_label.configure(text=f"Página {self.current_page} de {total_pages if total_pages > 0 else 1}")
        
        # Habilitar/deshabilitar botones según la página actual
        self.prev_btn.configure(state="disabled" if self.current_page <= 1 else "normal")
        self.next_btn.configure(state="disabled" if self.current_page >= total_pages else "normal")
    
    def _sort_tasks(self, column: str) -> None:
        """Ordena las tareas por la columna especificada."""
        if self.current_sort_column == column:
            # Si se hace clic en la misma columna, invertir el orden
            self.sort_ascending = not self.sort_ascending
        else:
            # Si es una columna diferente, ordenar ascendente por defecto
            self.current_sort_column = column
            self.sort_ascending = True
        
        # Volver a la primera página al cambiar el orden
        self.current_page = 1
        
        # Recargar tareas con el nuevo orden
        self._load_tasks()
    def _load_tasks(self) -> None:
        """Carga las tareas desde el servicio y las muestra en la interfaz."""
        # Limpiar tareas existentes (excepto los encabezados)
        for widget in self.tasks_container.winfo_children():
            if widget != self.tasks_container.winfo_children()[0]:  # No eliminar los encabezados
                widget.destroy()
        
        # Obtener término de búsqueda
        search_term = self.search_var.get().lower() if hasattr(self, 'search_var') else ""
        
        # Obtener tareas sin ordenar del servicio
        all_tasks = list(self.task_service.tasks.values())  # Obtenemos directamente del diccionario
        
        # Filtrar por término de búsqueda
        if search_term:
            all_tasks = [
                task for task in all_tasks
                if (search_term in task.name.lower() or
                    (task.description and search_term in task.description.lower()))
            ]
        
        # Ordenar tareas
        if self.current_sort_column:
            reverse = not self.sort_ascending
            all_tasks.sort(
                key=lambda x: (
                    str(getattr(x, self.current_sort_column, "") or ""),
                    x.name  # Segundo criterio de ordenación
                ),
                reverse=reverse
            )
        
        # Calcular paginación
        total_tasks = len(all_tasks)
        total_pages = (total_tasks + self.tasks_per_page - 1) // self.tasks_per_page
        
        # Ajustar la página actual si es necesario
        if total_pages > 0 and self.current_page > total_pages:
            self.current_page = total_pages
        elif self.current_page < 1:
            self.current_page = 1
        
        # Obtener tareas para la página actual
        start_idx = (self.current_page - 1) * self.tasks_per_page
        end_idx = min(start_idx + self.tasks_per_page, len(all_tasks))
        tasks_to_show = all_tasks[start_idx:end_idx]
        
        # Mostrar mensaje si no hay tareas
        if not tasks_to_show:
            no_tasks_frame = ctk.CTkFrame(self.tasks_container, fg_color="transparent")
            no_tasks_frame.pack(fill="x", pady=10)
            
            no_tasks_label = ctk.CTkLabel(
                no_tasks_frame,
                text="No hay tareas para mostrar" if not search_term else f"No se encontraron tareas con: '{search_term}'",
                font=ctk.CTkFont(size=14, slant="italic")
            )
            no_tasks_label.pack(pady=20)
        else:
            # Mostrar tareas de la página actual
            for task in tasks_to_show:
                self._create_task_widget(task)
        
        # Actualizar controles de paginación
        if hasattr(self, 'pagination_frame'):
            self._update_pagination_controls(total_pages)
    
    def _create_task_widget(self, task: Task) -> None:
        """Crea un widget para mostrar una tarea en la lista."""
        # Determinar si la tarea está completada (se usa en varios lugares)
        is_completed = task.status == Status.COMPLETED
        
        # Frame principal de la tarea
        task_frame = ctk.CTkFrame(self.tasks_container, fg_color=("#f0f0f0", "#2b2b2b"))
        task_frame.pack(fill="x", pady=2, padx=5)
        
        # Configuración de las columnas (debe coincidir con los encabezados)
        columns = [
            ("name", 4),      # Nombre - 40% del ancho
            ("priority", 2),  # Prioridad - 20% del ancho
            ("status", 2),    # Estado - 20% del ancho
            ("created_at", 2), # Fecha - 15% del ancho
            ("actions", 2)     # Acciones - 5% del ancho
        ]
        
        # Configurar el grid para los elementos de la tarea
        for idx, (col_id, weight) in enumerate(columns):
            task_frame.columnconfigure(idx, weight=weight)
        
        # Nombre de la tarea
        name_label = ctk.CTkLabel(
            task_frame,
            text=task.name,
            anchor="w",
            font=ctk.CTkFont(weight="bold" if task.status != Status.COMPLETED else "bold",
                           overstrike=task.status == Status.COMPLETED)
        )
        name_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Prioridad
        priority_colors = {
            Priority.HIGH: "#e74c3c",
            Priority.MEDIUM: "#f39c12",
            Priority.LOW: "#2ecc71"
        }
        priority_label = ctk.CTkLabel(
            task_frame,
            text=task.priority.value if task.priority else "",
            text_color=priority_colors.get(task.priority, "gray")
        )
        priority_label.grid(row=0, column=1, padx=5, pady=5)
        
        # Estado
        status_colors = {
            Status.PENDING: "#f39c12",
            Status.IN_PROGRESS: "#3498db",
            Status.COMPLETED: "#2ecc71"
        }
        status_label = ctk.CTkLabel(
            task_frame,
            text=task.status.value if task.status else "",
            text_color=status_colors.get(task.status, "gray")
        )
        status_label.grid(row=0, column=2, padx=5, pady=5)
        
        # Fecha y hora de creación
        if hasattr(task, 'created_at') and task.created_at:
            if isinstance(task.created_at, str):
                # Si created_at es un string, intentar convertirlo a datetime
                try:
                    from datetime import datetime
                    created_dt = datetime.fromisoformat(task.created_at.replace('Z', '+00:00'))
                    date_str = created_dt.strftime("%d/%m/%Y %H:%M")
                except (ValueError, AttributeError):
                    date_str = task.created_at
            else:
                # Si ya es un objeto datetime
                date_str = task.created_at.strftime("%d/%m/%Y %H:%M")
        else:
            date_str = ""
            
        date_label = ctk.CTkLabel(task_frame, text=date_str)
        date_label.grid(row=0, column=3, padx=5, pady=5)
        
        # Frame para los botones de acción
        actions_frame = ctk.CTkFrame(task_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=4, padx=5, pady=5, sticky="e")
        
        # Botón de editar
        edit_btn = ctk.CTkButton(
            actions_frame,
            text="✏️",
            width=30,
            height=30,
            fg_color="transparent",
            text_color=("#3498db", "#2980b9"),
            hover_color=("#d6eaf8", "#1a5276"),
            command=lambda t=task: self._show_edit_task_dialog(t) if task.status != Status.COMPLETED else None,
            state="normal" if task.status != Status.COMPLETED else "disabled"
        )
        # Añadir tooltip manual
        def show_edit_tooltip(event, text="Editar tarea"):
            # Primero ocultar cualquier tooltip existente
            if hasattr(edit_btn, 'tooltip'):
                edit_btn.tooltip.destroy()
                
            x, y, _, _ = edit_btn.bbox("insert")
            x += edit_btn.winfo_rootx() + 25
            y += edit_btn.winfo_rooty() + 25
            
            tooltip = ctk.CTkToplevel(edit_btn)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{x}+{y}")
            
            label = ctk.CTkLabel(
                tooltip,
                text=text,
                font=ctk.CTkFont(size=12),
                corner_radius=6,
                fg_color=("gray70", "gray30"),
                text_color=("black", "white"),
                padx=10,
                pady=5
            )
            label.pack()
            tooltip.label = label
            edit_btn.tooltip = tooltip
            
            # Programar la eliminación del tooltip después de 750 milisegundos
            tooltip.after(750, lambda t=tooltip: t.destroy() if t.winfo_exists() else None)
        
        def hide_tooltip(event):
            if hasattr(edit_btn, 'tooltip'):
                edit_btn.tooltip.destroy()
                delattr(edit_btn, 'tooltip')
        
        edit_btn.bind("<Enter>", lambda e: show_edit_tooltip(e, "Editar tarea" if not is_completed else "No se puede editar una tarea completada"))
        edit_btn.bind("<Leave>", hide_tooltip)
        edit_btn.pack(side="left", padx=2)
        
        # Botón de eliminar
        delete_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️",
            width=30,
            height=30,
            fg_color="transparent",
            text_color=("#e74c3c", "#c0392b"),
            hover_color=("#f5b7b1", "#78281F"),
            command=lambda t=task: self._confirm_delete_task(t) if task.status != Status.COMPLETED else None,
            state="normal" if task.status != Status.COMPLETED else "disabled"
        )
        # Añadir tooltip manual
        def show_delete_tooltip(event, text="Eliminar tarea"):
            # Primero ocultar cualquier tooltip existente
            if hasattr(delete_btn, 'tooltip'):
                delete_btn.tooltip.destroy()
                
            x, y, _, _ = delete_btn.bbox("insert")
            x += delete_btn.winfo_rootx() + 25
            y += delete_btn.winfo_rooty() + 25
            
            tooltip = ctk.CTkToplevel(delete_btn)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{x}+{y}")
            
            label = ctk.CTkLabel(
                tooltip,
                text=text,
                font=ctk.CTkFont(size=12),
                corner_radius=6,
                fg_color=("gray70", "gray30"),
                text_color=("black", "white"),
                padx=10,
                pady=5
            )
            label.pack()
            tooltip.label = label
            delete_btn.tooltip = tooltip
            
            # Programar la eliminación del tooltip después de 750 milisegundos
            tooltip.after(750, lambda t=tooltip: t.destroy() if t.winfo_exists() else None)
        
        def hide_delete_tooltip(event):
            if hasattr(delete_btn, 'tooltip'):
                delete_btn.tooltip.destroy()
                delattr(delete_btn, 'tooltip')
        
        delete_btn.bind("<Enter>", lambda e: show_delete_tooltip(e, "Eliminar tarea" if not is_completed else "No se puede eliminar una tarea completada"))
        delete_btn.bind("<Leave>", hide_delete_tooltip)
        delete_btn.pack(side="left", padx=2)
        
        # Función para manejar el clic en el botón de completar
        def on_complete_click():
            if not is_completed:
                self._confirm_complete_task(task)
        
        # Función para mostrar tooltip de completar tarea
        def show_complete_tooltip(event, text):
            # Primero ocultar cualquier tooltip existente
            if hasattr(complete_btn, 'tooltip') and complete_btn.tooltip.winfo_exists():
                complete_btn.tooltip.destroy()
                
            x, y, _, _ = complete_btn.bbox("insert")
            x += complete_btn.winfo_rootx() + 25
            y += complete_btn.winfo_rooty() + 25
            
            tooltip = ctk.CTkToplevel(complete_btn)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{x}+{y}")
            
            label = ctk.CTkLabel(
                tooltip,
                text=text,
                font=ctk.CTkFont(size=12),
                corner_radius=6,
                fg_color=("gray70", "gray30"),
                text_color=("black", "white"),
                padx=10,
                pady=5
            )
            label.pack()
            tooltip.label = label
            complete_btn.tooltip = tooltip
            
            # Programar la eliminación del tooltip después de 750 milisegundos
            tooltip.after(750, lambda t=tooltip: t.destroy() if t.winfo_exists() else None)
        
        def hide_complete_tooltip(event=None):
            if hasattr(complete_btn, 'tooltip') and complete_btn.tooltip.winfo_exists():
                complete_btn.tooltip.destroy()
                delattr(complete_btn, 'tooltip')
        
        # Botón de completar tarea (solo visible si no está completada)
        complete_btn = ctk.CTkButton(
            actions_frame,
            text="✓",
            width=30,
            height=30,
            fg_color=("#2ecc71", "#27ae60") if not is_completed else ("#95a5a6", "#7f8c8d"),
            hover_color=("#27ae60", "#219653") if not is_completed else ("#95a5a6", "#7f8c8d"),
            text_color=("white", "white"),
            command=on_complete_click
        )
        
        if is_completed:
            complete_btn.configure(state="disabled")
        
        # Configurar eventos del tooltip
        tooltip_text = "Tarea completada" if is_completed else "Marcar como completada"
        complete_btn.bind("<Enter>", lambda e, t=tooltip_text: show_complete_tooltip(e, t))
        complete_btn.bind("<Leave>", hide_complete_tooltip)
        complete_btn.bind("<Button-1>", hide_complete_tooltip)
        complete_btn.pack(side="left", padx=2)
    
    def _confirm_complete_task(self, task: Task) -> None:
        """Muestra un diálogo de confirmación antes de marcar una tarea como completada."""
        # Crear diálogo
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirmar Finalización")
        dialog.resizable(True, True)  # Hacer redimensionable
        dialog.minsize(450, 200)  # Tamaño mínimo
        dialog.geometry("550x220")  # Tamaño inicial
        self._setup_window_resize_handler(dialog, "Confirmar Finalización")
        
        # Hacer que el diálogo sea modal
        dialog.transient(self)
        dialog.grab_set()
        
        # Configurar comportamiento al cerrar
        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
        
        # Frame principal con padding
        main_frame = ctk.CTkFrame(dialog, corner_radius=10)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Mensaje de confirmación
        msg = f"¿Estás seguro de que deseas marcar la tarea como completada?\n\n{task.name}"
        label = ctk.CTkLabel(
            main_frame,
            text=msg,
            font=ctk.CTkFont(size=14, weight="bold"),
            wraplength=400,
            justify="center"
        )
        label.pack(pady=(20, 30), padx=20)
        
        # Frame para los botones
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Botón de confirmar
        confirm_btn = ctk.CTkButton(
            button_frame,
            text="Sí, marcar como completada",
            fg_color=("#2ecc71", "#27ae60"),
            hover_color=("#27ae60", "#219653"),
            command=lambda: self._complete_task(dialog, task),
            height=40,
            font=ctk.CTkFont(weight="bold")
        )
        confirm_btn.pack(side="left", expand=True, fill="x", padx=5)
        
        # Botón de cancelar
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            fg_color=("#95a5a6", "#7f8c8d"),
            hover_color=("#7f8c8d", "#6c7a7a"),
            command=dialog.destroy,
            height=40,
            font=ctk.CTkFont(weight="bold")
        )
        cancel_btn.pack(side="right", expand=True, fill="x", padx=5)
        
        # Ajustar tamaño automáticamente
        dialog.update_idletasks()
        
        # Centrar el diálogo en la pantalla
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Obtener el tamaño del diálogo
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        
        # Calcular posición
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        # Aplicar geometría
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Forzar el foco
        dialog.focus_force()
    
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
        self.sidebar.grid_rowconfigure(3, weight=1)
        
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
            ("📋 Tareas", "tasks"),
            ("📊 Estadísticas", "stats")
        ]
        
        # Crear botones de navegación
        for i, (text, view_name) in enumerate(nav_items, 1):
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=lambda v=view_name: self.show_view(v),
                fg_color="transparent",
                text_color=("gray10", "gray90"),  
                hover_color=("gray70", "gray30"),  
                anchor="w",
                font=ctk.CTkFont(weight="bold")
            )
            btn.grid(row=i, column=0, padx=20, pady=5, sticky="ew")
            self.nav_buttons[view_name] = btn
            
        # Frame para el selector de tema
        theme_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        theme_frame.grid(row=5, column=0, padx=10, pady=(20, 10), sticky="ew")
        
        # Título del selector de tema
        ctk.CTkLabel(
            theme_frame, 
            text="Tema:",
            text_color=("gray10", "gray90"),
            anchor="w"
        ).pack(side="left", padx=(10, 5))
        
        # Selector de tema
        # Mapeo entre los valores internos y los textos en español
        self.theme_map = {
            "light": "Claro",
            "dark": "Oscuro"
        }
        
        # Obtener el tema actual en español
        current_mode = ctk.get_appearance_mode()
        current_theme = self.theme_map.get(current_mode, "Oscuro")
        
        self.theme_var = ctk.StringVar(value=current_theme)
        theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            values=["Oscuro", "Claro"],
            variable=self.theme_var,
            command=self._change_theme,
            width=100,
            dropdown_fg_color=("gray90", "gray16"),
            button_color=("gray60", "gray40"),
            button_hover_color=("gray70", "gray35"),
            text_color=("gray10", "gray90")
        )
        theme_menu.pack(side="right", padx=(0, 10))
        
        # Botón de salir
        exit_btn = ctk.CTkButton(
            self.sidebar,
            text="🚪 Salir",
            font=ctk.CTkFont(weight="bold"),
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=self.quit
        )
        exit_btn.grid(row=10, column=0, padx=20, pady=20, sticky="s")
    
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
            
    def show_view(self, view_name: str) -> None:
        """Muestra la vista especificada."""
        # Eliminar la vista actual
        for widget in self.main_content.winfo_children():
            widget.destroy()
        
        # Actualizar estado de los botones de navegación
        for name, btn in self.nav_buttons.items():
            if name == view_name:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color="transparent")
        
        # Mostrar la vista correspondiente
        if view_name == "tasks":
            self._show_tasks_view()
        elif view_name == "stats":
            self._show_stats_view()
        elif view_name == "settings":
            self._show_settings_view()
    
    def _show_edit_task_dialog(self, task: Task) -> None:
        """Muestra el diálogo para editar una tarea existente."""
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Editar Tarea: {task.name}")
        dialog.resizable(True, True)  # Hacer redimensionable
        dialog.geometry("600x600")  # Tamaño inicial más compacto
        dialog.minsize(450, 350)  # Tamaño mínimo más pequeño
        self._setup_window_resize_handler(dialog, f"Editar Tarea: {task.name}")
        dialog.grab_set()  # Hace que el diálogo sea modal
        
        # Centrar el diálogo en la pantalla
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Título
        ctk.CTkLabel(
            dialog,
            text=f"Editar Tarea: {task.name}",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=10)
        
        # Formulario
        form_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        form_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        # Campo de nombre
        ctk.CTkLabel(form_frame, text="Nombre:", anchor="w").pack(fill="x", pady=(5, 0))
        name_entry = ctk.CTkEntry(form_frame, placeholder_text="Descripción de la tarea")
        name_entry.insert(0, task.name)
        name_entry.pack(fill="x", pady=(0, 10))
        
        # Prioridad
        ctk.CTkLabel(form_frame, text="Prioridad:", anchor="w").pack(fill="x", pady=(5, 0))
        priority_var = ctk.StringVar(value=task.priority.value)
        priority_menu = ctk.CTkOptionMenu(
            form_frame,
            values=[p.value for p in Priority],
            variable=priority_var,
            fg_color=("gray70", "gray30"),
            button_color=("gray60", "gray40"),
            button_hover_color=("gray50", "gray50")
        )
        priority_menu.pack(fill="x", pady=(0, 10))
        
        # Estado
        ctk.CTkLabel(form_frame, text="Estado:", anchor="w").pack(fill="x", pady=(5, 0))
        status_var = ctk.StringVar(value=task.status.value)
        status_menu = ctk.CTkOptionMenu(
            form_frame,
            values=[s.value for s in Status],
            variable=status_var,
            fg_color=("gray70", "gray30"),
            button_color=("gray60", "gray40"),
            button_hover_color=("gray50", "gray50")
        )
        status_menu.pack(fill="x", pady=(0, 20))
        
        # Botones
        buttons_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        buttons_frame.pack(pady=10)
        
        def save_changes():
            try:
                name = name_entry.get().strip()
                if not name:
                    raise ValueError("El nombre de la tarea no puede estar vacío")
                
                priority = Priority(priority_var.get())
                status = Status(status_var.get())
                
                # Actualizar la tarea
                self.task_service.update_task(
                    task_id=task.id,
                    name=name,
                    priority=priority,
                    status=status
                )
                
                # Actualizar la lista de tareas
                self._load_tasks()
                dialog.destroy()
                
            except Exception as e:
                # Mostrar mensaje de error
                error_label = ctk.CTkLabel(
                    form_frame,
                    text=str(e),
                    text_color="red"
                )
                error_label.pack(pady=5)
                self.after(3000, error_label.destroy)
        
        ctk.CTkButton(
            buttons_frame,
            text="Guardar Cambios",
            command=save_changes
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            buttons_frame,
            text="Cancelar",
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            command=dialog.destroy
        ).pack(side="left", padx=5)
        
        # Enfocar el campo de nombre
        name_entry.focus_set()
    
    def _show_new_task_dialog(self) -> None:
        """Muestra el diálogo para crear una nueva tarea."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Nueva Tarea")
        dialog.resizable(True, True)
        dialog.minsize(550, 500)  # Tamaño mínimo más pequeño
        dialog.geometry("600x600")  # Tamaño inicial más compacto
        self._setup_window_resize_handler(dialog, "Nueva Tarea")
        dialog.grab_set()  # Hace que el diálogo sea modal
        
        # Centrar el diálogo en la pantalla
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Título
        ctk.CTkLabel(
            dialog,
            text="Nueva Tarea",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=10)
        
        # Formulario
        form_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        form_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        # Campo de nombre
        ctk.CTkLabel(form_frame, text="Nombre:", anchor="w").pack(fill="x", pady=(5, 0))
        name_entry = ctk.CTkEntry(form_frame, placeholder_text="Descripción de la tarea")
        name_entry.pack(fill="x", pady=(0, 10))
        
        # Prioridad
        ctk.CTkLabel(form_frame, text="Prioridad:", anchor="w").pack(fill="x", pady=(5, 0))
        priority_var = ctk.StringVar(value=Priority.MEDIUM.value)
        priority_menu = ctk.CTkOptionMenu(
            form_frame,
            values=[p.value for p in Priority],
            variable=priority_var,
            fg_color=("gray70", "gray30"),
            button_color=("gray60", "gray40"),
            button_hover_color=("gray50", "gray50")
        )
        priority_menu.pack(fill="x", pady=(0, 10))
        
        # Estado
        ctk.CTkLabel(form_frame, text="Estado:", anchor="w").pack(fill="x", pady=(5, 0))
        status_var = ctk.StringVar(value=Status.PENDING.value)
        status_menu = ctk.CTkOptionMenu(
            form_frame,
            values=[s.value for s in Status],
            variable=status_var,
            fg_color=("gray70", "gray30"),
            button_color=("gray60", "gray40"),
            button_hover_color=("gray50", "gray50")
        )
        status_menu.pack(fill="x", pady=(0, 20))
        
        # Botones
        buttons_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        buttons_frame.pack(pady=10)
        
        def save_task():
            try:
                name = name_entry.get().strip()
                if not name:
                    raise ValueError("El nombre de la tarea no puede estar vacío")
                
                priority = Priority(priority_var.get())
                status = Status(status_var.get())
                
                # Crear la tarea
                self.task_service.create_task(
                    name=name,
                    priority=priority,
                    status=status
                )
                
                # Actualizar la lista de tareas
                self._load_tasks()
                dialog.destroy()
                
            except Exception as e:
                # Mostrar mensaje de error
                error_label = ctk.CTkLabel(
                    form_frame,
                    text=str(e),
                    text_color="red"
                )
                error_label.pack(pady=5)
                self.after(3000, error_label.destroy)
        
        ctk.CTkButton(
            buttons_frame,
            text="Guardar",
            command=save_task
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            buttons_frame,
            text="Cancelar",
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            command=dialog.destroy
        ).pack(side="left", padx=5)
        
        # Enfocar el campo de nombre
        name_entry.focus_set()
    
    def show_stats_view(self) -> None:
        """Muestra la vista de estadísticas."""
        label = ctk.CTkLabel(
            self.main_content,
            text="Estadísticas",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        label.pack(pady=20)
        
        # Aquí irán los gráficos de estadísticas
        # TODO: Implementar los gráficos
    
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
