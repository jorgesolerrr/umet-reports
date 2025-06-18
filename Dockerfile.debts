FROM python:3.13-slim AS base

# Instalar dependencias del sistema necesarias para compilar paquetes
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libmariadb-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar uv
RUN pip install --no-cache-dir uv

# Configurar directorio de trabajo
WORKDIR /app

RUN uv init .
# Copiar archivos de dependencias primero (para aprovechar caché de Docker)

# Instalar dependencias en un entorno virtual para mejor gestión


# Instalar dependencias con optimizaciones
COPY pyproject.toml uv.lock ./
RUN uv sync

# Copiar el código de la aplicación
COPY debts ./debts

FROM python:3.13-slim AS production

# Instalar solo las dependencias de runtime necesarias
RUN apt-get update && apt-get install -y \
    libmariadb3 \
    && rm -rf /var/lib/apt/lists/*

# Copiar el entorno virtual y la aplicación
COPY --from=base /usr/local /usr/local
COPY --from=base /app /app

# Configurar el PATH para usar el entorno virtual

WORKDIR /app

# Crear directorio de logs
RUN mkdir -p logs

CMD ["uv", "run", "debts/main.py"]