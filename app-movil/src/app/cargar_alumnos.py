import pyodbc

# 1. Configura tu conexión exacta igual que en tu main.py
conexion_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=IP_DEL_SERVIDOR_DE_SAUL;"
    "Database=NOMBRE_DE_TU_BASE;"
    "UID=TU_USUARIO;"
    "PWD=TU_CONTRASEÑA;"
)

try:
    conexion = pyodbc.connect(conexion_str)
    cursor = conexion.cursor()

    # 2. El comando SQL con todos tus compañeros
    query = """
    INSERT INTO SuperAlumnos (Matricula, Nombre) 
    VALUES
    ('8857', 'BECERRA SANCHEZ JUAN DANIEL'),
    ('8936', 'CORONADO RODRIGUEZ EMMANUEL'),
    ('9056', 'GALVAN PACHECO PABLO EMMANUEL'),
    ('8870', 'GARCIA LOZANO KEVIN CANEB'),
    ('9037', 'GARCIA PEREZ EMMANUEL ALEJANDRO'),
    ('9119', 'GARCIA RAMIREZ EDGAR KALEB'),
    ('8682', 'GARCIA TRUJILLO JUAN ALBERTO'),
    ('8712', 'JUAREZ RODRIGUEZ CHRISTIAN'),
    ('8721', 'LABRA GONZALEZ INAYA VIRIDIANA'),
    ('8910', 'LONA ARAUJO PALOMA GABRIELA'),
    ('8725', 'PANTOJA SALAS JESUS ANGEL'),
    ('8726', 'RAMIREZ MENDOZA JUAN CARLOS'),
    ('8898', 'SALDAÑA TRUJILLO DIEGO GUADALUPE'),
    ('9120', 'SANCHEZ MARQUEZ LUIS DANIEL'),
    ('9167', 'SEGOVIANO RODRIGUEZ MELANI ITZEL'),
    ('8885', 'TRUJILLO HUERTA BRAYAN ALEJANDRO');
    """

    # 3. Ejecutamos y guardamos los cambios
    cursor.execute(query)
    conexion.commit()
    print("¡Éxito! Todos tus compañeros han sido registrados en la base de datos.")

except Exception as e:
    print(f"Ups, hubo un error: {e}")

finally:
    if 'conexion' in locals():
        conexion.close()
