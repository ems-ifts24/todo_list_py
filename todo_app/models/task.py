from datetime import datetime
from enum import Enum
from functools import total_ordering
from typing import Optional, Dict, Any


@total_ordering
class Priority(Enum):
    HIGH = "ALTA"
    MEDIUM = "MEDIA"
    LOW = "BAJA"

    @property
    def _sort_order(self):
        return {
            Priority.LOW: 0,
            Priority.MEDIUM: 1,
            Priority.HIGH: 2
        }.get(self, -1)

    def __lt__(self, other):
        if not isinstance(other, Priority):
            return NotImplemented
        return self._sort_order < other._sort_order

class Status(Enum):
    PENDING = "PENDIENTE"
    IN_PROGRESS = "EN CURSO"
    COMPLETED = "FINALIZADA"

class Task:
    def __init__(
        self,
        name: str,
        priority: Priority,
        status: Status = Status.PENDING,
        task_id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = task_id
        self.name = name
        self.priority = priority
        self.status = status
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or self.created_at

    def update(
        self,
        name: Optional[str] = None,
        priority: Optional[Priority] = None,
        status: Optional[Status] = None
    ) -> None:
        """Actualiza los campos de la tarea y valida las transiciones de estado."""
        if self.status == Status.COMPLETED:
            raise ValueError("No se puede modificar una tarea completada")

        if name is not None:
            self.name = name
        if priority is not None:
            self.priority = priority
        if status is not None:
            self._validate_status_transition(status)
            self.status = status

        self.updated_at = datetime.now()

    def _validate_status_transition(self, new_status: Status) -> None:
        """Valida si la transición de estado es permitida."""
        if self.status == Status.COMPLETED:
            raise ValueError("No se puede modificar una tarea completada")

        valid_transitions = {
            Status.PENDING: [Status.IN_PROGRESS, Status.COMPLETED],
            Status.IN_PROGRESS: [Status.COMPLETED, Status.PENDING],
        }

        if new_status not in valid_transitions.get(self.status, []):
            raise ValueError(
                f"Transición de estado inválida: {self.status.value} a {new_status.value}"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la tarea a un diccionario para la serialización JSON."""
        return {
            "id": self.id,
            "name": self.name,
            "priority": self.priority.value,
            "status": self.status.value,
            "created_at": self.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%dT%H:%M:%S")
        }

    # Decorador @classmethod se utiliza para definir un método de clase.
    # Los métodos de clase se llaman en la clase en lugar de en una instancia de la clase.
    # Son útiles para definir métodos que operan en la clase en lugar de en una instancia de la clase,
    # por ejemplo, para obtener una lista de todos los valores de la enumeración.
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Crea una instancia de Task a partir de un diccionario."""
        # Parsear fechas - compatible con ambos formatos (con y sin microsegundos)
        def parse_datetime(date_str: str) -> datetime:
            try:
                # Intentar parsear con el formato estándar ISO
                return datetime.fromisoformat(date_str)
            except ValueError:
                # Si falla, intentar sin microsegundos
                return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        
        return cls(
            task_id=data["id"],
            name=data["name"],
            priority=Priority(data["priority"]),
            status=Status(data["status"]),
            created_at=parse_datetime(data["created_at"]),
            updated_at=parse_datetime(data["updated_at"])
        )

    def __str__(self) -> str:
        # Método mágico __str__ se utiliza para definir cómo se representa una instancia como cadena de texto.
        # Se llama automáticamente cuando se usa str(objeto) o cuando se imprime el objeto.
        return f"{self.name} (id:{self.id})"

    def __eq__(self, other: object) -> bool:
        # Método mágico __eq__ se utiliza para definir el comportamiento del operador de igualdad (==).
        # Se llama automáticamente cuando se compara un objeto con otro usando el operador ==.
        if not isinstance(other, Task):
            return False
        return self.id == other.id
