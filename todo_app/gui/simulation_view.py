import customtkinter as ctk
from typing import Optional, Dict
from datetime import datetime
from ..models.task import Task, Priority, Status
from .simulation_adapter import simulate_tasks, get_last_simulated_file, read_simulated_tasks
import os
import tkinter as tk
from tkinter import simpledialog, messagebox

class SimulationView(ctk.CTkFrame):
    """
    Vista para mostrar y simular tareas desde el archivo de simulación.
    """
    def __init__(self, master, main_window):
        super().__init__(master, fg_color="transparent")
        self.main_window = main_window
        self.current_page = 1
        self.tasks_per_page = 8
        self.search_var = ctk.StringVar()
        self.tasks = []
        self.filtered_tasks = []
        self._create_widgets()
        self._load_tasks()

    def _create_widgets(self):
        title_label = ctk.CTkLabel(self, text=" Simulación de Tareas", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=(0, 10), anchor="w")

        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", pady=(0, 10))

        search_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        search_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))

        search_bar_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_bar_frame.pack(side="left", fill="x", expand=True)

        search_entry = ctk.CTkEntry(
            search_bar_frame,
            placeholder_text="Buscar tareas...",
            width=300,
            textvariable=self.search_var
        )
        search_entry.pack(side="left", padx=(0, 5))
        self.search_var.trace("w", lambda *args: self._filter_tasks())

        clear_btn = ctk.CTkButton(
            search_bar_frame,
            text="Limpiar",
            width=30,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            command=self._clear_search
        )
        clear_btn.pack(side="left")

        buttons_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        buttons_frame.pack(side="right")

        simulate_btn = ctk.CTkButton(
            buttons_frame,
            text=" Simular Datos",
            command=self._simulate_data,
            fg_color=("#5dade2", "#1f6aa5"),
            hover_color=("#54b4e6", "#1a5a94"),
            text_color=("white", "white")
        )
        simulate_btn.pack(side="left", padx=(0, 10))

        export_btn = ctk.CTkButton(
            buttons_frame,
            text=" Exportar a CSV",
            command=self._export_to_csv,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            text_color=("black", "white")
        )
        export_btn.pack(side="left")

        # Encabezados de la tabla
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(25, 5))
        self._create_table_headers()

        self.tasks_container = ctk.CTkFrame(self, fg_color="transparent")
        self.tasks_container.pack(fill="both", expand=True)

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

    def _clear_search(self):
        self.search_var.set("")
        self.current_page = 1
        self._filter_tasks()

    def _create_table_headers(self):
        for widget in self.header_frame.winfo_children():
            widget.destroy()

        columns = [
            ("Tarea", 0),
            ("Prioridad", 1),
            ("Estado", 2),
            ("Creada", 3),
            ("Actualizada", 4),
            ("Acciones", 5)
        ]

        for idx, (title, _) in enumerate(columns):
            self.header_frame.grid_columnconfigure(idx, weight=1, uniform="simulation_columns")
            header_label = ctk.CTkLabel(
                self.header_frame,
                text=title,
                font=ctk.CTkFont(weight="bold"),
                anchor="center"
            )
            header_label.grid(row=0, column=idx, padx=5, pady=2, sticky="nsew")

    def _filter_tasks(self, reset_page=True):
        term = self.search_var.get().lower()
        if term:
            self.filtered_tasks = [t for t in self.tasks if term in t.name.lower()]
        else:
            self.filtered_tasks = list(self.tasks)
        if reset_page:
            self.current_page = 1
        self._show_tasks()

    def _simulate_data(self):
        cantidad = simpledialog.askinteger("Simular Datos", "¿Cuántos registros desea generar?", parent=self)
        if cantidad and cantidad > 0:
            try:
                simulate_tasks(cantidad)
                messagebox.showinfo("Simulación exitosa", f"Se generaron {cantidad} tareas simuladas.")
                self.tasks = read_simulated_tasks()
                self.filtered_tasks = list(self.tasks)
                self.current_page = 1
                self._show_tasks()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo simular: {e}")

    def _export_to_csv(self):
        from tkinter import filedialog
        if not self.filtered_tasks:
            messagebox.showinfo("Exportar a CSV", "No hay tareas para exportar.", parent=self)
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
            initialfile=f"simuladas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            title="Guardar archivo CSV"
        )
        if filepath:
            import csv
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Tarea", "Prioridad", "Estado", "Creada", "Actualizada"])
                for t in self.filtered_tasks:
                    writer.writerow([
                        t.name,
                        t.priority.value if t.priority else "",
                        t.status.value if t.status else "",
                        t.created_at.strftime("%d-%m-%Y %H:%M:%S") if t.created_at else "",
                        t.updated_at.strftime("%d-%m-%Y %H:%M:%S") if t.updated_at else ""
                    ])
            messagebox.showinfo("Exportación exitosa", f"Tareas exportadas a {filepath}", parent=self)

    def _load_tasks(self):
        self.tasks = read_simulated_tasks()
        self._filter_tasks(reset_page=False)

    def _show_tasks(self):
        for widget in self.tasks_container.winfo_children():
            widget.destroy()
        total = len(self.filtered_tasks)
        total_pages = max(1, (total + self.tasks_per_page - 1) // self.tasks_per_page)
        if self.current_page > total_pages:
            self.current_page = total_pages
        start_idx = (self.current_page - 1) * self.tasks_per_page
        end_idx = start_idx + self.tasks_per_page
        tasks_to_show = self.filtered_tasks[start_idx:end_idx]
        if not tasks_to_show:
            label = ctk.CTkLabel(self.tasks_container, text="No hay tareas simuladas para mostrar.", font=ctk.CTkFont(size=14, slant="italic"))
            label.pack(pady=20)
        else:
            for task in tasks_to_show:
                self._create_task_widget(task)
        self._update_pagination_controls(total_pages)

    def _update_pagination_controls(self, total_pages):
        self.page_label.configure(text=f"Página {self.current_page} de {total_pages if total_pages > 0 else 1}")
        self.prev_btn.configure(state="disabled" if self.current_page <= 1 else "normal")
        self.next_btn.configure(state="disabled" if self.current_page >= total_pages else "normal")

    def _prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self._show_tasks()

    def _next_page(self):
        self.current_page += 1
        self._show_tasks()

    def _create_task_widget(self, task: Task):
        task_frame = ctk.CTkFrame(self.tasks_container, fg_color=("#f0f0f0", "#2b2b2b"))
        task_frame.pack(fill="x", pady=2, padx=5)
        columns = ["name", "priority", "status", "created_at", "updated_at", "actions"]
        for idx, _ in enumerate(columns):
            task_frame.columnconfigure(idx, weight=1, uniform="simulation_columns")
        name_label = ctk.CTkLabel(task_frame, text=task.name, anchor="w", font=ctk.CTkFont(weight="bold"))
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
                if isinstance(dt_obj, str):
                    dt_obj = datetime.fromisoformat(dt_obj.replace('Z', '+00:00'))
                return dt_obj.strftime("%d-%m-%Y %H:%M:%S")
            except (ValueError, TypeError):
                return str(dt_obj)
        created_label = ctk.CTkLabel(task_frame, text=format_datetime_str(task.created_at), anchor="center")
        created_label.grid(row=0, column=3, padx=5, pady=5, sticky="nsew")
        updated_label = ctk.CTkLabel(task_frame, text=format_datetime_str(task.updated_at), anchor="center")
        updated_label.grid(row=0, column=4, padx=5, pady=5, sticky="nsew")
        actions_frame = ctk.CTkFrame(task_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=5, padx=5, pady=5, sticky="nsew")
        actions_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="simulation_actions")
        disabled_text_color = ("#95a5a6", "#7f8c8d")
        disabled_bg_color = ("#f0f0f0", "#2b2b2b")
        disabled_hover_color = disabled_bg_color
        edit_btn = ctk.CTkButton(
            actions_frame,
            text="✏️",
            width=30,
            height=30,
            fg_color=disabled_bg_color,
            text_color=disabled_text_color,
            hover_color=disabled_hover_color,
            state="disabled"
        )
        edit_btn.grid(row=0, column=0, padx=2, pady=0, sticky="nsew")
        delete_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️",
            width=30,
            height=30,
            fg_color=disabled_bg_color,
            text_color=disabled_text_color,
            hover_color=disabled_hover_color,
            state="disabled"
        )
        delete_btn.grid(row=0, column=1, padx=2, pady=0, sticky="nsew")
        complete_btn = ctk.CTkButton(
            actions_frame,
            text="✓",
            width=30,
            height=30,
            fg_color=disabled_bg_color,
            text_color=disabled_text_color,
            hover_color=disabled_hover_color,
            state="disabled"
        )
        complete_btn.grid(row=0, column=2, padx=2, pady=0, sticky="nsew")
