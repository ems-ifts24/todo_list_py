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
    ├── main.py                   # Punto de entrada del programa
    ├── models/
    │   └── task.py               # Clase Task: definición del modelo de datos
    ├── services/
    │   ├── task_service.py       # Lógica de negocio para CRUD
    │   └── export_service.py     # Lógica para exportar datos a CSV
    ├── utils/
    │   ├── ui_utils.py           # Funciones para la interfaz de usuario
    │   └── pagination.py         # Lógica de paginación para listados
    ├── data/                     # Directorio para almacenamiento persistente
    │   └── tareas.json           # Archivo JSON con las tareas
    └── exports/                  # Directorio para archivos exportados
        └── yyyyMMdd_hhmmss_-_todo_list.csv  # Plantilla de nombre para exportaciones

------------------------------------------------------------------------

## **Módulos y responsabilidades**

### **1. main.py**

- Inicia la aplicación.
- Configura los servicios necesarios.
- Controla el flujo principal de la aplicación.
- Gestiona el bucle del menú principal.

------------------------------------------------------------------------

### **2. models/task.py**

**Responsabilidad**: Representar una tarea y su lógica asociada.

**Atributos**:
- `id` → int (identificador único)
- `nombre` → str (descripción de la tarea)
- `prioridad` → str (ALTA, MEDIA, BAJA)
- `estado` → str (PENDIENTE, EN CURSO, FINALIZADA)
- `fecha` → datetime (última modificación)

**Métodos principales**:
- `to_dict()` → Convierte la tarea a diccionario para serialización
- `from_dict(data: dict) → Task` → Crea una tarea desde un diccionario
- `__str__` → Representación en cadena de la tarea

------------------------------------------------------------------------
### **3. services/task_service.py**

**Responsabilidad**: Gestionar la lógica de negocio de las tareas.

**Funciones principales**:
- `crear_tarea(nombre, prioridad, estado)` → Crea una nueva tarea
- `obtener_todas()` → Obtiene todas las tareas
- `buscar_por_id(id)` → Busca una tarea por su ID
- `actualizar_tarea(id, cambios)` → Actualiza los campos de una tarea
- `eliminar_tarea(id)` → Elimina una tarea
- `filtrar_por_estado(estado)` → Filtra tareas por estado
- `filtrar_por_prioridad(prioridad)` → Filtra tareas por prioridad
- `buscar_por_texto(texto)` → Búsqueda de texto en nombres de tareas

**Manejo de datos**:
- Carga/guarda tareas desde/hacia el archivo JSON
- Valida las reglas de negocio
- Gestiona los IDs autoincrementales

------------------------------------------------------------------------

### **4. services/export_service.py**

**Responsabilidad**: Gestionar la exportación de datos a diferentes formatos.

**Funciones principales**:
- `exportar_a_csv(tareas, ruta_archivo)` → Exporta tareas a formato CSV
- `generar_nombre_archivo()` → Genera nombre de archivo con timestamp
- `validar_ruta_export()` → Verifica permisos de escritura

------------------------------------------------------------------------

### **5. utils/ui_utils.py**

**Responsabilidad**: Proporcionar utilidades para la interfaz de usuario.

**Funciones principales**:
- `limpiar_pantalla()` → Limpia la consola
- `mostrar_menu(opciones)` → Muestra un menú con opciones
- `mostrar_tabla(tareas)` → Muestra tareas en formato de tabla
- `formatear_fecha(fecha)` → Formatea fechas para mostrar
- `resaltar_texto(texto, color)` → Aplica colores al texto
- `mostrar_error(mensaje)` → Muestra mensajes de error
- `confirmar_accion(pregunta)` → Solicita confirmación al usuario

------------------------------------------------------------------------

### **6. utils/pagination.py**

**Responsabilidad**: Manejar la paginación de listados.

**Funciones principales**:
- `paginacion(datos, por_pagina=10)` → Divide los datos en páginas
- `mostrar_pagina(datos, num_pagina, por_pagina)` → Muestra una página específica
- `obtener_opcion_paginacion()` → Maneja la navegación entre páginas

------------------------------------------------------------------------

## **Flujo de Datos**

1. **Inicio**: `main.py` inicia la aplicación
2. **Carga de datos**: Se cargan las tareas desde `data/tareas.json`
3. **Interacción**: El usuario interactúa con el menú principal
4. **Procesamiento**: Las acciones se delegan a los servicios correspondientes
5. **Persistencia**: Los cambios se guardan automáticamente en `tareas.json`
6. **Exportación**: Opcionalmente, los datos pueden exportarse a CSV en `exports/`

## **Consideraciones de Diseño**

- **Separación de responsabilidades**: Cada módulo tiene una única responsabilidad
- **Manejo de errores**: Validaciones en cada capa de la aplicación
- **Extensibilidad**: Fácil de añadir nuevos formatos de exportación
- **UX**: Interfaz intuitiva con retroalimentación clara
- **Rendimiento**: Carga/guardado eficiente de datos
`listar_tareas(filtro_prioridad=None, orden_alfabetico=True)` -
`buscar_tareas_por_nombre(parcial)` - Validar reglas de negocio: - No
permitir tareas duplicadas salvo que la existente esté **FINALIZADA**. -
Validar transiciones de estado. - Actualizar fecha de modificación.

------------------------------------------------------------------------

### **4. utils/file_manager.py**

**Responsabilidad**: manejo de persistencia.

**Funciones**: - `leer_json()` → carga las tareas desde el archivo. -
`guardar_json()` → actualiza las tareas en disco. - `exportar_csv()` →
exporta las tareas a CSV con nombre dinámico
`yyyyMMdd_hhmmss_-_todo_list.csv`.

------------------------------------------------------------------------

### **5. utils/validators.py**

**Responsabilidad**: validar datos ingresados por el usuario.

**Validaciones**: - Prioridad → solo `1, 2, 3`. - Estado → solo
`1, 2, 3`. - Nombre único si no hay otra tarea pendiente/en curso con el
mismo nombre.

------------------------------------------------------------------------

### **6. utils/formatter.py**

**Responsabilidad**: dar formato visual.

**Funciones**: - `formatear_tabla(tareas)` → mostrar resultados en
formato tabular con paginación. - `colorear_estado(estado)` → mostrar
estados con colores distintos. - `colorear_prioridad(prioridad)` →
resaltar prioridades.

------------------------------------------------------------------------

### **7. ui/menu.py**

**Responsabilidad**: manejar la interacción con el usuario.

**Funciones**: - Mostrar menú principal. - Pedir datos para crear,
editar, eliminar o buscar. - Mantener la pantalla amigable: - Emojis ✅
❌ 🔄 - Colores para mensajes. - Limpiar pantalla entre operaciones. -
Paginar resultados cuando hay más de 10 tareas.

------------------------------------------------------------------------

## **Principios aplicados**

-   **S** → **Single Responsibility**: cada módulo tiene una única
    responsabilidad.
-   **O** → **Open/Closed**: fácil agregar nuevas funcionalidades sin
    modificar las existentes.
-   **L** → **Liskov Substitution**: las clases son reemplazables por
    sus abstracciones.
-   **I** → **Interface Segregation**: separar validaciones, formateo,
    lógica de negocio.
-   **D** → **Dependency Inversion**: `main.py` depende de
    abstracciones, no de implementaciones.

------------------------------------------------------------------------

## **Beneficios**

-   Código limpio y mantenible.
-   Alta cohesión, bajo acoplamiento.
-   Fácil agregar nuevas funcionalidades.
-   Exportación CSV y persistencia JSON claras y desacopladas.
