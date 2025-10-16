# Grades - Sistema de Reportes de Calificaciones

Sistema de extracción y generación de reportes de calificaciones desde Moodle con procesamiento paralelo usando Redis.

## Características

-   **Procesamiento paralelo**: Utiliza ThreadPoolExecutor para procesar múltiples cursos simultáneamente
-   **Almacenamiento temporal en Redis**: Los datos se almacenan temporalmente en Redis para un procesamiento eficiente
-   **Búsqueda por patrones**: Busca cursos en Moodle usando patrones configurables
-   **Generación de Excel**: Exporta los datos a un archivo Excel formateado

## Estructura del Proyecto

```
grades/
├── main.py                          # Punto de entrada principal
├── src/
│   ├── settings.py                  # Configuración y variables de entorno
│   ├── parsers.py                   # Extracción de info del curso y construcción de filas Excel
│   ├── extract_data_flow.py         # Flujo de extracción paralela
│   ├── build_report.py              # Obtención de datos de Redis y generación de Excel
│   ├── grade_report_flow.py         # Parseo de calificaciones individuales (usado por parsers)
│   └── utils/
│       ├── moodle_client.py         # Cliente para API de Moodle
│       ├── redis_client.py          # Cliente de Redis
│       └── logging/                 # Sistema de logging
```

## Configuración

1. **Copiar el archivo de ejemplo de variables de entorno:**

    ```bash
    cp .env.grades.example .env.grades
    ```

2. **Configurar las variables de entorno en `.env.grades`:**

    - `MOODLE_URL`: URL del webservice de Moodle
    - `MOODLE_TOKEN`: Token de acceso a la API de Moodle
    - `MOODLE_NAME`: Nombre de la instancia (default: "grades")
    - `REDIS_HOST`: Host de Redis (default: "localhost")
    - `REDIS_PORT`: Puerto de Redis (default: 6379)

3. **Configurar patrones de búsqueda** (opcional en `settings.py`):
    - Por defecto: `["GRA-PA66", "UAFTT-PA12"]`

## Uso

### Ejecutar el sistema completo

```bash
python -m grades.main
```

Esto ejecutará el siguiente flujo:

1. **Extracción**: Busca cursos en Moodle por cada patrón configurado
2. **Procesamiento paralelo**: Procesa los cursos en paralelo usando 8 workers
3. **Procesamiento por curso**:
    - Usa `get_course_grade_report()` de `grade_report_flow.py` para parsear calificaciones
    - Enriquece cada fila con información del curso (PERIODO, OFG, PROFESOR, NOMBRE)
    - Cada diccionario resultante representa una fila completa del Excel
4. **Almacenamiento**: Guarda las filas completas en Redis temporalmente
5. **Generación de reporte**: Combina todas las filas de Redis y crea archivo Excel
6. **Limpieza**: Limpia los datos de Redis

### Salida

El sistema genera un archivo Excel con el formato:

```
reporte_calificaciones_YYYYMMDD.xlsx
```

## Campos del Reporte Excel

-   **PERIODO**: Período académico extraído del path de categorías
-   **OFG**: Código extraído del nombre corto del curso
-   **PROFESOR NOMBRE**: Nombre del primer docente asignado
-   **PROFESOR CEDULA**: Cédula/username del profesor
-   **NOMBRE**: Nombre corto del curso
-   **ESTUDIANTE**: Nombre completo del estudiante
-   **CEDULA_ESTUDIANTE**: Cédula/ID del estudiante
-   **CORTE_1, CORTE_2, CORTE_3...**: Calificaciones por corte

## Procesamiento Paralelo

El sistema utiliza procesamiento paralelo para mejorar el rendimiento:

-   **8 workers por defecto**: Procesa hasta 8 cursos simultáneamente
-   **Chunks dinámicos**: Divide automáticamente los cursos en chunks
-   **Manejo de errores**: Continúa procesando aunque algunos cursos fallen

## Requisitos

-   Python 3.10+
-   Redis (servidor corriendo)
-   Acceso a la API de Moodle con token válido
-   Dependencias: pandas, openpyxl, redis, requests, pydantic-settings

## Notas

-   Los cursos con "PLANTILLA" en el nombre son filtrados automáticamente
-   El sistema limpia Redis después de cada ejecución
-   Los logs se guardan en `logs/grades.log`
-   Si un curso no tiene profesor asignado, aparecerá como "SIN PROFESOR"
