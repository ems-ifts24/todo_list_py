"""
Módulo para el diálogo de creación y edición de tareas.
"""
import customtkinter as ctk
from typing import Optional

from ..models.task import Task, Priority, Status
from ..services.task_service import TaskService

class TaskDialog(ctk.CTkToplevel):
    """Diálogo para crear o editar una tarea."""

    def __init__(self, master, task_service: TaskService, on_save: callable, task: Optional[Task] = None):
        super().__init__(master)
        self.task_service = task_service
        self.on_save = on_save
        self.task = task

        self.title("Editar Tarea" if self.task else "Nueva Tarea")
        self.geometry("400x300")
        self.grab_set()

        self._create_widgets()

    def _create_widgets(self):
        """Crea los widgets del formulario."""
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Nombre
        ctk.CTkLabel(form_frame, text="Nombre:").pack(anchor="w")
        self.name_entry = ctk.CTkEntry(form_frame)
        if self.task:
            self.name_entry.insert(0, self.task.name)
        self.name_entry.pack(fill="x", pady=(0, 10))

        # Prioridad
        ctk.CTkLabel(form_frame, text="Prioridad:").pack(anchor="w")
        self.priority_var = ctk.StringVar(value=self.task.priority.value if self.task else Priority.MEDIUM.value)
        priority_menu = ctk.CTkOptionMenu(form_frame, values=[p.value for p in Priority], variable=self.priority_var)
        priority_menu.pack(fill="x", pady=(0, 10))

        # Estado
        ctk.CTkLabel(form_frame, text="Estado:").pack(anchor="w")
        self.status_var = ctk.StringVar(value=self.task.status.value if self.task else Status.PENDING.value)
        status_menu = ctk.CTkOptionMenu(form_frame, values=[s.value for s in Status], variable=self.status_var)
        status_menu.pack(fill="x", pady=(0, 20))

        # Botones
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(pady=10)

        ctk.CTkButton(buttons_frame, text="Guardar", command=self._save).pack(side="left", padx=10)
        ctk.CTkButton(buttons_frame, text="Cancelar", fg_color=("gray70", "gray30"), hover_color=("gray60", "gray40"), command=self.destroy).pack(side="left", padx=10)

    def _save(self):
        """Guarda la tarea (crea o actualiza)."""
        try:
            name = self.name_entry.get().strip()
            if not name:
                raise ValueError("El nombre no puede estar vacío")

            priority = Priority(self.priority_var.get())
            status = Status(self.status_var.get())

            if self.task:
                # Actualizar tarea existente
                self.task_service.update_task(
                    task_id=self.task.id,
                    name=name,
                    priority=priority,
                    status=status
                )
            else:
                # Crear nueva tarea
                self.task_service.create_task(
                    name=name,
                    priority=priority,
                    status=status
                )
            
            self.on_save()  # Llama al callback para refrescar la lista
            self.destroy()

        except Exception as e:
            # Aquí se podría mostrar un mensaje de error en el diálogo
            print(f"Error al guardar: {e}")
