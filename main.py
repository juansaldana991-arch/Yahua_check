from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pyodbc

app = FastAPI()

# --- CONFIGURACIÓN DE CONEXIÓN A SQL SERVER ---
def get_db_connection():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};' 
                    'SERVER=CBTis139.mssql.somee.com;'        # <-- PON TU SERVIDOR
                    'DATABASE=CBTis139;' # <-- PON TU BASE DE DATOS
                    'UID=TovarLara_SQLLogin_1;'            # <-- PON TU USUARIO (ej. sa)
                    'PWD=1hmetvyyiv'          # <-- PON TUS DATOS AQUÍ
    )

# --- MODELOS DE DATOS ---
class LoginMaestro(BaseModel):
    id_maestro: int
    codigo: str

class RegistroAsistencia(BaseModel):
    matricula_alumno: str
    id_maestro: int

# --- RUTAS DE LA API ---

@app.post("/maestro/login")
def login_maestro(datos: LoginMaestro):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificamos credenciales en la nueva tabla SuperMaestros
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
        
        # 1. Verificar si el alumno existe en SuperAlumnos
        cursor.execute("SELECT nombre FROM SuperAlumnos WHERE matricula = ?", (datos.matricula_alumno,))
        alumno = cursor.fetchone()
        
        if not alumno:
            conn.close()
            raise HTTPException(status_code=404, detail="Matrícula no encontrada en el sistema.")
            
        # 2. Registrar la asistencia en SuperAsistencias
        cursor.execute(
            "INSERT INTO SuperAsistencias (matricula_alumno, id_maestro, estado) VALUES (?, ?, ?)",
            (datos.matricula_alumno, datos.id_maestro, "Presente")
        )
        conn.commit()
        conn.close()
        
        return {"status": "Éxito", "mensaje": f"Asistencia registrada para {alumno[0]}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al registrar: {str(e)}")