FROM python:3.10-slim-bullseye

# Evitar que Linux haga preguntas interactivas que pausen la instalación
ENV DEBIAN_FRONTEND=noninteractive

# Instalamos las herramientas con certificados de seguridad extra
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    curl \
    apt-transport-https \
    gnupg \
    unixodbc-dev \
    ca-certificates

# Descargar las llaves oficiales de Microsoft SQL Server
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl -fsSL https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Instalar el Driver 17
RUN apt-get update -y && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Configurar tu aplicación
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Comando para encender la API
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}"]
