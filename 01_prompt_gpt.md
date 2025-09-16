# Prompt en ChatGPT

## Dijiste:
> Ejercicio en Python  
> Necesito generar una aplicación para guardar una lista de tareas que se ejecute por consola.  
> Dicha TODO List debo realizarla en python.  
> Debería guardar Tarea, prioridad y estado (pendiente/hecho).  
> El programa debe ofrecer todas las funciones de un CRUD, en un bucle infinito hasta que seleccione la opción de salir.  
> Luego de cada operación, deberá guardar o actualizar los datos en un archivo csv.  
> Otra opción del programa es generar un archivo json con toda la información a modo de Exportar los datos.  
> Quiero que me hagas todas preguntas necesarias para armar un prompt adecuado para que otra IA me pueda generar el código correctamente.

## ChatGPT dijo:
Perfecto 🙂  
Para armar un prompt sólido que otra IA pueda usar para generar el código completo de tu aplicación de consola en Python, primero necesito aclarar algunos puntos sobre los requisitos funcionales, estructura de datos, manejo de archivos y diseño de la app.  
Voy a dividir mis preguntas en secciones para que sea más fácil responder:

### 1. Datos de la Tarea
**¿Qué campos debe tener exactamente cada tarea?**
- Obligatorios: nombre de la tarea, prioridad, estado.

**Preguntas adicionales:**
- ¿Querés agregar un ID único para cada tarea para facilitar modificaciones y borrados?

**Para la prioridad, ¿qué valores querés manejar?**
- Ejemplo: alta, media, baja
- ¿O preferís números, como 1, 2, 3?

**Para el estado:**
- ¿Querés restringirlo solo a pendiente y hecho o que pueda haber más estados en el futuro?

---

### 2. Funcionalidades CRUD
El programa tendrá un menú interactivo. Confirmá si querés estas opciones o agregamos más:

1. Crear tarea
2. Listar todas las tareas
3. Buscar una tarea específica (por ID o por nombre)
4. Actualizar una tarea
5. Eliminar tarea
6. Exportar todas las tareas a JSON
7. Salir

**Preguntas adicionales:**
- ¿Querés que el listado permita filtrar por estado o prioridad?
- ¿El buscar debería ser por nombre parcial o coincidencia exacta?
- ¿El menú debería limpiar la consola cada vez que el usuario selecciona una opción para que sea más legible?

---

### 3. Manejo del Archivo CSV
**Ubicación del archivo:**
- ¿Dónde querés que se guarde el archivo CSV?  
  *Ejemplo: ./tareas.csv*

**Formato:**
- ¿El CSV debe tener encabezados? *(recomendado: Sí)*

**Comportamiento de escritura:**
- ¿Querés que el CSV se reescriba completo siempre?
- ¿O preferís que el programa solo agregue nuevas líneas y actualice in-place?

---

### 4. Exportar a JSON
**Nombre del archivo:**
- ¿Debería llamarse siempre igual? *(ejemplo: tareas.json)*

**Estructura de datos:**
- ¿Lista de objetos o diccionario indexado por ID?

**Ejemplos:**

**Opción 1 - Lista de objetos:**
```json
[
  {
    "id": 1,
    "tarea": "Pagar facturas",
    "prioridad": "alta",
    "estado": "pendiente"
  },
  {
    "id": 2,
    "tarea": "Llamar a Juan",
    "prioridad": "baja",
    "estado": "hecho"
  }
]
```

**Opción 2 - Diccionario indexado por ID:**
```json
{
  "1": {
    "tarea": "Pagar facturas",
    "prioridad": "alta",
    "estado": "pendiente"
  },
  "2": {
    "tarea": "Llamar a Juan",
    "prioridad": "baja",
    "estado": "hecho"
  }
}
```

---

### 5. Validaciones y Manejo de Errores
- ¿Querés que el programa valide que no se repitan nombres de tareas?
- Si el usuario ingresa una opción inválida, ¿el programa debe mostrar un mensaje y volver al menú principal?
- ¿Debe haber validación de prioridad y estado, mostrando solo valores permitidos?

---

### 6. Diseño del Programa
**Estructura de archivos:**
- ¿Preferís que el código esté en un único archivo o separado en módulos?  
  *Ejemplo: main.py, utils.py, storage.py*

**Paradigma de programación:**
- ¿Querés que tenga funciones puras o una clase que maneje toda la lógica?

**Documentación:**
- ¿Querés que el código esté comentado explicando cada parte?

**Interfaz de usuario:**
- ¿Te interesa que agregue colores en la consola para mejorar la legibilidad?

### 7. Otras Mejoras Posibles

**Ordenamiento:**
- ¿Querés que la lista de tareas se muestre ordenada por prioridad, estado o fecha de creación?

**Manejo de fechas:**
- ¿Querés que se guarde automáticamente la fecha de creación o actualización de cada tarea?

**Compatibilidad:**
- ¿El código debe funcionar en Python 3.10+ o hay alguna restricción?

---

### Próximos pasos
Con todas tus respuestas, puedo armarte un prompt ultra detallado que otra IA podrá usar para generar:

- Código completo de la aplicación
- Estructura de archivos
- Manejo de dependencias
- Documentación detallada
- Instrucciones de implementación

**Componentes del sistema a generar:**
- Código completo de la aplicación
- Menú interactivo amigable
- Funcionalidades CRUD completas
- Sistema de persistencia en CSV
- Módulo de exportación a JSON

**Aspectos adicionales:**
- Validaciones robustas
- Implementación de buenas prácticas de programación

---

## Respuestas del usuario

> 1.1- Si agrega un ID  
> 1.2- Prioridad debe guardar ALTA MEDIA BAJA pero para que el usuario no tenga que escribir la palabra, debe mostrarse como opción 1 2 o 3 y al lado la prioridad para que el usuario pueda elegir la que necesite  
> 1.3- similar al punto anterior, ofrecer tres opciones numéricas pero que se guarde: PENDIENTE, EN CURSO o FINALIZADA  

> 2.1 Si, filtrar por prioridad  
> 2.2 Buscar por nombre parcial  
> 2.3 si, limpiar la pantalla  

> 3.1 Gruardar el csv en la carpeta raiz de la aplicación  
> 3.2 agregar un encabezado  
> 3.3 Escucho tu propuesta para que sea más eficiente o rápido? En principio sería bueno poder agregar como una nueva linea los registros nuevos y editar los existentes. (No quiero guardar un historial de como estaban los registros antes)

> 4.1 El json debera tener como nombre la fecha del día que se generó en formato yyyyMMdd_hhmmss.json  
> 4.2 un diccionaro indexado por id

> 5.1 Si. No se puede ingresar dos tareas con el mismo nombre salgo que la existente tenga el estado FINALIZADA  
> 5.2 si, mostrar mensaje y volver a mostrar el menu  
> 5.3 también validar que los estados o prioridades sean las opciones 1 2 o 3. si es otra avisar y volver a preguntar

> 6.1 separado en módulos  
> 6.2 Creo que clases, pero utiliza las mejores prácticas  
> 6.3 quiero que comentes solo si es una funciones o código importante. No quiero que comentes código básico o simple de entender  
> 6.4 si, agrega colores y algún icono o emoji para una interfaz mas amigable con el usuario

> 7.1 quiero que se muestren ordenadas alfabéticamente y al final de la tarea el id entre paréntesis. Ej "Pagar tarjeta VISA (id:12)"
> 7.2 agregar la columna fecha para guardar la última modificación (esa será la de creación la primera vez, si se edita será la de modificación y si se termina la tarea, será la de finalización). De todas formas, no hace falta diferenciar que tipo de acción fue. Solo importa que el campo Fecha guarde el último cambio que se hizo  
> 7.3 python 3.1+ está bien  

> Nota sobre lógica de negocio: una tarea puede pasar de: pendiente a en curso, en curso a finalizada, pendiente a finalizada (directamente), de en curso a pendiente (retroceso). No se permite modificar el estado de una tarea si ya fue finalizada. En este último caso, si se podrá crear una tarea con el mismo nombre devuelta.  

> Adicionalmente, sería bueno que el listado de las tareas se muestre formateado como una tabla, paginado cada 10 tareas para que no se exceda de la pantalla y dar la opción de página siguiente, anterior o salir.  


## ChatGPT dijo:

Perfecto, con todas tus respuestas ya tengo una idea clarísima de lo que necesitás. 🙂

Voy a armar un prompt súper detallado para que puedas pasarlo a otra IA y que te genere un código completo, bien estructurado y con buenas prácticas.

Te incluyo todas las especificaciones que mencionaste y las optimizo para que el resultado sea un proyecto profesional, modular y mantenible.

## Prompt Final para la IA

Quiero que generes una aplicación de consola en Python 3.10+ para gestionar una lista de tareas (TODO List).

La app debe estar bien estructurada, modularizada y cumplir las siguientes especificaciones funcionales, de negocio y de usabilidad:

### 1. Requisitos funcionales

#### Campos de la tarea
Cada tarea tendrá los siguientes campos:

- **id**: entero autoincremental, único.
- **nombre**: string único (ver regla de duplicados más abajo).
- **prioridad**: string, valores posibles → ALTA, MEDIA, BAJA.
- **estado**: string, valores posibles → PENDIENTE, EN CURSO, FINALIZADA.
- **fecha**: datetime en formato YYYY-MM-DD HH:MM:SS → representa la última modificación de la tarea.

#### Reglas de negocio

- No se pueden crear dos tareas con el mismo nombre salvo que la existente esté en estado FINALIZADA.
- Transiciones permitidas de estado:
  - PENDIENTE → EN CURSO
  - PENDIENTE → FINALIZADA
  - EN CURSO → FINALIZADA
  - EN CURSO → PENDIENTE
- Si una tarea está en FINALIZADA, no puede cambiar su estado.
- Si una tarea está finalizada, se puede volver a crear otra tarea con el mismo nombre.

### 2. Funcionalidades del menú

La app debe ejecutarse en un bucle infinito y mostrar un menú principal con estas opciones:

1. Crear tarea
2. Listar tareas
3. Buscar tarea por nombre
4. Actualizar tarea (nombre, prioridad, estado)
5. Eliminar tarea
6. Exportar datos a JSON
7. Salir

#### Requisitos adicionales del menú
- Debe limpiar la consola antes de mostrar cada menú u opción.
- Mostrar iconos o emojis para que la interfaz sea más amigable.
- Validar entradas de usuario y mostrar mensajes claros si hay errores.

### 3. Listado de tareas

- El listado debe mostrarse ordenado alfabéticamente por nombre.
- Cada tarea debe mostrarse con este formato: `Pagar tarjeta VISA (id:12)`
- Mostrar los resultados en formato tabla con columnas: 
  - ID | NOMBRE | PRIORIDAD | ESTADO | FECHA

#### Paginación
- Máximo 10 tareas por página
- Al final de cada página, mostrar controles de navegación:
  - `[N]` → Página siguiente
  - `[P]` → Página anterior
  - `[S]` → Salir del listado

### 4. Manejo de CSV

- **Ubicación**: Archivo `tareas.csv` en la raíz del proyecto
- **Formato**: Incluir encabezados
- **Actualización automática**: Cada vez que se crea, edita o elimina una tarea

#### Estrategia de escritura:
- **Nuevas tareas**: Agregar como nuevas líneas
- **Modificaciones/Eliminaciones**: 
  1. Cargar todo el CSV en memoria
  2. Actualizar los datos
  3. Reescribir el archivo completo

### 5. Exportación a JSON

- **Formato del nombre**: `tareas_YYYYMMDD_HHMMSS.json`
- **Estructura**: Diccionario indexado por ID

```json
{
  "1": {
    "nombre": "Pagar facturas",
    "prioridad": "ALTA",
    "estado": "PENDIENTE",
    "fecha": "2025-09-01 10:15:00"
  },
  "2": {
    "nombre": "Llamar a Juan",
    "prioridad": "BAJA",
    "estado": "FINALIZADA",
    "fecha": "2025-09-01 12:00:00"
  }
}
```

### 6. Búsquedas y filtros

- **Búsqueda por nombre**: Búsqueda parcial insensible a mayúsculas/minúsculas
- **Filtros**: Permitir filtrar por prioridad

### 7. Validaciones

#### Opciones numéricas:

**Prioridad:**
1. ALTA
2. MEDIA
3. BAJA

**Estado:**
1. PENDIENTE
2. EN CURSO
3. FINALIZADA

- Validar entradas y mostrar mensajes claros
- Si se ingresa un valor inválido, volver a pedir la entrada
- En menús, ante opción inválida, mostrar mensaje y volver al menú principal

### 8. Estructura del proyecto

```
todo_app/
├── main.py             # Punto de entrada, arranca el menú principal
├── models/
│   └── task.py         # Clase Task con atributos y validaciones
├── services/
│   ├── task_service.py # Lógica CRUD y validaciones
│   └── export_service.py # Lógica para exportar a JSON
├── utils/
│   ├── csv_utils.py    # Funciones para leer/escribir CSV
│   ├── ui_utils.py     # Funciones para limpiar consola, colores, emojis, tablas
│   └── pagination.py   # Funciones para paginar listados
├── data/
│   └── tareas.csv      # Archivo CSV persistente
└── exports/
    └── tareas_YYYYMMDD_HHMMSS.json
```

### 9. Otros requisitos

- Usar programación orientada a objetos con clases
- Implementar interfaz atractiva con colores y emojis
- Documentación clara y concisa (solo funciones y bloques complejos)
- Seguir convenciones PEP8

### 10. Librerías

- **Estándar de Python**: Usar solo módulos de la biblioteca estándar, con dos excepciones:
  - `colorama` para colorear textos en consola
  - `tabulate` para formatear tablas de manera atractiva

### Objetivo final

Generar una aplicación que sea:
- **Completa y funcional**: Con todas las características solicitadas
- **Modular**: Código bien organizado en módulos y paquetes
- **Robusta**: Con manejo adecuado de errores y validaciones
- **Interactiva**: Interfaz de usuario clara y amigable
- **Profesional**: Siguiendo las mejores prácticas de Python (PEP 8, type hints, etc.)


## Información adicional que proporcionaste:  
> Agrego detalles para mejorar la experiencia de usuario.  
> Cuando se edite una tarea, se debe mostrar los datos actuales y preguntar que campo se quiere modificar: Tarea, prioridad o estado? y sin limpiar la pantalla debe pedirse el nuevo valor del campo elegido. Luego de modificarlo, preguntar si se quiere editar otro campo más, sino volver al menu.  

> Cambio el uso de los archivos. Quiero que se guarde siempre en un archivo json y en caso de querer exportarlo que se haga en un csv. El nombre de este archivo será la fecha de generación ej: yyyMMdd_hhmmss_-_todo_list.csv  

> El json no quiero que esté indexado por el id. mejor que esté el id como un atributo más del objeto y el json sería un array de jsons.  

## ChatGPT dijo:
Perfecto! 🙂  
Te muestro el prompt actualizado con todo integrado:  

Quiero que generes una aplicación de consola en Python 3.10+ para gestionar una lista de tareas (TODO List).  
La app debe estar bien estructurada, modularizada y cumplir las siguientes especificaciones funcionales, de negocio y de usabilidad:  

### Especificaciones Técnicas

#### 1. Requisitos funcionales

##### Campos de la tarea
Cada tarea tendrá los siguientes campos:

- **id**: Entero autoincremental, único
- **nombre**: String único (ver regla de duplicados más abajo)
- **prioridad**: String, valores posibles → ALTA, MEDIA, BAJA
- **estado**: String, valores posibles → PENDIENTE, EN CURSO, FINALIZADA
- **fecha**: Datetime en formato `YYYY-MM-DD HH:MM:SS` (última modificación)

#### Reglas de negocio

- No se pueden crear dos tareas con el mismo nombre, excepto si la existente está en estado FINALIZADA
- **Transiciones permitidas de estado**:
  - PENDIENTE → EN CURSO
  - PENDIENTE → FINALIZADA
  - EN CURSO → FINALIZADA
  - EN CURSO → PENDIENTE
- Si una tarea está en FINALIZADA, no puede cambiar su estado
- Si una tarea está finalizada, se puede volver a crear otra tarea con el mismo nombre

### 2. Funcionalidades del menú

La aplicación debe ejecutarse en un bucle infinito mostrando un menú principal con estas opciones:

1. Crear tarea
2. Listar tareas
3. Buscar tarea por nombre
4. Actualizar tarea
5. Eliminar tarea
6. Exportar datos a CSV
7. Salir

#### Requisitos adicionales del menú
- Limpiar la consola antes de mostrar cada menú/opción
- Usar iconos/emojis para mejorar la experiencia de usuario
- Validar entradas y mostrar mensajes de error claros

### 3. Edición de tareas

Al editar una tarea:
1. Mostrar sus datos actuales
2. Preguntar qué campo modificar (nombre, prioridad o estado)
3. No limpiar la pantalla durante la edición
4. Solicitar solo el valor del campo elegido
5. Preguntar si desea editar otro campo:
   - Si: Mostrar nuevamente las opciones
   - No: Guardar cambios y volver al menú principal

### 4. Listado de tareas

- Ordenar alfabéticamente por nombre
- Formato de visualización: `Pagar tarjeta VISA (id:12)`
- Mostrar en tabla con columnas: `ID | NOMBRE | PRIORIDAD | ESTADO | FECHA`
- **Paginación**: 10 tareas por página
- Controles de navegación:
  - `[N]` → Página siguiente
  - `[P]` → Página anterior
  - `[S]` → Salir del listado

### 5. Persistencia de datos

- **Formato**: JSON
- **Ubicación**: `tareas.json` en la raíz del proyecto
- **Estructura**: Array de objetos (no diccionario indexado)
- **Actualización**: Automática al crear/editar/eliminar tareas

### 6. Exportación a CSV

- **Nombre del archivo**: `yyyyMMdd_hhmmss_-_todo_list.csv`
- **Estructura**:
  ```
  ID,NOMBRE,PRIORIDAD,ESTADO,FECHA
  ```

### 7. Búsquedas y filtros

- Búsqueda por nombre: Parcial e insensible a mayúsculas/minúsculas
- Filtrado por prioridad

### 8. Validaciones

#### Opciones numéricas:

**Prioridad:**
1. ALTA
2. MEDIA
3. BAJA

**Estado:**
1. PENDIENTE
2. EN CURSO
3. FINALIZADA

- Validar entradas y mostrar mensajes de error claros
- Ante opciones inválidas, volver a solicitar la entrada

### 9. Estructura del proyecto

```
todo_app/
├── main.py             # Punto de entrada, arranca el menú principal
├── models/
│   └── task.py         # Clase Task con atributos y validaciones
├── services/
│   ├── task_service.py # Lógica CRUD y validaciones
│   └── export_service.py # Lógica para exportar a CSV
├── utils/
│   ├── json_utils.py   # Funciones para leer/escribir JSON
│   ├── csv_utils.py    # Funciones para exportar CSV
│   ├── ui_utils.py     # Funciones para limpiar consola, colores, emojis, tablas
│   └── pagination.py   # Funciones para paginar listados
├── data/
│   └── tareas.json     # Archivo JSON persistente
└── exports/
    └── yyyyMMdd_hhmmss_-_todo_list.csv
```

### 10. Otros requisitos

- Programación orientada a objetos
- Interfaz atractiva con colores y emojis
- Documentación clara (solo funciones/bloques complejos)
- Seguir convenciones PEP8

### 11. Dependencias

- **Estándar de Python** +:
  - `colorama` → para colorear textos
  - `tabulate` → para formatear tablas

## Objetivo final

Generar una aplicación que sea:
- **Completa y funcional**: Con todas las características solicitadas
- **Modular**: Código bien organizado en módulos y paquetes
- **Robusta**: Con manejo adecuado de errores y validaciones
- **Interactiva**: Interfaz de usuario clara y amigable
- **Profesional**: Siguiendo las mejores prácticas de Python (PEP 8, type hints, etc.)