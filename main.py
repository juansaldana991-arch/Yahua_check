from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pyodbc
import platform
from typing import List

app = FastAPI()

# --- CONFIGURACIÓN DE CONEXIÓN A SQL SERVER ---
def get_db_connection():
    if platform.system() == "Linux":
        driver_conexion = "{ODBC Driver 17 for SQL Server}"
    else:
        driver_conexion = "{SQL Server}"

    conexion_str = (
        f"DRIVER={driver_conexion};"
        "SERVER=CBTis139.mssql.somee.com;"
        "DATABASE=CBTis139;"
        "UID=TovarLara_SQLLogin_1;"
        "PWD=1hmetvyyiv"
    )
    
    return pyodbc.connect(conexion_str)

# --- MODELOS DE DATOS ---
class LoginMaestro(BaseModel):
    id_maestro: int
    codigo: str

class RegistroAsistencia(BaseModel):
    matricula_alumno: str
    id_maestro: int

# NUEVO: Modelo para recibir múltiples asistencias de golpe (Sincronización Offline)
class RegistroSincronizacion(BaseModel):
    matricula_alumno: str
    id_maestro: int
    estado: str  # Aquí recibiremos "Presente", "Faltó" o "Justificado"

# --- RUTAS DE LA API ---

@app.post("/maestro/login")
def login_maestro(datos: LoginMaestro):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT nombre FROM SuperMaestros WHERE id_maestro = ? AND codigo_acceso_actual = ?", 
                       (datos.id_maestro, datos.codigo))
        maestro = cursor.fetchone()
        conn.close()

        if maestro:
            return {"status": "Éxito", "mensaje": f"Bienvenido, Maestro {maestro[0]}"}
        else:
            raise HTTPException(status_code=401, detail="ID o código incorrecto")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")


@app.post("/asistencia/registrar")
def registrar_asistencia(datos: RegistroAsistencia):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT nombre FROM SuperAlumnos WHERE matricula = ?", (datos.matricula_alumno,))
        alumno = cursor.fetchone()
        
        if not alumno:
            conn.close()
            raise HTTPException(status_code=404, detail="Matrícula no encontrada en el sistema.")
            
        cursor.execute(
            "INSERT INTO SuperAsistencias (matricula_alumno, id_maestro, estado) VALUES (?, ?, ?)",
            (datos.matricula_alumno, datos.id_maestro, "Presente")
        )
        conn.commit()
        conn.close()
        
        return {"status": "Éxito", "mensaje": f"Asistencia registrada para {alumno[0]}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al registrar: {str(e)}")

# =========================================================
# NUEVAS RUTAS PARA EL MODO OFFLINE (LISTA POR DESCARTE)
# =========================================================

@app.get("/alumnos/descargar")
def descargar_alumnos():
    """Esta ruta envía todos los alumnos al celular del maestro para que funcione sin internet."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obtenemos la lista completa de alumnos
        cursor.execute("SELECT matricula, nombre FROM SuperAlumnos")
        alumnos_db = cursor.fetchall()
        conn.close()
        
        # Convertimos los datos de SQL a un formato que el celular entienda (JSON)
        lista_alumnos = [{"matricula": row[0], "nombre": row[1]} for row in alumnos_db]
        
        return {"status": "Éxito", "alumnos": lista_alumnos}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al descargar alumnos: {str(e)}")


@app.post("/asistencia/sincronizar")
def sincronizar_asistencias_offline(registros: List[RegistroSincronizacion]):
    """Esta ruta recibe de golpe toda la lista que el maestro guardó en su celular."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Recorremos la lista que mandó el celular y la guardamos en la base de datos
        for registro in registros:
            cursor.execute(
                "INSERT INTO SuperAsistencias (matricula_alumno, id_maestro, estado) VALUES (?, ?, ?)",
                (registro.matricula_alumno, registro.id_maestro, registro.estado)
            )
            
        conn.commit()
        conn.close()
        
        return {"status": "Éxito", "mensaje": f"{len(registros)} registros sincronizados correctamente a la nube."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al sincronizar: {str(e)}")
