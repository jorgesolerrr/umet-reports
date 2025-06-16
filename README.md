# UMET Reports

Repositorio para la generación de reportes asociados a diferentes dominios de UMET.

## Descripción

Este proyecto está diseñado para generar reportes automatizados utilizando Python. Actualmente incluye funcionalidades para:

-   Generación de reportes de deudas
-   Procesamiento de datos en formato JSON
-   Exportación de reportes en formato Excel

## Requisitos

-   Python >= 3.13
-   Dependencias principales:
    -   openpyxl >= 3.1.5
    -   pandas >= 2.3.0

## Estructura del Proyecto

```
umet-reports/
├── debts/                  # Módulo de reportes de deudas
│   ├── reports/           # Directorio para reportes generados
│   └── build_report.py    # Script para generar reportes de deudas
├── data/                  # Directorio para archivos de datos
├── main.py               # Punto de entrada principal
└── pyproject.toml        # Configuración del proyecto y dependencias
```

## Uso

1. Clonar el repositorio
2. Crear un entorno virtual (recomendado):
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # En Windows: .venv\Scripts\activate
    ```
3. Instalar dependencias:
    ```bash
    pip install -e .
    ```
4. Ejecutar los reportes:
    ```bash
    python -m debts.build_report
    ```

## Licencia

Este proyecto está bajo licencia. Ver el archivo `LICENSE` para más detalles.
