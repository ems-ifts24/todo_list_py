from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class Priority(Enum):
    HIGH = "ALTA"
    MEDIUM = "MEDIA"
    LOW = "BAJA"

    # Decorador @classmethod se utiliza para definir un método de clase.
    # Los métodos de clase se llaman en la clase en lugar de en una instancia de la clase.
    # Son útiles para definir métodos que operan en la clase en lugar de en una instancia de la clase,
    # por ejemplo, para obtener una lista de todos los valores de la enumeración.
    @classmethod
    def from_int(cls, value: int) -> 'Priority':
        try:
            return list(cls)[value - 1]
        except IndexError:
            raise ValueError(f"Valor inválido para prioridad: {value}. Debe estar entre 1 y {len(cls)}.")

    @classmethod
    def get_choices(cls) -> str:
        return "\n".join(f"{i+1}. {priority.value}" for i, priority in enumerate(cls))


class Status(Enum):
    PENDING = "PENDIENTE"
    IN_PROGRESS = "EN CURSO"
    COMPLETED = "FINALIZADA"

    @classmethod
    def from_int(cls, value: int) -> 'Status':
        try:
            return list(cls)[value - 1]
        except IndexError:
            raise ValueError(f"Valor de estado inválido: {value}. Debe estar entre 1 y {len(cls)}.")

    @classmethod
    def get_choices(cls) -> str:
        return "\n".join(f"{i+1}. {status.value}" for i, status in enumerate(cls))


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
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Crea una instancia de Task a partir de un diccionario."""
        return cls(
            task_id=data["id"],
            name=data["name"],
            priority=Priority(data["priority"]),
            status=Status(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )

    def __str__(self) -> str:
        return f"{self.name} (id:{self.id})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Task):
            return False
        return self.id == other.id
