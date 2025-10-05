"""
Servicio para generar datos simulados de tareas.
Crea registros aleatorios con nombres únicos, prioridades y estados variados.
"""
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Set

from ..models.task import Priority, Status


class DataGenerator:
    """Generador de datos simulados para tareas."""
    
    # Lista base de nombres de tareas para combinar aleatoriamente
    TASK_PREFIXES = [
        "Revisar", "Actualizar", "Completar", "Enviar", "Preparar",
        "Organizar", "Planificar", "Desarrollar", "Implementar", "Testear",
        "Documentar", "Analizar", "Diseñar", "Optimizar", "Refactorizar",
        "Investigar", "Configurar", "Instalar", "Migrar", "Integrar",
        "Validar", "Verificar", "Corregir", "Mejorar", "Automatizar",
        "Crear", "Eliminar", "Modificar", "Sincronizar", "Exportar",
        "Importar", "Compilar", "Desplegar", "Monitorear", "Auditar",
        "Archivar", "Restaurar", "Respaldar", "Limpiar", "Ordenar"
    ]
    
    TASK_OBJECTS = [
        "informe", "presentación", "documento", "código", "base de datos",
        "servidor", "aplicación", "módulo", "componente", "interfaz",
        "API", "servicio", "función", "clase", "método",
        "archivo", "directorio", "repositorio", "branch", "commit",
        "prueba", "test", "validación", "reporte", "análisis",
        "diagrama", "esquema", "modelo", "prototipo", "mockup",
        "configuración", "script", "query", "procedimiento", "trigger",
        "vista", "tabla", "índice", "backup", "log",
        "certificado", "credencial", "token", "sesión", "cache"
    ]
    
    TASK_CONTEXTS = [
        "del proyecto", "del cliente", "de producción", "de desarrollo", "de testing",
        "del sistema", "de la aplicación", "del servidor", "de la base de datos", "del módulo",
        "de seguridad", "de rendimiento", "de calidad", "de integración", "de despliegue",
        "mensual", "semanal", "diario", "trimestral", "anual",
        "urgente", "prioritario", "pendiente", "en revisión", "crítico",
        "frontend", "backend", "fullstack", "mobile", "web",
        "v1.0", "v2.0", "beta", "alpha", "release",
        "Q1", "Q2", "Q3", "Q4", "2025"
    ]
    
    def __init__(self, data_dir: str = "data", real_data_file: str = "tareas.json"):
        """Inicializa el generador de datos.
        
        Args:
            data_dir: Directorio donde se guardan los archivos de datos
            real_data_file: Nombre del archivo JSON con las tareas reales
        """
        self.data_dir = Path(data_dir)
        self.real_data_file = self.data_dir / real_data_file
        self._ensure_data_dir_exists()
    
    def _ensure_data_dir_exists(self) -> None:
        """Asegura que exista el directorio de datos."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_existing_tasks(self, simulated_file: Path) -> tuple[List[Dict[str, Any]], Set[str], int]:
        """Carga las tareas existentes (reales y simuladas previas).
        
        Args:
            simulated_file: Ruta del archivo simulado
            
        Returns:
            Tupla con (lista de tareas, conjunto de nombres usados, próximo ID disponible)
        """
        all_tasks = []
        used_names = set()
        max_id = 0
        
        # Cargar tareas reales si existen
        if self.real_data_file.exists():
            try:
                with open(self.real_data_file, 'r', encoding='utf-8') as f:
                    real_tasks = json.load(f)
                    all_tasks.extend(real_tasks)
                    for task in real_tasks:
                        used_names.add(task['name'].lower())
                        max_id = max(max_id, task['id'])
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Cargar tareas simuladas previas si existen
        if simulated_file.exists():
            try:
                with open(simulated_file, 'r', encoding='utf-8') as f:
                    simulated_tasks = json.load(f)
                    # Solo agregar las que no sean duplicadas de las reales
                    for task in simulated_tasks:
                        if task['name'].lower() not in used_names:
                            all_tasks.append(task)
                        used_names.add(task['name'].lower())
                        max_id = max(max_id, task['id'])
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        return all_tasks, used_names, max_id
    
    def _generate_unique_task_name(self, used_names: Set[str]) -> str:
        """Genera un nombre único de tarea.
        
        Args:
            used_names: Conjunto de nombres ya utilizados (en minúsculas)
            
        Returns:
            Nombre único de tarea
        """
        max_attempts = 1000
        attempt = 0
        
        while attempt < max_attempts:
            # Combinar elementos aleatorios
            prefix = random.choice(self.TASK_PREFIXES)
            obj = random.choice(self.TASK_OBJECTS)
            context = random.choice(self.TASK_CONTEXTS)
            
            # Generar nombre base
            name = f"{prefix} {obj} {context}"
            
            # Verificar si es único
            if name.lower() not in used_names:
                return name
            
            # Si no es único, agregar un número
            counter = 1
            while f"{name} {counter}".lower() in used_names:
                counter += 1
            
            return f"{name} {counter}"
        
        # Fallback: usar timestamp si no se encuentra nombre único
        return f"Tarea {datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
    def _generate_random_date(self, start_date: datetime, end_date: datetime) -> datetime:
        """Genera una fecha aleatoria entre dos fechas.
        
        Args:
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango
            
        Returns:
            Fecha aleatoria dentro del rango
        """
        time_delta = end_date - start_date
        random_days = random.randint(0, time_delta.days)
        random_seconds = random.randint(0, 86400)  # Segundos en un día
        
        return start_date + timedelta(days=random_days, seconds=random_seconds)
    
    def generate_simulated_tasks(self, count: int = 100) -> str:
        """Genera N tareas simuladas y las guarda en un archivo.
        
        Args:
            count: Número de tareas a generar (default: 100)
            
        Returns:
            Ruta del archivo generado
        """
        # Nombre del archivo simulado con timestamp
        timestamp = datetime.now().strftime("%Y%m%d")
        simulated_file = self.data_dir / f"tareas_simuladas_{timestamp}.json"
        
        # Cargar tareas existentes
        all_tasks, used_names, next_id = self._load_existing_tasks(simulated_file)
        
        # Rango de fechas: 01/07/2025 hasta hoy
        start_date = datetime(2025, 7, 1)
        end_date = datetime.now()
        
        # Generar nuevas tareas
        new_tasks = []
        for _ in range(count):
            next_id += 1
            
            # Generar nombre único
            name = self._generate_unique_task_name(used_names)
            used_names.add(name.lower())
            
            # Asignar prioridad y estado aleatorios
            priority = random.choice(list(Priority)).value
            status = random.choice(list(Status)).value
            
            # Generar fechas aleatorias
            created_at = self._generate_random_date(start_date, end_date)
            # updated_at debe ser igual o posterior a created_at
            updated_at = self._generate_random_date(created_at, end_date)
            
            # Crear tarea
            task = {
                "id": next_id,
                "name": name,
                "priority": priority,
                "status": status,
                "created_at": created_at.isoformat(),
                "updated_at": updated_at.isoformat()
            }
            
            new_tasks.append(task)
        
        # Combinar todas las tareas
        all_tasks.extend(new_tasks)
        
        # Ordenar por ID
        all_tasks.sort(key=lambda x: x['id'])
        
        # Guardar en archivo
        with open(simulated_file, 'w', encoding='utf-8') as f:
            json.dump(all_tasks, f, ensure_ascii=False, indent=2)
        
        return str(simulated_file)
    
    def get_latest_simulated_file(self) -> Path | None:
        """Obtiene el archivo simulado más reciente.
        
        Returns:
            Ruta del archivo simulado más reciente, o None si no existe
        """
        simulated_files = list(self.data_dir.glob("tareas_simuladas_*.json"))
        
        if not simulated_files:
            return None
        
        # Ordenar por fecha de modificación (más reciente primero)
        simulated_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        return simulated_files[0]
