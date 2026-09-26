FROM python:3.10-slim-bullseye

# Instalar herramientas necesarias y el Driver 17 de SQL Server
RUN apt-get update && apt-get install -y curl apt-transport-https gnupg2 unixodbc-dev
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Configurar la carpeta de la aplicación
WORKDIR /app

# Instalar tus librerías de requirements.txt
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copiar el resto de tus archivos (main.py, panel_web.py, etc.)
COPY . .

# Comando para encender tu API en la nube
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}"]
