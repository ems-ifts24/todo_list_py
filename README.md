# 📝 Gestor de Tareas en Python

Aplicación de línea de comandos para gestionar tareas pendientes con prioridades, estados y exportación a CSV.

## 🚀 Características

- ✅ Gestión de tareas (crear, listar, actualizar, eliminar)
- 🏷️ Prioridades: ALTA, MEDIA, BAJA
- 📊 Estados: PENDIENTE, EN_PROGRESO, COMPLETADA
- 📅 Fechas automáticas de creación
- 📤 Exportación a CSV
- 🔍 Búsqueda y filtrado de tareas
- 🎨 Interfaz de colores y emojis

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
=== Gestor de Tareas ===
1. 📋 Listar tareas
2. ➕ Agregar tarea
3. ✏️ Actualizar tarea
4. ❌ Eliminar tarea
5. 🔍 Buscar tareas
6. 📤 Exportar a CSV
7. ❌ Salir
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
│   ├── data/           # Datos de la aplicación
│   ├── exports/        # Archivos de exportación
│   ├── models/         # Modelos de datos
│   ├── services/       # Lógica de negocio
│   └── main.py         # Punto de entrada
├── .gitignore
├── README.md
└── requirements.txt
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
