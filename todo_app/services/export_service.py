import csv
from datetime import datetime
from pathlib import Path
from typing import List

from ..models.task import Task
from ..utils.ui_utils import ConsoleUI


class ExportService:
    """Servicio para exportar tareas a diferentes formatos."""
    
    def __init__(self, export_dir: str = "exports"):
        """Inicializa el servicio de exportación.
        
        Args:
            export_dir: Directorio donde se guardarán los archivos exportados
        """
        self.export_dir = Path(export_dir)
        self._ensure_export_dir_exists()
    
    def _ensure_export_dir_exists(self) -> None:
        """Asegura que exista el directorio de exportación."""
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_export_filename(self, extension: str = "csv") -> str:
        """Genera un nombre de archivo con la marca de tiempo actual.
        
        Args:
            extension: Extensión del archivo (sin el punto)
            
        Returns:
            Nombre de archivo generado en formato: yyyyMMdd_HHmmss_lista_tareas.{extension}
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{timestamp}_lista_tareas.{extension}"
    
    def export_to_csv(self, tasks: List[Task]) -> str:
        """Exporta las tareas a un archivo CSV.
        
        Args:
            tasks: Lista de tareas a exportar
            
        Returns:
            Ruta al archivo CSV generado
            
        Raises:
            IOError: Si hay un error al escribir el archivo
        """
        if not tasks:
            raise ValueError("No hay tareas para exportar")
        
        # Definir encabezados y mapeo de campos del CSV
        fieldnames = ["ID", "NOMBRE", "PRIORIDAD", "ESTADO", "FECHA_CREACION", "ULTIMA_MODIFICACION"]
        
        # Generar nombre de archivo de salida
        filename = self._generate_export_filename("csv")
        filepath = self.export_dir / filename
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for task in tasks:
                    writer.writerow({
                        "ID": task.id,
                        "NOMBRE": task.name,
                        "PRIORIDAD": task.priority.value,
                        "ESTADO": task.status.value,
                        "FECHA_CREACION": task.created_at.isoformat(),
                        "ULTIMA_MODIFICACION": task.updated_at.isoformat()
                    })
            
            return str(filepath.absolute())
            
        except IOError as e:
            error_msg = f"Error al exportar a CSV: {str(e)}"
            ConsoleUI.print_error(error_msg)
            raise IOError(error_msg) from e
    
    def export_tasks_interactive(self, tasks: List[Task]) -> bool:
        """Exportación interactiva de tareas a CSV.
        
        Args:
            tasks: Lista de tareas a exportar
            
        Returns:
            True si la exportación fue exitosa, False de lo contrario
            True if export was successful, False otherwise
        """
        if not tasks:
            ConsoleUI.print_warning("No tasks to export.")
            return False
            
        ConsoleUI.print_highlight(f"\nPreparing to export {len(tasks)} tasks to CSV...")
        
        try:
            filepath = self.export_to_csv(tasks)
            ConsoleUI.print_success(f"Successfully exported {len(tasks)} tasks to:\n{filepath}")
            return True
            
        except Exception as e:
            ConsoleUI.print_error(f"Failed to export tasks: {str(e)}")
            return False
