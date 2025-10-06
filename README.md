# 📝 Gestor de Tareas en Python

Aplicación de línea de comandos para gestionar tareas pendientes con prioridades, estados, simulación de datos y visualización de gráficos.

## 🚀 Características

- ✅ Gestión de tareas (crear, listar, actualizar, eliminar)
- 🏷️ Prioridades: ALTA, MEDIA, BAJA
- 📊 Estados: PENDIENTE, EN CURSO, FINALIZADA
- 📅 Fechas automáticas de creación
- 📤 Exportación a CSV
- 🔍 Búsqueda y filtrado de tareas
- 🎨 Interfaz de colores y emojis
- 📈 Visualización de datos con gráficos
- 🎲 Simulación de datos para análisis

## 📦 Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/todo_list_py.git
   cd todo_list_py
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## ▶️ Cómo Ejecutar

1. Ejecuta la aplicación:
   ```bash
   python -m todo_app.main
   ```

2. Los datos se guardan automáticamente en `todo_app/data/tareas.json`
3. Las exportaciones CSV se guardan en `todo_app/exports/`

## 📝 Uso

### Menú Principal
```
📋 GESTOR DE TAREAS
1. 📝 Crear tarea
2. 📋 Listar tareas
3. 🔍 Buscar tarea por nombre
4. ✏️  Actualizar tarea
5. 🗑️  Eliminar tarea
6. 💾 Exportar datos a CSV
7. 📊 Ver gráficos
8. 🎲 Simulación
0. ❌ Salir
```

### Visualización de Tareas
```
+----+-------------------------+-----------+-------------+---------------------+
| ID | NOMBRE                  | PRIORIDAD | ESTADO      | ÚLTIMA MODIFICACIÓN |
+====+=========================+===========+=============+=====================+
| 1  | Pagar tarjeta VISA      | ALTA      | PENDIENTE   | 2025-09-01 14:30    |
| 2  | Comprar víveres        | MEDIA     | EN CURSO    | 2025-09-01 15:15    |
+----+-------------------------+-----------+-------------+---------------------+
```

## 📂 Estructura de Archivos

### JSON de Tareas
```json
{
  "1": {
    "id": 1,
    "name": "Pagar tarjeta VISA",
    "priority": "ALTA",
    "status": "PENDIENTE",
    "created_at": "2025-09-01T14:30:00",
    "updated_at": "2025-09-01T14:30:00"
  }
}
```

### Ejemplo de CSV Exportado
```csv
ID,NOMBRE,PRIORIDAD,ESTADO,FECHA
1,Pagar tarjeta VISA,ALTA,PENDIENTE,2025-09-01 14:30:00
```

## 🛠️ Estructura del Proyecto

```
todo_list_py/
├── todo_app/
│   ├── data/                  # Datos de la aplicación
│   │   ├── tareas.json        # Tareas principales
│   │   └── tareas_simuladas_*.json  # Datos simulados
│   │
│   ├── exports/               # Archivos de exportación
│   │   └── yyyyMMdd_hhmmss_todo_list.csv
│   │
│   ├── models/                # Modelos de datos
│   │   └── task.py
│   │
│   ├── services/              # Lógica de negocio
│   │   ├── task_service.py    # Gestión de tareas
│   │   ├── export_service.py  # Exportación a CSV
│   │   ├── data_generator.py  # Generación de datos simulados
│   │   └── graphics_service.py # Visualización de gráficos
│   │
│   ├── utils/                 # Utilidades
│   │   └── ui_utils.py        # Interfaz de usuario
│   │
│   ├── simulator.py           # Módulo de simulación
│   └── main.py                # Punto de entrada
│
├── .windsurf/                 # Configuración de Windsurf
├── examples/                  # Ejemplos y datos de prueba
├── .gitignore
├── README.md
├── requirements.txt
└── arquitectura_todo_list.md  # Documentación de arquitectura
```

## 📝 Notas de Desarrollo

### Decisiones de Diseño
- Se utilizaron clases para mejor organización del código
- Se implementó un sistema de paginación para mejor usabilidad
- Se utilizaron colores y emojis para una mejor experiencia de usuario
- Las validaciones se implementaron tanto en el modelo como en el servicio

### 🚀 Posibles Mejoras
- Agregar más filtros de búsqueda
- Implementar categorías o etiquetas
- Añadir recordatorios o fechas límite
- Crear una interfaz web o de escritorio

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.
