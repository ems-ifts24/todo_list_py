"""
Ventana principal de la aplicación de tareas.
"""
import customtkinter as ctk
from typing import Dict, Callable, Any, Optional, List
import tkinter as tk
from tkinter import messagebox, ttk, Toplevel, StringVar, BooleanVar, filedialog
from datetime import datetime, timedelta
import os
import re
import webbrowser

from ..models.task import Task, Priority, Status
from ..services.task_service import TaskService
from ..services.graphics_service import GraphicsService

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
        
        # Inicializar servicio de exportación (importación diferida para evitar dependencia circular)
        from ..services.export_service import ExportService
        self.export_service = ExportService()
        
        # Inicializar variables de estado
        self.current_view = "dashboard"  # Vista por defecto (dashboard)
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
        
        # Mostrar la vista del dashboard por defecto
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
            
    def show_view(self, view_name: str, filter_status: str = None) -> None:
        """Muestra la vista especificada con un filtro opcional.
        
        Args:
            view_name: Nombre de la vista a mostrar ('tasks', 'stats', 'settings', 'dashboard')
            filter_status: Estado por el que filtrar las tareas (opcional)
        """
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
            if filter_status:
                # Si se proporciona un filtro, establecerlo antes de mostrar la vista
                if not hasattr(self, 'current_status_filter') or self.current_status_filter != filter_status:
                    self.current_status_filter = filter_status
                    self.current_page = 1  # Resetear a la primera página al cambiar de filtro
            self._show_tasks_view(filter_status)
        elif view_name == "stats":
            self._show_stats_view()
        elif view_name == "settings":
            self._show_settings_view()
        elif view_name == "dashboard":
            # Limpiar filtros al volver al dashboard
            if hasattr(self, 'current_status_filter'):
                del self.current_status_filter
            self._show_dashboard_view()
    
    def _show_dashboard_view(self) -> None:
        """Muestra la vista del dashboard."""
        # Limpiar el contenido actual
        for widget in self.main_content.winfo_children():
            widget.destroy()
            
        # Título del dashboard
        label = ctk.CTkLabel(
            self.main_content,
            text="Dashboard",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        label.pack(pady=20)
        
        # Aquí puedes agregar los widgets del dashboard
        # Por ejemplo, tarjetas con resúmenes, gráficos, etc.
        ctk.CTkLabel(
            self.main_content,
            text="Resumen de Actividades",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Frame para las tarjetas de resumen
        cards_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        cards_frame.pack(fill="x", pady=20, padx=20)  # Aumentado el padding vertical
        
        # Configuración común para todas las tarjetas
        card_config = {
            "width": 200,
            "height": 120,  # Altura fija para las tarjetas
            "corner_radius": 12,
            "border_width": 3,
            "fg_color": ("white", "gray10")
        }
        
        # Estilo para el texto de las tarjetas
        label_style = {
            "font": ctk.CTkFont(size=14, weight="bold"),
            "text_color": ("gray30", "gray70")
        }
        
        count_style = {
            "font": ctk.CTkFont(size=28, weight="bold"),
            "text_color": ("gray10", "gray90")
        }
        
        # Función para manejar el clic en las tarjetas
        def create_card_click_handler(status):
            def handler(event):
                self.show_view("tasks", status)
            return handler
        
        # Tarjeta de tareas pendientes (borde naranja)
        pending_card = ctk.CTkFrame(
            cards_frame,
            **card_config,
            border_color=("#FF8C00", "#FFA500"),  # Naranja
            cursor="hand2"
        )
        pending_card.pack_propagate(False)
        pending_card.pack(side="left", padx=10, pady=5, fill="both", expand=True)
        pending_card.bind("<Button-1>", create_card_click_handler("Tareas Pendientes"))
        
        # Hacer que los hijos también sean clickeables
        for child in [pending_card]:
            child.bind("<Button-1>", create_card_click_handler("Tareas Pendientes"))
        
        ctk.CTkLabel(
            pending_card,
            text="Tareas Pendientes",
            **label_style,
            cursor="hand2"
        ).pack(pady=(25, 10))
        
        self.pending_count = ctk.CTkLabel(
            pending_card,
            text="0",
            **count_style,
            cursor="hand2"
        )
        self.pending_count.pack()
        
        # Tarjeta de tareas en curso (borde azul)
        in_progress_card = ctk.CTkFrame(
            cards_frame,
            **card_config,
            border_color=("#1E90FF", "#4169E1"),  # Azul
            cursor="hand2"
        )
        in_progress_card.pack_propagate(False)
        in_progress_card.pack(side="left", padx=10, pady=5, fill="both", expand=True)
        in_progress_card.bind("<Button-1>", create_card_click_handler("En Curso"))
        
        # Hacer que los hijos también sean clickeables
        for child in [in_progress_card]:
            child.bind("<Button-1>", create_card_click_handler("En Curso"))
        
        ctk.CTkLabel(
            in_progress_card,
            text="En Curso",
            **label_style,
            cursor="hand2"
        ).pack(pady=(25, 10))
        
        self.overdue_count = ctk.CTkLabel(
            in_progress_card,
            text="0",
            **count_style,
            cursor="hand2"
        )
        self.overdue_count.pack()
        
        # Tarjeta de tareas finalizadas (borde verde)
        completed_card = ctk.CTkFrame(
            cards_frame,
            **card_config,
            border_color=("#32CD32", "#2E8B57"),  # Verde
            cursor="hand2"
        )
        completed_card.pack_propagate(False)
        completed_card.pack(side="left", padx=10, pady=5, fill="both", expand=True)
        completed_card.bind("<Button-1>", create_card_click_handler("Tareas Finalizadas"))
        
        # Hacer que los hijos también sean clickeables
        for child in [completed_card]:
            child.bind("<Button-1>", create_card_click_handler("Tareas Finalizadas"))
        
        ctk.CTkLabel(
            completed_card,
            text="Tareas Finalizadas",
            **label_style,
            cursor="hand2"
        ).pack(pady=(25, 10))
        
        self.completed_count = ctk.CTkLabel(
            completed_card,
            text="0",
            **count_style,
            cursor="hand2"
        )
        self.completed_count.pack()
        
        # Establecer el padding para el contenedor de tarjetas
        cards_frame.pack_configure(padx=20, pady=15)
        
        # Contenedor para la barra de progreso
        progress_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        progress_frame.pack(fill="x", pady=(20, 10), padx=20)
        
        # Etiqueta del progreso
        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="Progreso general: 0%",
            font=ctk.CTkFont(weight="bold")
        )
        self.progress_label.pack(anchor="w", pady=(0, 5))
        
        # Barra de progreso
        self.progress_bar = ctk.CTkProgressBar(
            progress_frame,
            height=20,
            corner_radius=10,
            progress_color=("#4CAF50", "#2E7D32"),  # Verde
            fg_color=("#E0E0E0", "#424242")  # Fondo claro/oscuro
        )
        self.progress_bar.pack(fill="x", pady=(0, 10))
        self.progress_bar.set(0)  # Inicialmente en 0%
        
        # Actualizar los contadores y la barra de progreso
        self._update_dashboard_counts()
        
        # Sección de Racha de Productividad
        productivity_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        productivity_frame.pack(fill="x", pady=(30, 20), padx=20)
        
        # Título de la sección
        ctk.CTkLabel(
            productivity_frame,
            text="📅 Racha de Productividad",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", pady=(0, 10))
        
        # Frame para el gráfico de barras
        chart_frame = ctk.CTkFrame(productivity_frame, fg_color=("#f5f5f5", "#1a1a1a"), corner_radius=12)
        chart_frame.pack(fill="both", expand=True)
        
        # Contenedor principal para el gráfico
        self.chart_container = ctk.CTkFrame(chart_frame, fg_color="transparent")
        self.chart_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Inicializar el gráfico
        self._init_productivity_chart()
        
    def _update_dashboard_counts(self):
        """Actualiza los contadores del dashboard y la barra de progreso."""
        try:
            tasks = self.task_service.get_all_tasks()
            total_tasks = len(tasks)
            
            # Contar tareas por estado
            pending = 0
            completed = 0
            in_progress = 0
            
            for task in tasks:
                if task.status == Status.COMPLETED:
                    completed += 1
                elif task.status == Status.IN_PROGRESS:
                    in_progress += 1
                else:  # PENDING
                    pending += 1
            
            # Actualizar las etiquetas
            self.pending_count.configure(text=str(pending))
            self.completed_count.configure(text=str(completed))
            self.overdue_count.configure(text=str(in_progress))
            
            # Actualizar la barra de progreso
            if total_tasks > 0:
                progress = completed / total_tasks
                self.progress_bar.set(progress)
                self.progress_label.configure(
                    text=f"Progreso general: {int(progress * 100)}%"
                )
            else:
                self.progress_bar.set(0)
                self.progress_label.configure(text="Progreso general: 0%")
            
            # Actualizar el gráfico de productividad
            self._update_productivity_chart()
            
        except Exception as e:
            print(f"Error al actualizar el dashboard: {e}")
    
    def _init_productivity_chart(self):
        """Inicializa el contenedor del gráfico de productividad."""
        # Limpiar el contenedor si ya existe
        for widget in self.chart_container.winfo_children():
            widget.destroy()
            
        # Crear el contenedor de barras
        self.bars_container = ctk.CTkFrame(self.chart_container, fg_color="transparent")
        self.bars_container.pack(fill="both", expand=True)
        
        # Actualizar el gráfico
        self._update_productivity_chart()
        
    def _update_productivity_chart(self):
        """Actualiza el gráfico de racha de productividad."""
        try:
            # Verificar si el contenedor de barras existe
            if not hasattr(self, 'bars_container') or not self.bars_container.winfo_exists():
                return
                
            # Limpiar el contenedor de barras
            for widget in self.bars_container.winfo_children():
                widget.destroy()
            
            # Obtener tareas finalizadas en los últimos 7 días
            completed_tasks = self.task_service.get_completed_tasks_last_week()
            
            if not completed_tasks:
                # Mostrar mensaje si no hay datos
                no_data_label = ctk.CTkLabel(
                    self.bars_container,
                    text="No hay datos de productividad recientes",
                    text_color=("gray50", "gray60"),
                    font=ctk.CTkFont(weight="bold")
                )
                no_data_label.pack(pady=40)
                return
                
            # Obtener la altura máxima para escalar las barras
            max_count = max(completed_tasks.values()) if any(completed_tasks.values()) else 1
            max_height = 150  # Altura máxima en píxeles para la barra más alta
            
            # Frame para el título y estadísticas
            header_frame = ctk.CTkFrame(self.bars_container, fg_color="transparent")
            header_frame.pack(fill="x", pady=(0, 15))
            
            # Título de la sección
            ctk.CTkLabel(
                header_frame,
                text="Tareas finalizadas en los últimos 7 días",
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(side="left")
            
            # Estadísticas
            total_tasks = sum(completed_tasks.values())
            avg_tasks = total_tasks / len(completed_tasks) if completed_tasks else 0
            
            stats_text = f"Total: {total_tasks} | Promedio diario: {avg_tasks:.1f}"
            ctk.CTkLabel(
                header_frame,
                text=stats_text,
                text_color=("gray50", "gray60"),
                font=ctk.CTkFont(size=12)
            ).pack(side="right")
            
            # Frame para el gráfico
            chart_frame = ctk.CTkFrame(self.bars_container, fg_color=("#f5f5f5", "#1a1a1a"), corner_radius=8)
            chart_frame.pack(fill="both", expand=True, padx=0, pady=0)
            
            # Frame para las barras
            bars_frame = ctk.CTkFrame(chart_frame, fg_color="transparent")
            bars_frame.pack(side="top", fill="both", expand=True, padx=20, pady=(20, 10))
            
            # Frame para las etiquetas de los días
            days_frame = ctk.CTkFrame(chart_frame, fg_color="transparent")
            days_frame.pack(side="bottom", fill="x", pady=(0, 10))
            
            # Configurar el grid para las columnas
            num_days = len(completed_tasks)
            for i in range(num_days):
                bars_frame.columnconfigure(i, weight=1)
                days_frame.columnconfigure(i, weight=1)
            
            # Crear las barras y etiquetas
            for i, (date, count) in enumerate(completed_tasks.items()):
                # Calcular la altura de la barra
                bar_height = (count / max_count) * max_height if max_count > 0 else 0
                bar_height = max(10, bar_height)  # Mínimo 10px de altura para que sea visible
                
                # Crear el marco de la barra
                bar_frame = ctk.CTkFrame(bars_frame, fg_color="transparent")
                bar_frame.grid(row=0, column=i, padx=4, sticky="nsew")
                bar_frame.columnconfigure(0, weight=1)
                
                # Contenedor para la barra y su etiqueta
                bar_container = ctk.CTkFrame(bar_frame, fg_color="transparent")
                bar_container.pack(fill="both", expand=True)
                
                # Mostrar el contador sobre la barra
                count_label = ctk.CTkLabel(
                    bar_container,
                    text=str(count) if count > 0 else "0",
                    text_color=("black", "white"),
                    font=ctk.CTkFont(size=12, weight="bold")
                )
                count_label.pack(side="top", pady=(0, 5))
                
                # Crear la barra
                bar_color = "#4CAF50"  # Verde
                bar = ctk.CTkFrame(
                    bar_container, 
                    fg_color=bar_color,
                    corner_radius=6,
                    height=bar_height,
                    width=30
                )
                bar.pack(side="bottom", fill="x")
                
                # Agregar el día de la semana
                day_name = date.strftime("%a").upper()  # Nombre corto del día (LUN, MAR, etc.)
                day_label = ctk.CTkLabel(
                    days_frame,
                    text=day_name,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=("gray30", "gray70")
                )
                day_label.grid(row=0, column=i, pady=(5, 0))
                
                # Agregar la fecha
                date_label = ctk.CTkLabel(
                    days_frame,
                    text=date.strftime("%d/%m"),
                    text_color=("gray50", "gray60"),
                    font=ctk.CTkFont(size=11)
                )
                date_label.grid(row=1, column=i, pady=(2, 0))
                
                # Resaltar el día actual
                if date == datetime.now().date():
                    day_label.configure(text_color=("#2196F3", "#64B5F6"))
                    date_label.configure(text_color=("#2196F3", "#64B5F6"))
                    bar.configure(fg_color=("#2196F3", "#64B5F6"))  # Azul para el día actual
                    
                    # Añadir etiqueta "Hoy"
                    today_label = ctk.CTkLabel(
                        bar_frame,
                        text="HOY",
                        text_color=("#2196F3", "#64B5F6"),
                        font=ctk.CTkFont(size=10, weight="bold")
                    )
                    today_label.pack(side="top", pady=(0, 5))
                    
                    # Mover el contador debajo de la etiqueta "HOY"
                    count_label.pack_forget()
                    count_label.pack(side="top", pady=(0, 5))
                
                # Función para manejar los tooltips
                def create_tooltip(widget, text):
                    # Variable para almacenar el tooltip
                    tooltip = None
                    
                    # Función para verificar si el mouse salió del tooltip
                    def check_mouse_leave():
                        nonlocal tooltip
                        if tooltip is not None and tooltip.winfo_exists():
                            x, y = tooltip.winfo_pointerxy()
                            widget_x = widget.winfo_rootx()
                            widget_y = widget.winfo_rooty()
                            widget_w = widget.winfo_width()
                            widget_h = widget.winfo_height()
                            
                            if not (widget_x <= x <= widget_x + widget_w and 
                                   widget_y <= y <= widget_y + widget_h):
                                tooltip.destroy()
                    
                    def show_tooltip(event):
                        nonlocal tooltip
                        
                        # Si ya hay un tooltip, no hacer nada
                        if tooltip is not None and tooltip.winfo_exists():
                            return
                        
                        # Crear el tooltip
                        tooltip = ctk.CTkToplevel(widget)
                        tooltip.overrideredirect(True)
                        tooltip.attributes("-topmost", True)
                        
                        # Obtener posición del mouse
                        x = widget.winfo_pointerx() + 10
                        y = widget.winfo_pointery() + 10
                        tooltip.geometry(f"+{x}+{y}")
                        
                        # Crear etiqueta dentro del tooltip
                        label = ctk.CTkLabel(
                            tooltip,
                            text=text,
                            fg_color=("white", "#2b2b2b"),
                            corner_radius=6,
                            padx=10,
                            pady=5
                        )
                        label.pack()
                        
                        # Asegurarse de que el tooltip se cierre al salir del widget
                        def on_leave(event):
                            if tooltip is not None and tooltip.winfo_exists():
                                tooltip.destroy()
                        
                        # Configurar eventos
                        widget.bind("<Leave>", on_leave, add="+")
                        tooltip.bind("<Leave>", lambda e: tooltip.after(100, check_mouse_leave), add="+")
                    
                    # Configurar eventos
                    widget.bind("<Enter>", show_tooltip)
                    widget.bind("<Leave>", lambda e: tooltip.after(100, check_mouse_leave) if hasattr(tooltip, 'winfo_exists') and tooltip.winfo_exists() else None)
                
                # Crear el texto del tooltip
                tooltip_text = (
                    f"{date.strftime('%A, %d de %B')}\n"
                    f"Tareas finalizadas: {count}"
                )
                
                # Configurar el tooltip para el contenedor de la barra
                create_tooltip(bar_container, tooltip_text)
                
        except Exception as e:
            print(f"Error al actualizar el gráfico de productividad: {e}")
    
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
    
    def _show_tasks_view(self, status_filter: str = None) -> None:
        """Muestra la vista de tareas."""
        # Título
        title_label = ctk.CTkLabel(
            self.main_content,
            text=" Mis Tareas",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 10), anchor="w")
        
        # Frame para controles de filtrado
        filter_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        filter_frame.pack(fill="x", pady=(0, 10))
        
        # Filtro de búsqueda
        search_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        search_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Inicializar filtros
        self.current_status_filter = status_filter
        self.current_priority_filter = None
        self.date_filter = {
            'type': None,  # 'today', 'week', 'month', 'custom'
            'start': None,
            'end': None
        }
            
        # Frame para la barra de búsqueda y botón de limpiar
        search_bar_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_bar_frame.pack(side="left", fill="x", expand=True)
        
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self._on_search_change)
        
        # Entrada de búsqueda
        search_entry = ctk.CTkEntry(
            search_bar_frame,
            placeholder_text="Buscar tareas...",
            width=300,
            textvariable=self.search_var
        )
        search_entry.pack(side="left", padx=(0, 5))
        
        # Botón para limpiar búsqueda
        clear_btn = ctk.CTkButton(
            search_bar_frame,
            text="×",
            width=30,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            command=self._clear_search
        )
        clear_btn.pack(side="left")
        
        new_task_btn = ctk.CTkButton(
            search_frame,
            text=" Nueva Tarea",
            command=self._show_new_task_dialog,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40")
        )
        new_task_btn.pack(side="left", padx=(0, 10))
        
        # Botón para exportar a CSV
        export_btn = ctk.CTkButton(
            search_frame,
            text=" Exportar a CSV",
            command=self._export_to_csv,
            fg_color=("#2ecc71", "#27ae60"),
            hover_color=("#27ae60", "#219653"),
            text_color=("white", "white")
        )
        export_btn.pack(side="left", padx=(0, 10))
        
        # Botón para mostrar/ocultar filtros avanzados
        self.show_filters_btn = ctk.CTkButton(
            search_frame,
            text="Filtros Avanzados ▼",
            command=self._toggle_advanced_filters,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40")
        )
        self.show_filters_btn.pack(side="left")
        
        # Frame para filtros avanzados (inicialmente oculto)
        self.advanced_filters_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.advanced_filters_frame.pack(fill="x", pady=(0, 10))
        self.advanced_filters_visible = False
        
        # Controles de filtros avanzados
        self._setup_advanced_filters()
        
        # Contenedor para la lista de tareas
        self.tasks_container = ctk.CTkFrame(
            self.main_content,
            fg_color="transparent"
        )
        self.tasks_container.pack(fill="both", expand=True)
        
        # Crear encabezados de la tabla
        self._create_table_headers()
        
        # Variable para controlar el orden actual
        self.current_sort_column = "created_at"  # Columna por defecto para ordenar
        self.sort_ascending = True               # Orden ascendente por defecto (más antigua a más reciente)
        self.current_status_filter = status_filter  # Filtro de estado actual
        
        # Controles de paginación
        self.pagination_outer_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.pagination_outer_frame.pack(fill="x", pady=(10, 0))
        
        # Frame interno para centrar los controles
        self.pagination_frame = ctk.CTkFrame(self.pagination_outer_frame, fg_color="transparent")
        self.pagination_frame.pack(expand=True, pady=5)
        
        # Botones de paginación
        self.prev_btn = ctk.CTkButton(
            self.pagination_frame,
            text=" Anterior",
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
            text="Siguiente ",
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
    
    def _clear_search(self) -> None:
        """Limpia el campo de búsqueda, los filtros y actualiza la lista de tareas."""
        self.search_var.set("")
        if hasattr(self, 'current_status_filter'):
            del self.current_status_filter
        self.current_page = 1
        self._load_tasks()
        
    def _clear_filters(self) -> None:
        """Limpia todos los filtros y actualiza la lista de tareas."""
        self.search_var.set("")
        self.current_status_filter = None
        self.current_page = 1
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
            ("name", "Tarea", 6),               # Nombre - 50% del ancho
            ("priority", "Prioridad", 1),       # Prioridad - 10% del ancho
            ("status", "Estado", 2),            # Estado - 15% del ancho
            ("created_at", "Creada", 2),        # Fecha de creación - 15% del ancho
            ("updated_at", "Actualizada", 2),    # Fecha de actualización - 15% del ancho
            ("actions", "Acciones", 1)          # Acciones - 5% del ancho
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
        
    def _export_to_csv(self):
        """Exporta las tareas filtradas a un archivo CSV permitiendo elegir la ubicación de guardado."""
        try:
            # Obtener tareas filtradas y ordenadas
            tasks = self._get_filtered_sorted_tasks()
            
            if not tasks:
                messagebox.showinfo(
                    "Exportar a CSV",
                    "No hay tareas para exportar con los filtros actuales.",
                    parent=self
                )
                return
            
            # Mostrar diálogo para seleccionar ubicación de guardado
            import os
            from tkinter import filedialog
            
            # Obtener la ruta del escritorio por defecto
            default_dir = os.path.join(os.path.expanduser('~'), 'Desktop')
            default_filename = f"tareas_exportadas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            filepath = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
                initialdir=default_dir,
                initialfile=default_filename,
                title="Guardar archivo CSV como..."
            )
            
            # Si el usuario cancela el diálogo
            if not filepath:
                return
                
            # Exportar a CSV en la ubicación seleccionada
            self.export_service.export_to_csv(tasks, filepath)
            
            # Mostrar mensaje de éxito
            messagebox.showinfo(
                "Exportación exitosa",
                f"Se exportaron {len(tasks)} tareas a:\n{filepath}",
                parent=self
            )
            
        except Exception as e:
            messagebox.showerror(
                "Error al exportar",
                f"Ocurrió un error al exportar las tareas:\n{str(e)}",
                parent=self
            )
    
    def _setup_advanced_filters(self) -> None:
        """Configura los controles de filtros avanzados."""
        # Frame para los filtros de estado
        status_frame = ctk.CTkFrame(self.advanced_filters_frame, fg_color="transparent")
        status_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(status_frame, text="Estado:").pack(side="left", padx=(0, 5))
        
        self.status_var = ctk.StringVar(value="Todas")
        statuses = ["Todas", "Tareas Pendientes", "En Curso", "Tareas Finalizadas"]
        
        for status in statuses:
            rb = ctk.CTkRadioButton(
                status_frame,
                text=status,
                variable=self.status_var,
                value=status,
                command=self._on_status_change
            )
            rb.pack(side="left", padx=5)
        
        # Frame para los filtros de prioridad
        priority_frame = ctk.CTkFrame(self.advanced_filters_frame, fg_color="transparent")
        priority_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(priority_frame, text="Prioridad:").pack(side="left", padx=(0, 5))
        
        self.priority_var = ctk.StringVar(value="Todas")
        priorities = ["Todas"] + [p.value for p in Priority]
        
        for priority in priorities:
            rb = ctk.CTkRadioButton(
                priority_frame,
                text=priority,
                variable=self.priority_var,
                value=priority,
                command=self._apply_filters
            )
            rb.pack(side="left", padx=5)
        
        # Frame para los filtros de fecha
        date_frame = ctk.CTkFrame(self.advanced_filters_frame, fg_color="transparent")
        date_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(date_frame, text="Filtrar por fecha de:").pack(side="left", padx=(0, 5))
        
        # Selector de tipo de fecha (creación o actualización)
        self.date_type_var = ctk.StringVar(value="created_at")
        date_type_menu = ctk.CTkOptionMenu(
            date_frame,
            values=["Creación", "Actualización"],
            variable=ctk.StringVar(value="Creación"),
            command=lambda v: self._on_date_type_change(v)
        )
        date_type_menu.pack(side="left", padx=5)
        
        date_options = ["Sin filtrar", "Hoy", "Esta semana", "Este mes", "Personalizado"]
        self.date_filter_var = ctk.StringVar(value="Sin filtrar")
        self.date_filter_menu = ctk.CTkOptionMenu(
            date_frame,
            values=date_options,
            variable=self.date_filter_var,
            command=self._on_date_filter_change
        )
        self.date_filter_menu.pack(side="left", padx=5)
        
        # Frame para el rango de fechas personalizado (inicialmente oculto)
        self.custom_date_frame = ctk.CTkFrame(date_frame, fg_color="transparent")
        
        self.start_date_var = ctk.StringVar()
        self.end_date_var = ctk.StringVar()
        
        ctk.CTkLabel(self.custom_date_frame, text="Desde:").pack(side="left")
        ctk.CTkEntry(self.custom_date_frame, textvariable=self.start_date_var, 
                    placeholder_text="AAAA-MM-DD", width=100).pack(side="left", padx=5)
        ctk.CTkLabel(self.custom_date_frame, text="Hasta:").pack(side="left")
        ctk.CTkEntry(self.custom_date_frame, textvariable=self.end_date_var, 
                    placeholder_text="AAAA-MM-DD", width=100).pack(side="left", padx=5)
        
        # Botón para aplicar filtros
        buttons_frame = ctk.CTkFrame(self.advanced_filters_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(5, 0))
        
        clear_btn = ctk.CTkButton(
            buttons_frame,
            text="Limpiar Filtros",
            command=self._clear_filters,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40")
        )
        clear_btn.pack(side="left", padx=5)
        
        apply_btn = ctk.CTkButton(
            buttons_frame,
            text="Aplicar Filtros",
            command=self._apply_filters,
            fg_color=("#2ecc71", "#27ae60"),
            hover_color=("#27ae60", "#219653")
        )
        apply_btn.pack(side="right")
        
        # Ocultar filtros avanzados inicialmente
        self.advanced_filters_frame.pack_forget()
    
    def _toggle_advanced_filters(self) -> None:
        """Muestra u oculta los filtros avanzados."""
        if self.advanced_filters_visible:
            self.advanced_filters_frame.pack_forget()
            self.show_filters_btn.configure(text="Filtros Avanzados ▼")
        else:
            self.advanced_filters_frame.pack(fill="x", pady=(0, 10))
            self.show_filters_btn.configure(text="Ocultar Filtros ▲")
        
        self.advanced_filters_visible = not self.advanced_filters_visible
    
    def _on_status_change(self) -> None:
        """Maneja el cambio en el selector de estado."""
        status_map = {
            "Todas": None,
            "Tareas Pendientes": "Tareas Pendientes",
            "En Curso": "En Curso",
            "Tareas Finalizadas": "Tareas Finalizadas"
        }
        self.current_status_filter = status_map.get(self.status_var.get())
        self._apply_filters()
    
    def _on_date_type_change(self, date_type: str) -> None:
        """Maneja el cambio en el tipo de fecha (creación/actualización)."""
        self.date_field = "created_at" if date_type == "Creación" else "updated_at"
        self._apply_filters()
    
    def _on_date_filter_change(self, selected_option: str) -> None:
        """Maneja el cambio en el selector de fecha."""
        today = datetime.now().date()
        
        if selected_option == "Hoy":
            self.start_date_var.set(today.strftime("%Y-%m-%d"))
            self.end_date_var.set(today.strftime("%Y-%m-%d"))
            self.custom_date_frame.pack_forget()
            self._apply_filters()
        elif selected_option == "Esta semana":
            start = today - timedelta(days=today.weekday())
            self.start_date_var.set(start.strftime("%Y-%m-%d"))
            self.end_date_var.set(today.strftime("%Y-%m-%d"))
            self.custom_date_frame.pack_forget()
            self._apply_filters()
        elif selected_option == "Este mes":
            start = today.replace(day=1)
            self.start_date_var.set(start.strftime("%Y-%m-%d"))
            self.end_date_var.set(today.strftime("%Y-%m-%d"))
            self.custom_date_frame.pack_forget()
            self._apply_filters()
        elif selected_option == "Personalizado":
            self.custom_date_frame.pack(side="left", padx=5)
        else:
            self.start_date_var.set("")
            self.end_date_var.set("")
            self.custom_date_frame.pack_forget()
            self._apply_filters()
    
    def _apply_filters(self) -> None:
        """Aplica todos los filtros seleccionados."""
        # Actualizar filtro de prioridad
        priority = self.priority_var.get()
        self.current_priority_filter = priority if priority != "Todas" else None
        
        # Actualizar filtro de fecha
        date_option = self.date_filter_var.get()
        if date_option == "Sin filtrar":
            self.start_date_var.set("")
            self.end_date_var.set("")
        
        # Recargar tareas con los nuevos filtros
        self.current_page = 1
        self._load_tasks()
    
    def _clear_filters(self) -> None:
        """Limpia todos los filtros aplicados."""
        if hasattr(self, 'search_var'):
            self.search_var.set("")
        
        if hasattr(self, 'status_var'):
            self.status_var.set("Todas")
            self.current_status_filter = None
        
        if hasattr(self, 'priority_var'):
            self.priority_var.set("Todas")
            self.current_priority_filter = None
        
        if hasattr(self, 'date_filter_var'):
            self.date_filter_var.set("Sin filtrar")
            self.start_date_var.set("")
            self.end_date_var.set("")
            self.custom_date_frame.pack_forget()
        
        self.current_page = 1
        self._load_tasks()
    
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
    
    def _get_filtered_sorted_tasks(self):
        """Obtiene las tareas filtradas y ordenadas según los criterios actuales."""
        # Obtener término de búsqueda
        search_term = self.search_var.get().lower() if hasattr(self, 'search_var') and self.search_var.get() else ""
        
        # Obtener tareas sin ordenar del servicio
        all_tasks = list(self.task_service.tasks.values())
        
        # Aplicar filtros
        filtered_tasks = []
        
        for task in all_tasks:
            # Filtrar por término de búsqueda (nombre o descripción)
            if search_term:
                search_in_name = search_term in task.name.lower()
                search_in_desc = task.description and search_term in task.description.lower()
                if not (search_in_name or search_in_desc):
                    continue
            
            # Filtrar por estado
            if hasattr(self, 'current_status_filter') and self.current_status_filter:
                status_matches = (
                    (self.current_status_filter == "Tareas Pendientes" and task.status == Status.PENDING) or
                    (self.current_status_filter == "En Curso" and task.status == Status.IN_PROGRESS) or
                    (self.current_status_filter == "Tareas Finalizadas" and task.status == Status.COMPLETED)
                )
                if not status_matches:
                    continue
            
            # Filtrar por prioridad
            if hasattr(self, 'current_priority_filter') and self.current_priority_filter:
                if not task.priority or task.priority.value != self.current_priority_filter:
                    continue
            
            # Filtrar por fecha
            if hasattr(self, 'start_date_var') and self.start_date_var.get():
                try:
                    start_date = datetime.strptime(self.start_date_var.get(), "%Y-%m-%d").date()
                    end_date = datetime.strptime(self.end_date_var.get(), "%Y-%m-%d").date() if self.end_date_var.get() else start_date
                    
                    # Usar el campo de fecha correcto (creación o actualización)
                    date_field = getattr(self, 'date_field', 'created_at')
                    task_date = getattr(task, date_field, None)
                    
                    if task_date:
                        task_date = task_date.date()
                        if not (start_date <= task_date <= end_date):
                            continue
                except (ValueError, AttributeError) as e:
                    # Si hay un error en el formato de fecha o el campo no existe, ignorar el filtro
                    print(f"Error al filtrar por fecha: {e}")
                    continue
            
            # Si pasa todos los filtros, agregar a la lista
            filtered_tasks.append(task)
        
        # Ordenar tareas
        if self.current_sort_column:
            reverse = not self.sort_ascending
            filtered_tasks.sort(
                key=lambda x: (
                    str(getattr(x, self.current_sort_column, "") or ""),
                    x.name  # Segundo criterio de ordenación
                ),
                reverse=reverse
            )
        
        return filtered_tasks
    
    def _load_tasks(self) -> None:
        """Carga las tareas desde el servicio y las muestra en la interfaz."""
        # Limpiar tareas existentes (excepto los encabezados)
        for widget in self.tasks_container.winfo_children():
            if widget != self.tasks_container.winfo_children()[0]:  # No eliminar los encabezados
                widget.destroy()
        
        # Obtener término de búsqueda actual
        search_term = self.search_var.get().strip() if hasattr(self, 'search_var') and self.search_var.get() else ""
        
        # Obtener tareas filtradas y ordenadas
        all_tasks = self._get_filtered_sorted_tasks()
        
        # Calcular paginación
        total_tasks = len(all_tasks)
        total_pages = max(1, (total_tasks + self.tasks_per_page - 1) // self.tasks_per_page)
        
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
            
            # Construir mensaje descriptivo
            message = "No hay tareas para mostrar"
            
            # Agregar información de filtros activos al mensaje
            active_filters = []
            
            if search_term:
                active_filters.append(f"búsqueda: '{search_term}'")
                
            if hasattr(self, 'current_status_filter') and self.current_status_filter:
                active_filters.append(f"estado: {self.current_status_filter}")
                
            if hasattr(self, 'current_priority_filter') and self.current_priority_filter:
                active_filters.append(f"prioridad: {self.current_priority_filter}")
                
            if hasattr(self, 'date_filter_var') and self.date_filter_var.get() != "Sin filtrar":
                date_filter = self.date_filter_var.get()
                if date_filter == "Personalizado" and hasattr(self, 'start_date_var'):
                    start_date = self.start_date_var.get()
                    end_date = self.end_date_var.get()
                    if start_date and end_date:
                        active_filters.append(f"fecha: {start_date} a {end_date}")
                else:
                    active_filters.append(f"fecha: {date_filter}")
            
            if active_filters:
                message = f"No hay tareas que coincidan con {', '.join(active_filters)}"
            
            no_tasks_label = ctk.CTkLabel(
                no_tasks_frame,
                text=message,
                font=ctk.CTkFont(size=14, slant="italic")
            )
            no_tasks_label.pack(pady=20)
        else:
            # Mostrar tareas de la página actual
            for task in tasks_to_show:
                self._create_task_widget(task)
        
        # Actualizar controles de paginación
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
            ("name", 6),          # Nombre - 50% del ancho
            ("priority", 1),      # Prioridad - 10% del ancho
            ("status", 2),        # Estado - 15% del ancho
            ("created_at", 2),    # Fecha de creación - 15% del ancho
            ("updated_at", 2),    # Fecha de actualización - 15% del ancho
            ("actions", 1)        # Acciones - 5% del ancho
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
        def format_datetime(dt):
            if not dt:
                return ""
            if isinstance(dt, str):
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    return dt
            return dt.strftime("%d/%m/%Y %H:%M")
            
        created_date = format_datetime(task.created_at)
        created_label = ctk.CTkLabel(task_frame, text=created_date)
        created_label.grid(row=0, column=3, padx=5, pady=5)
        
        # Fecha de última actualización
        updated_date = format_datetime(task.updated_at)
        updated_label = ctk.CTkLabel(task_frame, text=updated_date)
        updated_label.grid(row=0, column=4, padx=5, pady=5)
        
        # Frame para los botones de acción
        actions_frame = ctk.CTkFrame(task_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=5, padx=5, pady=5, sticky="e")
        
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
            btn.grid(row=i, column=0, padx=20, pady=2, sticky="ew")  # Reducido el pady de 5 a 2
            self.nav_buttons[view_name] = btn
            
        # Frame para el selector de tema - movido abajo
        theme_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        theme_frame.grid(row=9, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        # Título del selector de tema
        ctk.CTkLabel(
            theme_frame, 
            text="Tema:",
            text_color=("gray10", "gray90"),
            anchor="w"
        ).pack(side="left", padx=(0, 5))
        
        # Selector de tema
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
        theme_menu.pack(side="right")
        
        # Botón de salir - movido justo debajo del selector de tema
        exit_btn = ctk.CTkButton(
            self.sidebar,
            text="🚪 Salir",
            font=ctk.CTkFont(weight="bold"),
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=self.quit
        )
        exit_btn.grid(row=10, column=0, padx=20, pady=(0, 20), sticky="ew")
    
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
            
    def show_view(self, view_name: str, filter_status: Status = None) -> None:
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
        if view_name == "dashboard":
            self._show_dashboard_view()
        elif view_name == "tasks":
            self._show_tasks_view(filter_status)
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
        dialog.geometry("600x600")  # Tamaño inicial más compacto
        dialog.minsize(450, 350)  # Tamaño mínimo más pequeño
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
