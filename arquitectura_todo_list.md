# Arquitectura de la Aplicación TODO List (Python)

Este documento describe la **arquitectura modular** de la aplicación de
consola para gestión de tareas (TODO List).\
El objetivo es que la IA que genere el código entienda **claramente**
cómo debe estar estructurado el proyecto para mantener buenas prácticas,
separación de responsabilidades y principios **SOLID**.

------------------------------------------------------------------------

## **Estructura de carpetas actual**

    todo_app/
    │
    ├── main.py                   # Punto de entrada del programa + clase TodoApp principal
    ├── models/
    │   └── task.py               # Modelos: Task, Priority, Status enums
    ├── services/
    │   ├── task_service.py       # Lógica de negocio para CRUD de tareas
    │   └── export_service.py     # Lógica para exportar datos a CSV
    ├── utils/
    │   └── ui_utils.py           # Funciones para la interfaz de usuario + TablePrinter
    ├── data/                     # Directorio para almacenamiento persistente
    │   └── tareas.json           # Archivo JSON con las tareas
    └── exports/                  # Directorio para archivos exportados
        └── yyyyMMdd_hhmmss_todo_list.csv  # Plantilla de nombre para exportaciones

------------------------------------------------------------------------

## **Módulos y responsabilidades**

### **1. main.py**

- **Clase TodoApp**: Controla toda la lógica de la aplicación
- Inicia la aplicación y configura los servicios necesarios
- Gestiona el bucle principal del menú interactivo
- Maneja toda la interacción con el usuario (UI)
- Coordina las operaciones CRUD a través de los servicios
- Implementa navegación por tareas con paginación integrada

------------------------------------------------------------------------

### **2. models/task.py**

**Responsabilidad**: Representar una tarea y definir enumeraciones.

**Clases y Enums**:
- `Priority` → Enum (ALTA, MEDIA, BAJA)
- `Status` → Enum (PENDIENTE, EN CURSO, FINALIZADA)
- `Task` → Clase principal del modelo de datos

**Atributos de Task**:
- `id` → int (identificador único autoincremental)
- `name` → str (descripción de la tarea)
- `priority` → Priority (ALTA, MEDIA, BAJA)
- `status` → Status (PENDIENTE, EN CURSO, FINALIZADA)
- `created_at` → datetime (fecha de creación)
- `updated_at` → datetime (última modificación)

**Métodos principales de Task**:
- `update(name, priority, status)` → Actualiza campos con validación de transiciones
- `to_dict()` → Convierte la tarea a diccionario para serialización JSON
- `from_dict(data)` → Crea una tarea desde un diccionario (método de clase)
- `_validate_status_transition()` → Valida cambios de estado permitidos
- `__str__()` → Representación en cadena de la tarea
- `__eq__()` → Comparación por ID para igualdad

------------------------------------------------------------------------

### **3. services/task_service.py**

**Responsabilidad**: Gestionar la lógica de negocio y persistencia de tareas.

**Funciones principales**:
- `create_task(name, priority, status)` → Crea nueva tarea con validación de unicidad
- `get_all_tasks(priority_filter)` → Obtiene todas las tareas (opcionalmente filtradas)
- `get_task(task_id)` → Busca tarea específica por ID
- `update_task(id, **kwargs)` → Actualiza tarea con validación de reglas de negocio
- `delete_task(task_id)` → Elimina tarea por ID
- `search_tasks(query)` → Búsqueda de texto en nombres de tareas

**Características**:
- Manejo automático de IDs autoincrementales
- Persistencia en JSON (`data/tareas.json`)
- Validación de reglas de negocio (nombres únicos, transiciones de estado)
- Carga y guardado automático de datos

------------------------------------------------------------------------

### **4. services/export_service.py**

**Responsabilidad**: Gestionar la exportación de datos a CSV.

**Funciones principales**:
- `export_to_csv(tasks)` → Exporta tareas a formato CSV con timestamp
- `export_tasks_interactive(tasks)` → Proceso interactivo de exportación
- `_generate_export_filename()` → Genera nombre único con fecha y hora

**Características**:
- Genera archivos con nombres automáticos: `yyyymmdd_hhmmss_todo_list.csv`
- Almacenamiento en directorio `exports/`
- Formato CSV estándar con encabezados descriptivos
- Manejo de errores y validaciones

------------------------------------------------------------------------

### **5. utils/ui_utils.py**

**Responsabilidad**: Proporcionar utilidades para la interfaz de usuario.

**Clases principales**:
- `ConsoleUI` → Funciones estáticas para interacción con consola
- `TablePrinter` → Generador de tablas con paginación integrada
- `TextColor` → Enum para colores de consola
- `TableStyle` → Enum para estilos de tabla (aunque actualmente solo se usa FANCY_GRID)

**Funciones de ConsoleUI**:
- `clear_screen()` → Limpia la pantalla de la consola
- `print_header(text, symbol, padding)` → Imprime encabezados formateados
- `print_success/error/warning/info/highlight()` → Mensajes con colores
- `input_with_prompt(prompt, default)` → Obtiene entrada del usuario formateada
- `confirm(prompt, default)` → Solicita confirmación sí/no

**Características de TablePrinter**:
- Muestra datos tabulares con paginación automática
- Soporta diferentes estilos de tabla (aunque usa FANCY_GRID por defecto)
- Navegación interactiva: Anterior/Siguiente/Continuar
- Configurable filas por página (10 por defecto)

------------------------------------------------------------------------

## **Flujo de Datos Actual**

1. **Inicio**: `main.py` ejecuta la aplicación → `TodoApp.__init__()`
2. **Configuración**: Se inicializan `TaskService` y `ExportService`
3. **Carga de datos**: `TaskService` carga tareas desde `data/tareas.json`
4. **Interacción**: `TodoApp` gestiona el menú principal interactivo
5. **Operaciones CRUD**: Se delegan al `TaskService` correspondiente
6. **Persistencia**: Los cambios se guardan automáticamente en JSON
7. **Presentación**: `TablePrinter` muestra datos con paginación integrada
8. **Exportación**: `ExportService` genera archivos CSV en `exports/`

------------------------------------------------------------------------

## **Características Técnicas Actuales**

### **Arquitectura Aplicada**
- **MVC simplificado**: Modelos + Servicios + Vista integrada en controlador
- **Separación clara**: Cada servicio tiene responsabilidad única
- **Inyección de dependencias**: Servicios configurados en constructor
- **Patrón Repository**: `TaskService` abstrae la persistencia

### **Validaciones y Reglas de Negocio**
- **Nombres únicos**: No se permiten tareas duplicadas activas
- **Transiciones de estado**: Solo cambios válidos (PENDING→IN_PROGRESS→COMPLETED)
- **Tareas completadas**: No modificables (regla de inmutabilidad)
- **IDs autoincrementales**: Gestión automática de identificadores

### **Características de Usuario**
- **Interfaz intuitiva**: Navegación por menú numerado
- **Retroalimentación visual**: Colores para diferentes tipos de mensajes
- **Paginación automática**: Listados divididos en páginas de 10 elementos
- **Búsqueda de texto**: Filtrado por nombre parcial (case-insensitive)
- **Exportación filtrada**: Opción de exportar por prioridad específica

------------------------------------------------------------------------

## **Principios SOLID Aplicados**

- **S** → **Single Responsibility**: Cada clase tiene una responsabilidad única
- **O** → **Open/Closed**: Fácil extender funcionalidades sin modificar existentes
- **L** → **Liskov Substitution**: Enums y clases son reemplazables por abstracciones
- **I** → **Interface Segregation**: Métodos enfocados y específicos
- **D** → **Dependency Inversion**: `TodoApp` depende de abstracciones de servicios

------------------------------------------------------------------------

## **Estado Actual vs Documentación Anterior**

### **Simplificaciones Realizadas**
- ❌ Eliminado `utils/pagination.py` → Funcionalidad integrada en `TablePrinter`
- ❌ Eliminados módulos separados → Funcionalidades consolidadas en clases existentes
- ❌ Removidos métodos sin uso → `select_from_list()`, `format_datetime()`, métodos comentados
- ✅ Agregados comentarios explicativos → Para todos los decoradores y métodos mágicos
- ✅ Arquitectura más limpia → Menos archivos, mejor mantenibilidad

### **Mejoras de Documentación**
- ✅ Comentarios para `@staticmethod` y `@classmethod`
- ✅ Comentarios para métodos mágicos (`__init__`, `__str__`, `__eq__`)
- ✅ Comentarios para condición de punto de entrada (`if __name__ == "__main__"`)
- ✅ Documentación actualizada de responsabilidades reales

------------------------------------------------------------------------

## **Beneficios de la Arquitectura Actual**

- **Código más mantenible**: Menos archivos, responsabilidades claras
- **Mejor separación**: Servicios enfocados vs controlador integrado
- **Fácil extensión**: Agregar nuevas funcionalidades en servicios específicos
- **Performance optimizada**: Una sola carga de datos, persistencia automática
- **UX mejorada**: Paginación integrada, navegación intuitiva
- **Código documentado**: Comentarios explicativos para elementos técnicos
