import json
from typing import List, Optional, Dict
from pathlib import Path

from ..models.task import Task, Priority, Status


class TaskService:
    def __init__(self, data_dir: str = "data", data_file: str = "tareas.json"):
        """Inicializa el servicio de tareas con el directorio y archivo de datos.
        
        Args:
            data_dir: Directorio donde se guardarán los archivos de datos
            data_file: Nombre del archivo JSON para guardar las tareas
        """
        self.data_dir = Path(data_dir)
        self.data_file = self.data_dir / data_file
        self.tasks: Dict[int, Task] = {}
        self._ensure_data_dir_exists()
        self._load_tasks()
        self._next_id = max(self.tasks.keys(), default=0) + 1

    def _ensure_data_dir_exists(self) -> None:
        """Asegura que exista el directorio de datos."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if not self.data_file.exists():
            self.data_file.write_text("[]", encoding="utf-8")

    def _load_tasks(self) -> None:
        """Carga las tareas desde el archivo JSON."""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                tasks_data = json.load(f)
                self.tasks = {
                    task_data['id']: Task.from_dict(task_data)
                    for task_data in tasks_data
                }
        except (json.JSONDecodeError, FileNotFoundError):
            self.tasks = {}

    def _save_tasks(self) -> None:
        """Guarda las tareas en el archivo JSON."""
        tasks_data = [task.to_dict() for task in self.tasks.values()]
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(tasks_data, f, ensure_ascii=False, indent=2)

    def create_task(self, name: str, priority: Priority, status: Status = None) -> Task:
        """Crea una nueva tarea.
        
        Args:
            name: Nombre de la tarea (debe ser único a menos que la tarea existente esté completada)
            priority: Prioridad de la tarea
            status: Estado inicial (por defecto es PENDIENTE)
            
        Returns:
            La tarea creada
            
        Raises:
            ValueError: Si ya existe una tarea con el mismo nombre y no está completada
        """
        # Verificar si ya existe una tarea con el mismo nombre que no esté completada
        for task in self.tasks.values():
            if task.name.lower() == name.lower() and task.status != Status.COMPLETED:
                raise ValueError(f"Ya existe una tarea con el nombre '{name}' que no está completada")

        task = Task(
            name=name,
            priority=priority,
            status=status or Status.PENDING,
            task_id=self._next_id
        )
        
        self.tasks[task.id] = task
        self._next_id += 1
        self._save_tasks()
        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        """Obtiene una tarea por su ID.
        
        Args:
            task_id: ID de la tarea a recuperar
            
        Returns:
            La tarea si se encuentra, None en caso contrario
        """
        return self.tasks.get(task_id)

    def get_all_tasks(self, priority: Optional[Priority] = None) -> List[Task]:
        """Obtiene todas las tareas, opcionalmente filtradas por prioridad.
        
        Args:
            priority: Si se proporciona, solo devuelve tareas con esta prioridad
            
        Returns:
            Lista de tareas, ordenadas por nombre
        """
        tasks = list(self.tasks.values())
        if priority is not None:
            tasks = [t for t in tasks if t.priority == priority]
        return sorted(tasks, key=lambda t: t.name.lower())

    def update_task(
        self,
        task_id: int,
        name: Optional[str] = None,
        priority: Optional[Priority] = None,
        status: Optional[Status] = None
    ) -> Optional[Task]:
        """Actualiza una tarea existente.
        
        Args:
            task_id: ID de la tarea a actualizar
            name: Nuevo nombre para la tarea
            priority: Nueva prioridad para la tarea
            status: Nuevo estado para la tarea
            
        Returns:
            La tarea actualizada si se encuentra, None en caso contrario
            
        Raises:
            ValueError: Si ya existe otra tarea con el mismo nombre que no esté completada
        """
        task = self.tasks.get(task_id)
        if task is None:
            return None
            
        if name is not None and name != task.name:
            # Verificar si ya existe otra tarea con el mismo nombre que no esté completada
            for t in self.tasks.values():
                if t.id != task_id and t.name.lower() == name.lower() and t.status != Status.COMPLETED:
                    raise ValueError(f"Ya existe una tarea con el nombre '{name}' que no está completada")
            
        task.update(name=name, priority=priority, status=status)
        self._save_tasks()
        return task

    def delete_task(self, task_id: int) -> bool:
        """Elimina una tarea.
        
        Args:
            task_id: ID de la tarea a eliminar
            
        Returns:
            True si la tarea fue eliminada, False si no se encontró
        """
        if task_id in self.tasks:
            del self.tasks[task_id]
            self._save_tasks()
            return True
        return False

    def search_tasks(self, query: str) -> List[Task]:
        """Busca tareas por nombre (coincidencia parcial sin distinción de mayúsculas/minúsculas).
        
        Args:
            query: Término de búsqueda
            
        Returns:
            Lista de tareas que coinciden, ordenadas por nombre
        """
        query = query.lower()
        return sorted(
            [t for t in self.tasks.values() if query in t.name.lower()],
            key=lambda t: t.name.lower()
        )
