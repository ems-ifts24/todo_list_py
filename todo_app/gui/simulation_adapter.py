from pathlib import Path
from typing import List
from ..models.task import Task
from ..services.data_generator import DataGenerator

# --- Funciones para integración GUI ---

def simulate_tasks(count: int) -> str:
    """
    Genera N tareas simuladas y las guarda en el archivo correspondiente.
    Retorna la ruta del archivo generado/actualizado.
    """
    generator = DataGenerator()
    return generator.generate_simulated_tasks(count)


def get_last_simulated_file() -> str:
    """
    Devuelve la ruta del archivo de simulación más reciente, o None si no existe.
    """
    generator = DataGenerator()
    file = generator.get_latest_simulated_file()
    return str(file) if file else None


def read_simulated_tasks() -> List[Task]:
    """
    Lee el archivo de simulación más reciente y devuelve una lista de Task.
    """
    file_path = get_last_simulated_file()
    if not file_path or not Path(file_path).exists():
        return []
    import json
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    tasks = []
    for d in data:
        try:
            # Reutilizamos la lógica centralizada del modelo para evitar inconsistencias
            task = Task.from_dict(d)
            tasks.append(task)
        except Exception:
            continue
    return tasks
