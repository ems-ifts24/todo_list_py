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

        search_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="Buscar tareas...",
            width=300,
            textvariable=self.search_var
        )
        search_entry.pack(side="left", padx=(0, 5))
        self.search_var.trace("w", lambda *args: self._filter_tasks())

        clear_btn = ctk.CTkButton(
            filter_frame,
            text="×",
            width=30,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            command=self._clear_search
        )
        clear_btn.pack(side="left")

        simulate_btn = ctk.CTkButton(
            filter_frame,
            text=" Simular Datos",
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            command=self._simulate_data
        )
        simulate_btn.pack(side="left", padx=(10, 10))

        export_btn = ctk.CTkButton(
            filter_frame,
            text=" Exportar a CSV",
            command=self._export_to_csv,
            fg_color=("#2ecc71", "#27ae60"),
            hover_color=("#27ae60", "#219653"),
            text_color=("white", "white")
        )
        export_btn.pack(side="left", padx=(0, 10))

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
        columns = [("name", 6), ("priority", 1), ("status", 2), ("created_at", 2), ("updated_at", 2), ("actions", 1)]
        for idx, (col_id, weight) in enumerate(columns):
            task_frame.columnconfigure(idx, weight=weight)
        name_label = ctk.CTkLabel(task_frame, text=task.name, anchor="w", font=ctk.CTkFont(weight="bold"))
        name_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        priority_colors = {Priority.HIGH: "#e74c3c", Priority.MEDIUM: "#f39c12", Priority.LOW: "#2ecc71"}
        priority_label = ctk.CTkLabel(task_frame, text=task.priority.value if task.priority else "", text_color=priority_colors.get(task.priority, "gray"))
        priority_label.grid(row=0, column=1, padx=5, pady=5)
        status_colors = {Status.PENDING: "#f39c12", Status.IN_PROGRESS: "#3498db", Status.COMPLETED: "#2ecc71"}
        status_label = ctk.CTkLabel(task_frame, text=task.status.value if task.status else "", text_color=status_colors.get(task.status, "gray"))
        status_label.grid(row=0, column=2, padx=5, pady=5)
        def format_datetime_str(dt_obj):
            if not dt_obj: return ""
            try:
                if isinstance(dt_obj, str):
                    dt_obj = datetime.fromisoformat(dt_obj.replace('Z', '+00:00'))
                return dt_obj.strftime("%d-%m-%Y %H:%M:%S")
            except (ValueError, TypeError):
                return str(dt_obj)
        created_label = ctk.CTkLabel(task_frame, text=format_datetime_str(task.created_at))
        created_label.grid(row=0, column=3, padx=5, pady=5)
        updated_label = ctk.CTkLabel(task_frame, text=format_datetime_str(task.updated_at))
        updated_label.grid(row=0, column=4, padx=5, pady=5)
        actions_frame = ctk.CTkFrame(task_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=5, padx=5, pady=5, sticky="e")
        edit_btn = ctk.CTkButton(actions_frame, text="✏️", width=30, height=30, fg_color="gray70", text_color="gray60", hover_color="gray80", state="disabled")
        edit_btn.pack(side="left", padx=2)
        delete_btn = ctk.CTkButton(actions_frame, text="🗑️", width=30, height=30, fg_color="gray70", text_color="gray60", hover_color="gray80", state="disabled")
        delete_btn.pack(side="left", padx=2)
        complete_btn = ctk.CTkButton(actions_frame, text="✓", width=30, height=30, fg_color="gray70", text_color="gray60", hover_color="gray80", state="disabled")
        complete_btn.pack(side="left", padx=2)
