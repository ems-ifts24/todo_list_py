import customtkinter as ctk
from typing import Dict, Callable, Any, Optional, List
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox

from ..models.task import Task, Priority, Status
from ..services.task_service import TaskService


class TasksView(ctk.CTkFrame):
    """
    Vista que muestra la lista de tareas con filtros, paginación y opciones de ordenamiento.
    """
    def __init__(self, master, task_service: TaskService, main_window, config_service):
        super().__init__(master, fg_color="transparent")
        self.task_service = task_service
        self.main_window = main_window
        self.config_service = config_service

        # Inicializar variables de estado
        self.current_status_filter = None
        self.current_priority_filter = None
        self.search_var = ctk.StringVar()
        self.date_filter = {
            'type': None,
            'start': None,
            'end': None
        }
        self.date_field = "created_at"
        self.current_sort_column = "updated_at"
        self.sort_ascending = True
        self.current_page = 1
        self.tasks_per_page = self.config_service.get("tasks_per_page")
        self.advanced_filters_visible = False

        # Colores personalizados para el botón de exportación
        self.export_btn_fg_color = ("gray70", "gray30")
        self.export_btn_hover_color = ("gray60", "gray40")
        self.export_btn_text_color = ("black", "white")

        self._create_widgets()

    def update_config(self):
        """Actualiza la configuración de la vista desde el ConfigService."""
        self.tasks_per_page = self.config_service.get("tasks_per_page")
        self.update_colors()
        self._load_tasks()  # Recargar las tareas para aplicar el paginado

    def update_colors(self):
        """Actualiza los colores de los widgets para que coincidan con el tema."""
        if hasattr(self, "export_btn"):
            self.export_btn.configure(
                fg_color=self.export_btn_fg_color,
                hover_color=self.export_btn_hover_color,
                text_color=self.export_btn_text_color
            )

    def _create_widgets(self):
        """Crea todos los widgets para la vista de tareas."""
        # Título
        title_label = ctk.CTkLabel(
            self,
            text=" Mis Tareas",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 10), anchor="w")

        # Frame para controles de filtrado
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", pady=(0, 10))

        # Filtro de búsqueda
        search_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        search_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Frame para la barra de búsqueda y botón de limpiar
        search_bar_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_bar_frame.pack(side="left", fill="x", expand=True)

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
            text="Limpiar",
            width=30,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            command=self._clear_search
        )
        clear_btn.pack(side="left")

        new_task_btn = ctk.CTkButton(
            search_frame,
            text=" Nueva Tarea",
            command=lambda: self.main_window._show_task_dialog(), # Llama al nuevo diálogo sin tarea
            fg_color=("#5dade2", "#1f6aa5"),
            hover_color=("#54b4e6", "#1a5a94"),
            text_color=("white", "white")
        )
        new_task_btn.pack(side="left", padx=(0, 10))

        # Botón para exportar a CSV
        self.export_btn = ctk.CTkButton(
            search_frame,
            text=" Exportar a CSV",
            command=self._export_to_csv,
            fg_color=self.export_btn_fg_color,
            hover_color=self.export_btn_hover_color,
            text_color=self.export_btn_text_color
        )
        self.export_btn.pack(side="left", padx=(0, 10))

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
        self.advanced_filters_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.advanced_filters_frame.pack(fill="x", pady=(0, 10))
        self.advanced_filters_visible = False

        # Controles de filtros avanzados
        self._setup_advanced_filters()

        # Crear encabezados de la tabla (fuera del área de scroll)
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(25, 5))
        self._create_table_headers()

        # Contenedor para la lista de tareas
        self.tasks_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.tasks_container.pack(fill="both", expand=True)

        # Controles de paginación
        self.pagination_outer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pagination_outer_frame.pack(fill="x", pady=(10, 0))

        self.pagination_frame = ctk.CTkFrame(self.pagination_outer_frame, fg_color="transparent")
        self.pagination_frame.pack(expand=True, pady=5)

        self.prev_btn = ctk.CTkButton(
            self.pagination_frame,
            text=" Anterior",
            command=self._prev_page,
            fg_color="transparent",
            hover_color=("gray70", "gray30"),
            state="disabled"
        )
        self.prev_btn.pack(side="left", padx=5)

        self.page_label = ctk.CTkLabel(self.pagination_frame, text="Página 1")
        self.page_label.pack(side="left", padx=5)

        self.next_btn = ctk.CTkButton(
            self.pagination_frame,
            text="Siguiente ",
            command=self._next_page,
            fg_color="transparent",
            hover_color=("gray70", "gray30")
        )
        self.next_btn.pack(side="left", padx=5)

        self._load_tasks()

    def set_status_filter(self, status: Optional[str]):
        """Establece un filtro de estado inicial."""
        self.current_status_filter = status
        if hasattr(self, 'status_var'):
            status_map_rev = {
                "Tareas Pendientes": "Tareas Pendientes",
                "En Curso": "En Curso",
                "Tareas Finalizadas": "Tareas Finalizadas"
            }
            self.status_var.set(status_map_rev.get(status, "Todas"))
        self._load_tasks()

    def _prev_page(self) -> None:
        if self.current_page > 1:
            self.current_page -= 1
            self._load_tasks()

    def _next_page(self) -> None:
        self.current_page += 1
        self._load_tasks()

    def _clear_search(self) -> None:
        self.search_var.set("")
        self.current_page = 1
        self._load_tasks()

    def _on_search_change(self, *args) -> None:
        self.current_page = 1
        self._load_tasks()

    def _create_table_headers(self) -> None:
        # Limpiar encabezados existentes para redibujar con el indicador de ordenamiento
        for widget in self.header_frame.winfo_children():
            widget.destroy()

        header_frame = self.header_frame
        columns = [
            ("name", "Tarea"),
            ("priority", "Prioridad"),
            ("status", "Estado"),
            ("created_at", "Creada"),
            ("updated_at", "Actualizada"),
            ("actions", "Acciones")
        ]
        for i, (col_id, col_name) in enumerate(columns):
            header_frame.grid_columnconfigure(i, weight=1, uniform="tasks_columns")
            col_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
            col_frame.grid(row=0, column=i, padx=2, pady=2, sticky="nsew")
            if col_id == "actions":
                header = ctk.CTkLabel(
                    col_frame,
                    text=col_name,
                    font=ctk.CTkFont(weight="bold"),
                    anchor="center"
                )
                header.pack(fill="both", expand=True)
            else:
                header = ctk.CTkButton(
                    col_frame,
                    text=f"{col_name} {'▲' if self.sort_ascending else '▼'}" if self.current_sort_column == col_id else col_name,
                    font=ctk.CTkFont(weight="bold"),
                    fg_color="transparent",
                    hover_color=("gray70", "gray30"),
                    text_color=("black", "white"),
                    anchor="center",
                    command=lambda c=col_id: self._sort_tasks(c)
                )
                header.pack(fill="both", expand=True)

    def _update_pagination_controls(self, total_pages: int) -> None:
        self.page_label.configure(text=f"Página {self.current_page} de {total_pages if total_pages > 0 else 1}")
        self.prev_btn.configure(state="disabled" if self.current_page <= 1 else "normal")
        self.next_btn.configure(state="disabled" if self.current_page >= total_pages else "normal")

    def _export_to_csv(self):
        try:
            tasks = self._get_filtered_sorted_tasks()
            if not tasks:
                messagebox.showinfo("Exportar a CSV", "No hay tareas para exportar.", parent=self)
                return
            filepath = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
                initialfile=f"tareas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                title="Guardar archivo CSV"
            )
            if filepath:
                self.main_window.export_service.export_to_csv(tasks, filepath)
                messagebox.showinfo("Exportación exitosa", f"Tareas exportadas a {filepath}", parent=self)
        except Exception as e:
            messagebox.showerror("Error al exportar", str(e), parent=self)

    def _setup_advanced_filters(self) -> None:
        status_frame = ctk.CTkFrame(self.advanced_filters_frame, fg_color="transparent")
        status_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(status_frame, text="Estado:").pack(side="left", padx=(0, 5))
        self.status_var = ctk.StringVar(value="Todas")
        statuses = ["Todas", "Tareas Pendientes", "En Curso", "Tareas Finalizadas"]
        for status in statuses:
            rb = ctk.CTkRadioButton(status_frame, text=status, variable=self.status_var, value=status, command=self._on_status_change)
            rb.pack(side="left", padx=5)

        priority_frame = ctk.CTkFrame(self.advanced_filters_frame, fg_color="transparent")
        priority_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(priority_frame, text="Prioridad:").pack(side="left", padx=(0, 5))
        self.priority_var = ctk.StringVar(value="Todas")
        priorities = ["Todas"] + [p.value for p in Priority]
        for priority in priorities:
            rb = ctk.CTkRadioButton(priority_frame, text=priority, variable=self.priority_var, value=priority, command=self._apply_filters)
            rb.pack(side="left", padx=5)

        date_frame = ctk.CTkFrame(self.advanced_filters_frame, fg_color="transparent")
        date_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(date_frame, text="Filtrar por fecha de:").pack(side="left", padx=(0, 5))
        self.date_type_var = ctk.StringVar(value="created_at")
        date_type_menu = ctk.CTkOptionMenu(date_frame, values=["Creación", "Actualización"], variable=ctk.StringVar(value="Creación"), command=lambda v: self._on_date_type_change(v))
        date_type_menu.pack(side="left", padx=5)
        date_options = ["Sin filtrar", "Hoy", "Esta semana", "Este mes", "Personalizado"]
        self.date_filter_var = ctk.StringVar(value="Sin filtrar")
        self.date_filter_menu = ctk.CTkOptionMenu(date_frame, values=date_options, variable=self.date_filter_var, command=self._on_date_filter_change)
        self.date_filter_menu.pack(side="left", padx=5)
        self.custom_date_frame = ctk.CTkFrame(date_frame, fg_color="transparent")
        self.start_date_var = ctk.StringVar()
        self.end_date_var = ctk.StringVar()
        ctk.CTkLabel(self.custom_date_frame, text="Desde:").pack(side="left")
        ctk.CTkEntry(self.custom_date_frame, textvariable=self.start_date_var, placeholder_text="AAAA-MM-DD", width=100).pack(side="left", padx=5)
        ctk.CTkLabel(self.custom_date_frame, text="Hasta:").pack(side="left")
        ctk.CTkEntry(self.custom_date_frame, textvariable=self.end_date_var, placeholder_text="AAAA-MM-DD", width=100).pack(side="left", padx=5)

        buttons_frame = ctk.CTkFrame(self.advanced_filters_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(5, 0))
        clear_btn = ctk.CTkButton(buttons_frame, text="Limpiar Filtros", command=self._clear_filters, fg_color=("gray70", "gray30"), hover_color=("gray60", "gray40"))
        clear_btn.pack(side="left", padx=5)
        apply_btn = ctk.CTkButton(buttons_frame, text="Aplicar Filtros", command=self._apply_filters, fg_color=("#2ecc71", "#27ae60"), hover_color=("#27ae60", "#219653"))
        apply_btn.pack(side="right")
        self.advanced_filters_frame.pack_forget()

    def _toggle_advanced_filters(self) -> None:
        if self.advanced_filters_visible:
            self.advanced_filters_frame.pack_forget()
            self.show_filters_btn.configure(text="Filtros Avanzados ▼")
        else:
            self.advanced_filters_frame.pack(fill="x", pady=(0, 10))
            self.show_filters_btn.configure(text="Ocultar Filtros ▲")
        self.advanced_filters_visible = not self.advanced_filters_visible

    def _on_status_change(self, *args) -> None:
        status_map = {"Todas": None, "Tareas Pendientes": "Tareas Pendientes", "En Curso": "En Curso", "Tareas Finalizadas": "Tareas Finalizadas"}
        self.current_status_filter = status_map.get(self.status_var.get())
        self._apply_filters()

    def _on_date_type_change(self, date_type: str) -> None:
        self.date_field = "created_at" if date_type == "Creación" else "updated_at"
        self._apply_filters()

    def _on_date_filter_change(self, selected_option: str) -> None:
        today = datetime.now().date()
        if selected_option == "Hoy":
            self.start_date_var.set(today.strftime("%Y-%m-%d"))
            self.end_date_var.set(today.strftime("%Y-%m-%d"))
            self.custom_date_frame.pack_forget()
        elif selected_option == "Esta semana":
            start = today - timedelta(days=today.weekday())
            self.start_date_var.set(start.strftime("%Y-%m-%d"))
            self.end_date_var.set(today.strftime("%Y-%m-%d"))
            self.custom_date_frame.pack_forget()
        elif selected_option == "Este mes":
            start = today.replace(day=1)
            self.start_date_var.set(start.strftime("%Y-%m-%d"))
            self.end_date_var.set(today.strftime("%Y-%m-%d"))
            self.custom_date_frame.pack_forget()
        elif selected_option == "Personalizado":
            self.custom_date_frame.pack(side="left", padx=5)
        else:
            self.start_date_var.set("")
            self.end_date_var.set("")
            self.custom_date_frame.pack_forget()
        self._apply_filters()

    def _apply_filters(self) -> None:
        priority = self.priority_var.get()
        self.current_priority_filter = priority if priority != "Todas" else None
        date_option = self.date_filter_var.get()
        if date_option == "Sin filtrar":
            self.start_date_var.set("")
            self.end_date_var.set("")
        self.current_page = 1
        self._load_tasks()

    def _clear_filters(self) -> None:
        if hasattr(self, 'search_var'): self.search_var.set("")
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
        if self.current_sort_column == column:
            self.sort_ascending = not self.sort_ascending
        else:
            self.current_sort_column = column
            self.sort_ascending = True
        self.current_page = 1
        self._load_tasks()

    def _get_filtered_sorted_tasks(self):
        search_term = self.search_var.get().lower() if hasattr(self, 'search_var') and self.search_var.get() else ""
        all_tasks = list(self.task_service.tasks.values())
        filtered_tasks = []
        for task in all_tasks:
            if search_term and not (search_term in task.name.lower()):
                continue
            if self.current_status_filter:
                status_map = {"Tareas Pendientes": Status.PENDING, "En Curso": Status.IN_PROGRESS, "Tareas Finalizadas": Status.COMPLETED}
                if task.status != status_map.get(self.current_status_filter):
                    continue
            if self.current_priority_filter and (not task.priority or task.priority.value != self.current_priority_filter):
                continue
            if self.start_date_var.get():
                try:
                    start_date = datetime.strptime(self.start_date_var.get(), "%Y-%m-%d").date()
                    end_date = datetime.strptime(self.end_date_var.get(), "%Y-%m-%d").date() if self.end_date_var.get() else start_date
                    task_date = getattr(task, self.date_field, None)
                    if task_date and not (start_date <= task_date.date() <= end_date):
                        continue
                except (ValueError, AttributeError):
                    continue
            filtered_tasks.append(task)
        if self.current_sort_column:
            filtered_tasks.sort(
                key=lambda x: (getattr(x, self.current_sort_column, "") or "", x.name),
                reverse=not self.sort_ascending
            )
        return filtered_tasks

    def _load_tasks(self) -> None:
        """Inicia la carga asíncrona de tareas."""
        # Llamar al método asíncrono del servicio, que se encargará de la UI
        self.task_service.load_tasks_async(self._populate_tasks)

    def _populate_tasks(self, tasks: Dict[int, Task]) -> None:
        """Puebla la vista con las tareas cargadas. Se ejecuta como callback."""
        def update_ui():
            # 1. Limpiar el contenedor de tareas de forma segura
            for widget in self.tasks_container.winfo_children():
                widget.destroy()

            # 2. Redibujar los encabezados para actualizar el indicador de ordenamiento
            self._create_table_headers()

            # 3. Obtener y mostrar las tareas
            all_filtered_tasks = self._get_filtered_sorted_tasks()
            total_tasks = len(all_filtered_tasks)
            total_pages = max(1, (total_tasks + self.tasks_per_page - 1) // self.tasks_per_page)

            if self.current_page > total_pages:
                self.current_page = total_pages

            start_idx = (self.current_page - 1) * self.tasks_per_page
            end_idx = start_idx + self.tasks_per_page
            tasks_to_show = all_filtered_tasks[start_idx:end_idx]

            if not tasks_to_show:
                no_tasks_label = ctk.CTkLabel(self.tasks_container, text="No hay tareas para mostrar con los filtros actuales.", font=ctk.CTkFont(size=14, slant="italic"))
                no_tasks_label.pack(pady=20)
            else:
                for task in tasks_to_show:
                    self._create_task_widget(task)
            
            self._update_pagination_controls(total_pages)

        # Asegurarse de que la actualización de la UI se ejecute en el hilo principal
        self.main_window.after(0, update_ui)

    def _create_task_widget(self, task: Task) -> None:
        is_completed = task.status == Status.COMPLETED
        task_frame = ctk.CTkFrame(self.tasks_container, fg_color=("#f0f0f0", "#2b2b2b"))
        task_frame.pack(fill="x", pady=2, padx=5)
        columns = ["name", "priority", "status", "created_at", "updated_at", "actions"]
        for idx, _ in enumerate(columns):
            task_frame.columnconfigure(idx, weight=1, uniform="tasks_columns")
        name_label = ctk.CTkLabel(task_frame, text=task.name, anchor="w", font=ctk.CTkFont(weight="bold", overstrike=is_completed))
        name_label.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        priority_colors = {Priority.HIGH: "#e74c3c", Priority.MEDIUM: "#f39c12", Priority.LOW: "#2ecc71"}
        priority_label = ctk.CTkLabel(task_frame, text=task.priority.value if task.priority else "", text_color=priority_colors.get(task.priority, "gray"), anchor="center")
        priority_label.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        status_colors = {Status.PENDING: "#f39c12", Status.IN_PROGRESS: "#3498db", Status.COMPLETED: "#2ecc71"}
        status_label = ctk.CTkLabel(task_frame, text=task.status.value if task.status else "", text_color=status_colors.get(task.status, "gray"), anchor="center")
        status_label.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        def format_datetime_str(dt_obj):
            if not dt_obj: return ""
            try:
                # Si es una cadena, conviértela a datetime
                if isinstance(dt_obj, str):
                    dt_obj = datetime.fromisoformat(dt_obj.replace('Z', '+00:00'))
                return dt_obj.strftime("%d/%m/%Y %H:%M")
            except (ValueError, TypeError):
                return str(dt_obj)  # Devuelve el objeto original si falla el formateo
        created_label = ctk.CTkLabel(task_frame, text=format_datetime_str(task.created_at), anchor="center")
        created_label.grid(row=0, column=3, padx=5, pady=5, sticky="nsew")
        updated_label = ctk.CTkLabel(task_frame, text=format_datetime_str(task.updated_at), anchor="center")
        updated_label.grid(row=0, column=4, padx=5, pady=5, sticky="nsew")

        actions_frame = ctk.CTkFrame(task_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=5, padx=5, pady=5, sticky="nsew")
        actions_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="actions_buttons")

        edit_btn = ctk.CTkButton(actions_frame, text="✏️", width=30, height=30, fg_color="transparent", text_color=("#3498db", "#2980b9"), hover_color=("#d6eaf8", "#1a5276"), command=lambda t=task: self.main_window._show_task_dialog(t) if not is_completed else None, state="normal" if not is_completed else "disabled")
        edit_btn.grid(row=0, column=0, padx=2, pady=0, sticky="nsew")

        delete_btn = ctk.CTkButton(actions_frame, text="🗑️", width=30, height=30, fg_color="transparent", text_color=("#e74c3c", "#c0392b"), hover_color=("#f5b7b1", "#78281F"), command=lambda t=task: self._confirm_delete_task(t) if not is_completed else None, state="normal" if not is_completed else "disabled")
        delete_btn.grid(row=0, column=1, padx=2, pady=0, sticky="nsew")

        if is_completed:
            complete_btn = ctk.CTkButton(
                actions_frame,
                text="✓",
                width=30,
                height=30,
                fg_color=("#f0f0f0", "#2b2b2b"),
                text_color=("#95a5a6", "#7f8c8d"),
                hover_color=("#f0f0f0", "#2b2b2b"),
                state="disabled"
            )
        else:
            complete_btn = ctk.CTkButton(
                actions_frame,
                text="✓",
                width=30,
                height=30,
                fg_color="transparent",
                text_color=("#2ecc71", "#27ae60"),
                hover_color=("#d0f5e2", "#1a5276"),
                command=lambda t=task: self._confirm_complete_task(t, False)
            )
        complete_btn.grid(row=0, column=2, padx=2, pady=0, sticky="nsew")

    def _confirm_delete_task(self, task: Task) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirmar Eliminación")
        dialog.geometry("400x150")
        dialog.grab_set()
        ctk.CTkLabel(dialog, text=f"¿Seguro que quieres eliminar la tarea '{task.name}'?").pack(pady=20)
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Eliminar", command=lambda: (self.task_service.delete_task(task.id), self._load_tasks(), dialog.destroy()), fg_color="#e74c3c", hover_color="#c0392b").pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancelar", command=dialog.destroy).pack(side="left", padx=10)

    def _confirm_complete_task(self, task: Task, is_reopen: bool) -> None:
        action_text = "reabrir" if is_reopen else "completar"
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Confirmar {action_text.capitalize()}")
        dialog.geometry("400x150")
        dialog.grab_set()
        ctk.CTkLabel(dialog, text=f"¿Seguro que quieres {action_text} la tarea '{task.name}'?").pack(pady=20)
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text=action_text.capitalize(), command=lambda: (self.task_service.update_task(task_id=task.id, status=Status.PENDING if is_reopen else Status.COMPLETED), self._load_tasks(), dialog.destroy())).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancelar", command=dialog.destroy).pack(side="left", padx=10)
