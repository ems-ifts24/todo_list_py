from typing import List, TypeVar, Generic, Callable, Optional
from dataclasses import dataclass

T = TypeVar('T')

@dataclass
class Page(Generic[T]):
    """Representa una página de elementos con metadatos de paginación."""
    items: List[T]
    page_number: int
    page_size: int
    total_items: int
    total_pages: int

class Paginator(Generic[T]):
    """Clase auxiliar para paginar una lista de elementos."""
    
    def __init__(self, items: List[T], page_size: int = 10):
        """Inicializa el paginador.
        
        Args:
            items: Lista de elementos a paginar
            page_size: Número de elementos por página
        """
        self.items = items
        self.page_size = max(1, page_size)
        self.total_items = len(items)
        self.total_pages = (self.total_items + self.page_size - 1) // self.page_size
    
    def get_page(self, page_number: int = 1) -> Page[T]:
        """Obtiene una página específica de elementos.
        
        Args:
            page_number: Número de página basado en 1
            
        Returns:
            Un objeto Page que contiene los elementos de la página solicitada
            
        Raises:
            ValueError: Si el número de página está fuera de rango
        """
        if page_number < 1 or (page_number > self.total_pages and self.total_pages > 0):
            raise ValueError(f"El número de página debe estar entre 1 y {self.total_pages}")
            
        start = (page_number - 1) * self.page_size
        end = start + self.page_size
        
        return Page(
            items=self.items[start:end],
            page_number=page_number,
            page_size=self.page_size,
            total_items=self.total_items,
            total_pages=self.total_pages
        )
    
    def iterate_pages(self) -> 'PageIterator[T]':
        """Obtiene un iterador sobre todas las páginas."""
        return PageIterator(self)
    
    @property
    def page_numbers(self) -> range:
        """Obtiene un rango de números de página (basado en 1)."""
        return range(1, self.total_pages + 1)


class PageIterator(Generic[T]):
    """Iterador para resultados paginados."""
    
    def __init__(self, paginator: Paginator[T]):
        """Inicializa el iterador.
        
        Args:
            paginator: El paginador sobre el que iterar
        """
        self.paginator = paginator
        self.current_page = 0
    
    def __iter__(self) -> 'PageIterator[T]':
        return self
    
    def __next__(self) -> Page[T]:
        """Obtiene la siguiente página."""
        self.current_page += 1
        if self.current_page > self.paginator.total_pages:
            raise StopIteration
        return self.paginator.get_page(self.current_page)


def paginate_with_ui(
    items: List[T],
    display_func: Callable[[List[T]], None],
    page_size: int = 10,
    item_name: str = "elementos",
    empty_message: str = "No hay elementos para mostrar."
) -> bool:
    """Muestra elementos con paginación y maneja la navegación del usuario.
    
    Args:
        items: Lista de elementos a paginar
        display_func: Función que recibe una lista de elementos y los muestra
        page_size: Número de elementos por página
        item_name: Nombre de los elementos que se muestran (para mensajes de estado)
        empty_message: Mensaje que se muestra cuando no hay elementos
        
    Returns:
        bool: True si el usuario eligió salir, False si vio todas las páginas
    """
    if not items:
        print(f"\n{empty_message}")
        return True
    
    paginator = Paginator(items, page_size)
    current_page = 1
    
    while True:
        try:
            page = paginator.get_page(current_page)
            
            # Display the current page
            display_func(page.items)
            
            # Mostrar información de paginación
            start_item = (current_page - 1) * page_size + 1
            end_item = min(start_item + page_size - 1, paginator.total_items)
            print(f"\nPágina {current_page} de {paginator.total_pages} ({start_item}-{end_item} de {paginator.total_items} {item_name})")
            
            # Mostrar opciones de navegación
            options = []
            if current_page > 1:
                options.append("A - Página anterior")
            if current_page < paginator.total_pages:
                options.append("S - Siguiente página")
            options.append("Q - Volver al menú principal")
            
            if options:
                print(" | ".join(options))
            
            # Obtener entrada del usuario
            while True:
                choice = input("\nIngrese su opción: ").strip().upper()
                
                if choice == 'Q':
                    return True
                elif choice == 'A' and current_page > 1:
                    current_page -= 1
                    break
                elif choice == 'S' and current_page < paginator.total_pages:
                    current_page += 1
                    break
                else:
                    print("Opción no válida. Por favor, inténtelo de nuevo.")
        
        except KeyboardInterrupt:
            print("\nOperación cancelada por el usuario.")
            return True
        except Exception as e:
            print(f"\nError: {str(e)}")
            return True


def display_paginated_menu(
    items: List[T],
    display_func: Callable[[T], str],
    title: str = "Seleccione un elemento",
    page_size: int = 10,
    allow_cancel: bool = True
) -> Optional[T]:
    """Muestra un menú paginado y permite al usuario seleccionar un elemento.
    
    Args:
        items: Lista de elementos a mostrar
        display_func: Función que convierte un elemento en una cadena para mostrar
        title: Título que se muestra encima del menú
        page_size: Número de elementos por página
        allow_cancel: Indica si se permite al usuario cancelar la selección
        
    Returns:
        El elemento seleccionado, o None si se canceló
    """
    if not items:
        print("No hay elementos disponibles para seleccionar.")
        return None
    
    paginator = Paginator(items, page_size)
    current_page = 1
    
    while True:
        try:
            page = paginator.get_page(current_page)
            
            # Mostrar el título y los elementos de la página actual
            print(f"\n{title}:")
            for i, item in enumerate(page.items, 1):
                print(f"{(current_page - 1) * page_size + i}. {display_func(item)}")
            
            # Mostrar información de paginación
            print(f"\nPágina {current_page} de {paginator.total_pages} "
                  f"(Total: {paginator.total_items} elementos)")
            
            # Mostrar opciones de navegación
            options = []
            if current_page > 1:
                options.append("A - Página anterior")
            if current_page < paginator.total_pages:
                options.append("S - Siguiente página")
            if allow_cancel:
                options.append("C - Cancelar")
            
            if options:
                print("\nOpciones:")
                print("\n".join(options))
            
            # Obtener entrada del usuario
            prompt = "\nIngrese el número del elemento o una opción: "
            choice = input(prompt).strip().upper()
            
            if choice == 'C' and allow_cancel:
                return None
            elif choice == 'A' and current_page > 1:
                current_page -= 1
            elif choice == 'S' and current_page < paginator.total_pages:
                current_page += 1
            elif choice.isdigit():
                item_index = int(choice) - 1
                absolute_index = (current_page - 1) * page_size + item_index
                if 0 <= item_index < len(page.items):
                    return items[absolute_index]
                else:
                    print(f"Por favor, ingrese un número entre 1 y {len(page.items)}")
            else:
                print("Opción no válida. Por favor, inténtelo de nuevo.")
                
        except ValueError as e:
            print("\nOperación cancelada por el usuario.")
            return None
        except Exception as e:
            print(f"\nError: {str(e)}")
            return None
