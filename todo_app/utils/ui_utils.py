from typing import List, Any, TypeVar, Generic
from enum import Enum
import os
import platform
from datetime import datetime
from colorama import init, Fore, Style

# Inicializar colorama
init()

# Variable de tipo personalizada para filas de tabla
T = TypeVar('T')

class TextColor(Enum):
    """Opciones de color para la salida en consola."""
    HEADER = Fore.CYAN
    SUCCESS = Fore.GREEN
    WARNING = Fore.YELLOW
    ERROR = Fore.RED
    INFO = Fore.BLUE
    DEFAULT = Fore.WHITE
    HIGHLIGHT = Fore.MAGENTA

class TableStyle(Enum):
    """Estilos predefinidos para tablas."""
    SIMPLE = "simple"
    GRID = "grid"
    FANCY_GRID = "fancy_grid"
    PIPE = "pipe"
    ORGTBL = "orgtbl"
    JIRA = "jira"
    PRESTO = "presto"
    PRETTY = "pretty"
    PSQL = "psql"
    RST = "rst"
    MEDIAWIKI = "mediawiki"
    MOINMOIN = "moinmoin"
    YOUTRACK = "youtrack"
    HTML = "html"
    UNSAFEHTML = "unsafehtml"
    LIGHT = "light"
    HEAVY = "heavy"
    BOX = "box"
    ROUNDED = "rounded"

class ConsoleUI:
    """Clase de utilidad para elementos y formato de la interfaz de consola."""
    
    @staticmethod
    def clear_screen() -> None:
        """Limpia la pantalla de la consola."""
        if platform.system() == 'Windows':
            os.system('cls')
        else:
            os.system('clear')
    
    @staticmethod
    def print_header(text: str, symbol: str = '=', padding: int = 2) -> None:
        """Imprime un encabezado formateado.
        
        Args:
            text: Texto del encabezado
            symbol: Carácter a usar para la línea del encabezado
            padding: Número de líneas en blanco antes y después del encabezado
        """
        ConsoleUI.print_newline(padding)
        print(TextColor.HEADER.value + text + Style.RESET_ALL)
        print(TextColor.HEADER.value + symbol * len(text) + Style.RESET_ALL)
        ConsoleUI.print_newline(padding)
    
    @staticmethod
    def print_success(message: str) -> None:
        """Imprime un mensaje de éxito."""
        print(TextColor.SUCCESS.value + "✓ " + message + Style.RESET_ALL)
    
    @staticmethod
    def print_error(message: str) -> None:
        """Imprime un mensaje de error."""
        print(TextColor.ERROR.value + "✗ " + message + Style.RESET_ALL)
    
    @staticmethod
    def print_warning(message: str) -> None:
        """Imprime un mensaje de advertencia."""
        print(TextColor.WARNING.value + "⚠ " + message + Style.RESET_ALL)
    
    @staticmethod
    def print_info(message: str) -> None:
        """Imprime un mensaje informativo."""
        print(TextColor.INFO.value + "ℹ " + message + Style.RESET_ALL)
    
    @staticmethod
    def print_highlight(message: str) -> None:
        """Imprime texto resaltado."""
        print(TextColor.HIGHLIGHT.value + message + Style.RESET_ALL)
    
    @staticmethod
    def print_newline(lines: int = 1) -> None:
        """Imprime una o más líneas en blanco."""
        print('\n' * (lines - 1) if lines > 0 else '')
    
    @staticmethod
    def input_with_prompt(prompt: str, default: str = "") -> str:
        """Obtiene entrada del usuario con un mensaje formateado.
        
        Args:
            prompt: Mensaje a mostrar
            default: Valor por defecto si el usuario no ingresa nada
            
        Returns:
            Entrada del usuario o valor por defecto
        """
        prompt_text = f"{TextColor.INFO.value}» {prompt}: {Style.RESET_ALL}"
        if default:
            prompt_text = f"{prompt_text}[{TextColor.HIGHLIGHT.value}{default}{Style.RESET_ALL}] "
        
        user_input = input(prompt_text).strip()
        return user_input if user_input else default
    
    @staticmethod
    def confirm(prompt: str, default: bool = False) -> bool:
        """Solicita confirmación (sí/no).
        
        Args:
            prompt: Mensaje de confirmación
            default: Valor por defecto si el usuario presiona Enter sin ingresar nada
            
        Returns:
            True si se confirma, False en caso contrario
        """
        si_no = "(S/N)" if default else "(s/N)"
        prompt = f"{prompt} {si_no}: "
        
        while True:
            response = ConsoleUI.input_with_prompt(prompt, "S" if default else "N").lower()
            if response in ('s', 'si', 'sí', 'y', 'yes'):
                return True
            elif response in ('n', 'no'):
                return False
            print("Por favor, ingrese 's' para sí o 'n' para no.")
    
    @staticmethod
    def select_from_list(
        items: List[Any], 
        display_func: callable = str,
        prompt: str = "Seleccione una opción"
    ) -> Any:
        """Muestra una lista numerada y permite al usuario seleccionar un elemento.
        
        Args:
            items: Lista de elementos para seleccionar
            display_func: Función para convertir un elemento en una cadena de visualización
            prompt: Mensaje a mostrar al usuario
            
        Returns:
            El elemento seleccionado, o None si se cancela
        """
        if not items:
            ConsoleUI.print_warning("No hay elementos para seleccionar.")
            return None
            
        while True:
            ConsoleUI.print_highlight(f"\n{prompt}:")
            for i, item in enumerate(items, 1):
                print(f"{i}. {display_func(item)}")
            
            choice = ConsoleUI.input_with_prompt("Ingrese el número o 'q' para cancelar")
            
            if choice.lower() == 'q':
                return None
                
            try:
                index = int(choice) - 1
                if 0 <= index < len(items):
                    return items[index]
                ConsoleUI.print_error(f"Por favor ingrese un número entre 1 y {len(items)}")
            except ValueError:
                ConsoleUI.print_error("Entrada inválida. Por favor ingrese un número.")
    
    @staticmethod
    def format_datetime(dt: datetime) -> str:
        """Formatea un objeto datetime para su visualización."""
        return dt.strftime("%d-%m-%Y %H:%M:%S") if dt else ""
        # return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else ""


class TablePrinter(Generic[T]):
    """Clase auxiliar para mostrar datos tabulares con paginación."""
    
    def __init__(
        self,
        headers: List[str],
        data: List[T],
        rows_per_page: int = 10,
        style: TableStyle = TableStyle.GRID
    ):
        """Inicializa el generador de tablas.
        
        Args:
            headers: Lista de encabezados de columna
            data: Lista de filas de datos (cada fila es una lista o diccionario)
            rows_per_page: Número de filas por página
            style: Estilo de la tabla
        """
        self.headers = headers
        self.data = data
        self.rows_per_page = rows_per_page
        self.style = style
    
    def display(self) -> None:
        """Muestra la tabla con paginación."""
        from tabulate import tabulate
        
        if not self.data:
            ConsoleUI.print_info("No hay datos para mostrar.")
            return
            
        page = 0
        total_pages = (len(self.data) + self.rows_per_page - 1) // self.rows_per_page
        
        while True:
            ConsoleUI.clear_screen()
            start_idx = page * self.rows_per_page
            end_idx = min(start_idx + self.rows_per_page, len(self.data))
            
            # Obtener datos de la página actual
            page_data = self.data[start_idx:end_idx]
            
            # Mostrar tabla
            print(tabulate(
                page_data,
                headers=self.headers,
                tablefmt=self.style.value,
                showindex=range(start_idx + 1, end_idx + 1),
                numalign="left",
                stralign="left"
            ))
            
            # Mostrar información de paginación
            print(f"\nPágina {page + 1} de {total_pages} (elementos {start_idx + 1}-{end_idx} de {len(self.data)})")
            
            # Opciones de navegación
            options = []
            if page > 0:
                options.append("A - Página anterior")
            if page < total_pages - 1:
                options.append("S - Siguiente página")
            options.append("C - Continuar")
            
            print("\n" + " | ".join(options))
            
            # Obtener entrada del usuario
            while True:
                choice = input("\nIngrese su elección: ").strip().upper()
                
                if choice == 'A' and page > 0:
                    page -= 1
                    break
                elif choice == 'S' and page < total_pages - 1:
                    page += 1
                    break
                elif choice == 'C':
                    return
                else:
                    ConsoleUI.print_error("Opción inválida. Por favor intente nuevamente.")
