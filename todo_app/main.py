#!/usr/bin/env python3
"""
TODO_List Application
Aplicación de gestión de tareas con persistencia y exportación de datos.
"""
import sys  # Importado para agregar el directorio raíz al PATH
import os   # Importado para obtener la ruta del directorio raíz
from typing import Optional, List, Any
# Importado para tipado de datos
# Opcional: mejora el manejo de valores nulos. Indicando que la variable "puede" ser de un tipo de dato o ser nula.
# List: lista de datos.
# Any: variable que puede ser de cualquier tipo de dato.
# Por ejemplo, se puede definir la firma de la función como `def get_tasks() -> List[Task]` indicando que la función retorna una lista de objetos `Task`.
# Esto ayuda a Python a detectar posibles errores en tiempo de compilación y a ofrecer sugerencias de autocompletado en el editor de código.

from colorama import init as init_colorama, Style
# Importa la función `init` y `Style` de la biblioteca `colorama` para su inicialización.
# Esta biblioteca permite agregar colores y estilos a la salida de la consola en Python. Como mensajes de error, advertencias y información.

init_colorama()  # Inicializa colorama

# Agrega el directorio raíz del proyecto al PATH de Python,
# para que Python pueda encontrar los módulos definidos en el directorio raíz.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from todo_app.models.task import Task, Priority, Status  # Para poder usar los métodos en cada una de las clase
from todo_app.services.task_service import TaskService  # Para usar los métodos de la clase TaskService
from todo_app.services.export_service import ExportService  # Para exportar datos a CSV
from todo_app.utils.ui_utils import ConsoleUI, TablePrinter, TextColor  # Permite mostrar mensajes en consola con colores y estilos


class TodoApp:
    """Clase principal de la aplicación."""
    
    def __init__(self):
        """Inicializa la aplicación."""
        self.task_service = TaskService()
        self.export_service = ExportService()
        self.running = True
        
        # Menu options mapping
        self.menu_options = {
            "1": ("📝 Crear tarea", self.create_task),
            "2": ("📋 Listar tareas", self.list_tasks),
            "3": ("🔍 Buscar tarea por nombre", self.search_tasks),
            "4": ("✏️  Actualizar tarea", self.update_task),
            "5": ("🗑️  Eliminar tarea", self.delete_task),
            "6": ("💾 Exportar datos a CSV", self.export_tasks),
            "7": ("❌ Salir", self.exit_app)
        }
    
    def run(self) -> None:
        """Ejecuta el bucle principal de la aplicación."""
        try:
            while self.running:
                self._show_main_menu()
                self._handle_menu_selection()
        except KeyboardInterrupt:
            self._handle_shutdown()
        except Exception as e:
            ConsoleUI.print_error(f"An unexpected error occurred: {str(e)}")
            self._handle_shutdown()
    
    def _show_main_menu(self) -> None:
        """Muestra el menu principal."""
        ConsoleUI.clear_screen()
        ConsoleUI.print_header("📋 GESTOR DE TAREAS")
        
        # Display menu options
        for key, (label, _) in self.menu_options.items():
            print(f"{TextColor.INFO.value}{key}.{Style.RESET_ALL} {label}")
        
        # Display task count summary
        tasks = self.task_service.get_all_tasks()
        pending = len([t for t in tasks if t.status == Status.PENDING])
        in_progress = len([t for t in tasks if t.status == Status.IN_PROGRESS])
        completed = len([t for t in tasks if t.status == Status.COMPLETED])
        
        print(f"\n📊 Resumen: {TextColor.INFO.value}{pending} pendientes{Style.RESET_ALL}, "
              f"{TextColor.WARNING.value}{in_progress} en curso{Style.RESET_ALL}, "
              f"{TextColor.SUCCESS.value}{completed} completadas{Style.RESET_ALL}")
    
    def _handle_menu_selection(self) -> None:
        """Maneja la selección del usuario."""
        choice = input("\nSeleccione una opción: ").strip()
        
        if choice in self.menu_options:
            _, action = self.menu_options[choice]
            action()
        else:
            ConsoleUI.print_error("Opción inválida. Por favor, intente de nuevo.")
            input("\nPresione Enter para continuar...")
    
    def create_task(self) -> None:
        """Crea una nueva tarea."""
        ConsoleUI.clear_screen()
        ConsoleUI.print_header("➕ CREAR NUEVA TAREA")
        
        try:
            # Get task name
            while True:
                name = ConsoleUI.input_with_prompt("Nombre de la tarea")
                if name.strip():
                    break
                ConsoleUI.print_warning("El nombre de la tarea no puede estar vacío.")
            
            # Get priority
            ConsoleUI.print_highlight("\nSeleccione la prioridad:")
            for i, priority in enumerate(Priority, 1):
                print(f"{i}. {priority.value}")
            
            priority = self._get_valid_enum_choice(Priority, "prioridad")
            if priority is None:
                return
            
            # Crea la tarea
            task = self.task_service.create_task(name, priority)
            ConsoleUI.print_success(f"\n✅ Tarea creada exitosamente: {task}")
            
        except ValueError as e:
            ConsoleUI.print_error(f"Error al crear la tarea: {str(e)}")
        
        input("\nPresione Enter para continuar...")
    
    def list_tasks(self, tasks: Optional[List[Task]] = None, title: str = "📋 LISTA DE TAREAS") -> None:
        """Muestra una lista de tareas con paginación.
        
        Args:
            tasks: Lista de tareas a mostrar. Si None, se mostrarán todas las tareas.
            title: Título a mostrar encima de la lista de tareas.
        """
        if tasks is None:
            tasks = self.task_service.get_all_tasks()
        
        if not tasks:
            ConsoleUI.print_info("No hay tareas para mostrar.")
            input("\nPresione Enter para continuar...")
            return
        
        # Prepara los datos de la tabla
        headers = ["ID", "NOMBRE", "PRIORIDAD", "ESTADO", "ÚLTIMA MODIFICACIÓN"]
        table_data = []
        
        for task in tasks:
            # Codifica la prioridad
            if task.priority == Priority.HIGH:
                priority_display = f"{TextColor.ERROR.value}{task.priority.value}{Style.RESET_ALL}"
            elif task.priority == Priority.MEDIUM:
                priority_display = f"{TextColor.WARNING.value}{task.priority.value}{Style.RESET_ALL}"
            else:
                priority_display = f"{TextColor.SUCCESS.value}{task.priority.value}{Style.RESET_ALL}"
            
            # Codifica el estado
            if task.status == Status.COMPLETED:
                status_display = f"{TextColor.SUCCESS.value}{task.status.value}{Style.RESET_ALL}"
            elif task.status == Status.IN_PROGRESS:
                status_display = f"{TextColor.INFO.value}{task.status.value}{Style.RESET_ALL}"
            else:
                status_display = task.status.value
            
            table_data.append([
                task.id,
                task.name,
                priority_display,
                status_display,
                task.updated_at.strftime("%d-%m-%Y %H:%M")
                # task.updated_at.strftime("%Y-%m-%d %H:%M")
            ])
        
        # Muestra la tabla con paginación
        table = TablePrinter(headers, table_data, rows_per_page=10)
        table.display()
    
    def search_tasks(self) -> None:
        """Busca tareas por nombre."""
        ConsoleUI.clear_screen()
        ConsoleUI.print_header("🔍 BUSCAR TAREAS")
        
        query = ConsoleUI.input_with_prompt("Ingrese el nombre o parte del nombre a buscar")
        if not query.strip():
            ConsoleUI.print_warning("No se ingresó ningún término de búsqueda.")
            input("\nPresione Enter para continuar...")
            return
        
        tasks = self.task_service.search_tasks(query)
        self.list_tasks(tasks, f"🔍 RESULTADOS DE BÚSQUEDA: '{query}'")
    
    def update_task(self) -> None:
        """Actualiza una tarea existente."""
        ConsoleUI.clear_screen()
        ConsoleUI.print_header("✏️  ACTUALIZAR TAREA")
        
        # Obtiene todas las tareas
        tasks = self.task_service.get_all_tasks()
        if not tasks:
            ConsoleUI.print_info("No hay tareas para actualizar.")
            input("\nPresione Enter para continuar...")
            return
        
        # Permite al usuario seleccionar una tarea para actualizar
        task = self._select_task("Seleccione la tarea a actualizar", tasks)
        if not task:
            return
        
        while True:
            ConsoleUI.clear_screen()
            ConsoleUI.print_header(f"✏️  EDITANDO TAREA: {task.name}")
            
            # Muestra los detalles de la tarea actual
            print(f"1. Nombre: {task.name}")
            print(f"2. Prioridad: {task.priority.value}")
            print(f"3. Estado: {task.status.value}")
            print("\n0. Volver al menú principal")
            
            # Obtiene el campo a actualizar
            choice = input("\nSeleccione el campo a modificar (1-3) o 0 para volver: ").strip()
            
            try:
                if choice == "0":
                    return
                elif choice == "1":
                    # Actualiza el nombre
                    new_name = ConsoleUI.input_with_prompt("Nuevo nombre", task.name)
                    if new_name and new_name != task.name:
                        self.task_service.update_task(task.id, name=new_name)
                        task = self.task_service.get_task(task.id)
                        ConsoleUI.print_success("✅ Nombre actualizado correctamente.")
                elif choice == "2":
                    # Actualiza la prioridad
                    ConsoleUI.print_highlight("\nSeleccione la nueva prioridad:")
                    for i, priority in enumerate(Priority, 1):
                        print(f"{i}. {priority.value}")
                    
                    new_priority = self._get_valid_enum_choice(Priority, "prioridad")
                    if new_priority:
                        self.task_service.update_task(task.id, priority=new_priority)
                        task = self.task_service.get_task(task.id)
                        ConsoleUI.print_success("✅ Prioridad actualizada correctamente.")
                elif choice == "3":
                    # Actualiza el estado
                    ConsoleUI.print_highlight("\nSeleccione el nuevo estado:")
                    for i, status in enumerate(Status, 1):
                        print(f"{i}. {status.value}")
                    
                    new_status = self._get_valid_enum_choice(Status, "estado")
                    if new_status:
                        try:
                            self.task_service.update_task(task.id, status=new_status)
                            task = self.task_service.get_task(task.id)
                            ConsoleUI.print_success("✅ Estado actualizado correctamente.")
                        except ValueError as e:
                            ConsoleUI.print_error(f"Error al actualizar el estado: {str(e)}")
                else:
                    ConsoleUI.print_error("Opción inválida. Por favor, intente de nuevo.")
                    continue
                
                input("\nPresione Enter para continuar...")
                
            except Exception as e:
                ConsoleUI.print_error(f"Error al actualizar la tarea: {str(e)}")
                input("\nPresione Enter para continuar...")
    
    def delete_task(self) -> None:
        """Elimina una tarea."""
        ConsoleUI.clear_screen()
        ConsoleUI.print_header("🗑️  ELIMINAR TAREA")
        
        # Obtiene todas las tareas
        tasks = self.task_service.get_all_tasks()
        if not tasks:
            ConsoleUI.print_info("No hay tareas para eliminar.")
            input("\nPresione Enter para continuar...")
            return
        
        # Permite al usuario seleccionar una tarea para eliminar
        task = self._select_task("Seleccione la tarea a eliminar", tasks)
        if not task:
            return
        
        # Confirma la eliminación
        if ConsoleUI.confirm(f"¿Está seguro que desea eliminar la tarea '{task.name}'?", False):
            if self.task_service.delete_task(task.id):
                ConsoleUI.print_success("✅ Tarea eliminada correctamente.")
            else:
                ConsoleUI.print_error("No se pudo eliminar la tarea.")
        else:
            ConsoleUI.print_info("Operación cancelada.")
        
        input("\nPresione Enter para continuar...")
    
    def export_tasks(self) -> None:
        """Exporta las tareas a CSV."""
        ConsoleUI.clear_screen()
        ConsoleUI.print_header("💾 EXPORTAR TAREAS A CSV")
        
        # Obtiene todas las tareas
        tasks = self.task_service.get_all_tasks()
        if not tasks:
            ConsoleUI.print_info("No hay tareas para exportar.")
            input("\nPresione Enter para continuar...")
            return
        
        # Pide el filtro
        ConsoleUI.print_highlight("\nFiltrar por prioridad (opcional):")
        print("1. Alta")
        print("2. Media")
        print("3. Baja")
        print("0. Todas las prioridades")
        
        priority_choice = input("\nSeleccione una opción (0-3): ").strip()
        
        filtered_tasks = tasks
        if priority_choice in ["1", "2", "3"]:
            priority = list(Priority)[int(priority_choice) - 1]
            filtered_tasks = [t for t in tasks if t.priority == priority]
            ConsoleUI.print_info(f"Mostrando {len(filtered_tasks)} tareas con prioridad {priority.value}.")
        
        # Exporta las tareas
        if ConsoleUI.confirm(f"\n¿Desea exportar {len(filtered_tasks)} tareas a un archivo CSV?"):
            self.export_service.export_tasks_interactive(filtered_tasks)
        
        input("\nPresione Enter para continuar...")
    
    def exit_app(self) -> None:
        """Cierra la aplicación."""
        if ConsoleUI.confirm("¿Está seguro que desea salir?"):
            ConsoleUI.print_info("¡Hasta pronto! 👋")
            self.running = False
    
    def _select_task(self, prompt: str, tasks: List[Task]) -> Optional[Task]:
        """Helper para seleccionar una tarea de una lista.
        
        Args:
            prompt: Mensaje a mostrar al usuario
            tasks: Lista de tareas entre las que elegir
            
        Returns:
            La tarea seleccionada, o None si el usuario cancela
        """
        if not tasks:
            return None
            
        while True:
            ConsoleUI.clear_screen()
            ConsoleUI.print_header(prompt)
            
            # Mostrar tareas en formato de tabla
            self.list_tasks(tasks, "Seleccione una tarea")
            
            # Obtener entrada del usuario
            task_id = input("\nIngrese el ID de la tarea (o 'm' para volver al menú): ").strip().lower()
            
            if task_id == 'm':
                return None
                
            if task_id.isdigit():
                task_id_int = int(task_id)
                for task in tasks:
                    if task.id == task_id_int:
                        return task
                print(f"\n❌ No se encontró ninguna tarea con el ID {task_id_int}")
            else:
                print("\n❌ Por favor ingrese un ID numérico o 'm' para volver al menú")
            
            input("\nPresione Enter para continuar...")
    
    @staticmethod
    def _get_valid_enum_choice(enum_type, field_name: str) -> Any:
        """Obtiene un valor válido de enum del usuario.
        
        Args:
            enum_type: El tipo de enum para obtener un valor
            field_name: Nombre del campo (para mensajes de error)
            
        Returns:
            The selected enum value, or None if the user cancels
        """
        while True:
            choice = input(f"\nSeleccione {field_name} (1-{len(enum_type)}): ").strip()
            
            if not choice:
                return None
                
            if choice.isdigit() and 1 <= int(choice) <= len(enum_type):
                return list(enum_type)[int(choice) - 1]
                
            ConsoleUI.print_error(f"Por favor ingrese un número entre 1 y {len(enum_type)}.")
    
    def _handle_shutdown(self) -> None:
        """Maneja el cierre de la aplicación."""
        ConsoleUI.print_info("\nSaliendo de la aplicación...")
        self.running = False


def main():
    """Punto de entrada de la aplicación."""
    try:
        app = TodoApp()
        app.run()
    except Exception as e:
        ConsoleUI.print_error(f"Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        input("\nPresione Enter para salir...")
    finally:
        # Ensure colorama is properly reset
        from colorama import deinit
        deinit()

# esta condición es el punto de entrada del programa. Esto permite ejecutar el archivo como un script y no como un módulo
# __name__ es una variable que contiene el nombre del módulo actual
# Si el archivo se ejecuta directamente, __name__ es "__main__"
# Si el archivo se importa como módulo, __name__ es el nombre del módulo
# Si esta condición no se pone, el código dentro del if se ejecutará cuando el archivo se importe como módulo
if __name__ == "__main__":
    main()
