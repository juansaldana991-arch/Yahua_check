import pyodbc

# 1. Configura tu conexión exacta
conexion_str = (
    "Driver={SQL Server};"
    "Server=CBTis139.mssql.somee.com;"
    "Database=CBTis139;"
    "UID=TovarLara_SQLLogin_1;"
    "PWD=1hmetvyyiv;"
)

try:
    conexion = pyodbc.connect(conexion_str)
    cursor = conexion.cursor()

    # 2. El comando SQL para crear la nueva tabla
    query = """
    CREATE TABLE SuperAsistenciasMaestros (
        id_registro INT IDENTITY(1,1) PRIMARY KEY,
        id_maestro INT NOT NULL,
        fecha_hora DATETIME DEFAULT GETDATE(),
        FOREIGN KEY (id_maestro) REFERENCES SuperMaestros(id_maestro)
    );
    """

    # 3. Ejecutamos y guardamos los cambios
    cursor.execute(query)
    conexion.commit()
    print("¡Éxito! La tabla SuperAsistenciasMaestros ha sido creada en la base de datos.")

except Exception as e:
    print(f"Ups, hubo un error: {e}")

finally:
    if 'conexion' in locals():
        conexion.close()
