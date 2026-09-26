import streamlit as st
import random
import string
import pyodbc
import pandas as pd

# --- CONFIGURACIÓN DE CONEXIÓN A SQL SERVER ---
def conectar_bd():
    try:
        conexion = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};' 
            'SERVER=CBTis139.mssql.somee.com;'        # <-- PON TU SERVIDOR
            'DATABASE=CBTis139;' # <-- PON TU BASE DE DATOS
            'UID=TovarLara_SQLLogin_1;'            # <-- PON TU USUARIO (ej. sa)
            'PWD=1hmetvyyiv'          # <-- PON TU CONTRASEÑA
        )
        return conexion
    except Exception as e:
        st.error(f"Error al conectar a la Base de Datos: {e}")
        return None

# --- DISEÑO DE LA PÁGINA ---
st.set_page_config(page_title="Panel de Asistencia", page_icon="🏫", layout="centered")
st.title("🏫 Colegio Universitario")
st.header("Panel de Coordinadores")

tab1, tab2 = st.tabs(["Generar Accesos", "Reportes de Asistencia"])

# --- PESTAÑA 1: GENERAR CÓDIGO ---
with tab1:
    st.subheader("🔑 Generar Código para Maestro")
    id_maestro = st.text_input("Ingresa el ID del Maestro (Ej. 1001)")
    
    if st.button("Generar Código", type="primary"):
        if id_maestro:
            conexion = conectar_bd()
            if conexion:
                cursor = conexion.cursor()
                
                # 1. Verificar si el maestro existe en SuperMaestros
                cursor.execute("SELECT nombre FROM SuperMaestros WHERE id_maestro = ?", (id_maestro,))
                maestro = cursor.fetchone()
                
                if maestro:
                    # 2. Generar código y actualizar en SQL Server
                    nuevo_codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
                    cursor.execute("UPDATE SuperMaestros SET codigo_acceso_actual = ? WHERE id_maestro = ?", (nuevo_codigo, id_maestro))
                    conexion.commit()
                    
                    st.success(f"¡Código generado para el maestro: {maestro[0]}!")
                    st.metric(label="Nuevo Código de Acceso", value=nuevo_codigo)
                else:
                    st.warning("Ese ID de maestro no existe en la base de datos.")
                
                conexion.close()
        else:
            st.warning("Por favor, ingresa un ID válido.")

# --- PESTAÑA 2: REPORTES ---
with tab2:
    st.subheader("📊 Reporte General de Asistencias")
    
    if st.button("Actualizar Tabla"):
        conexion = conectar_bd()
        if conexion:
            # Consulta uniendo las nuevas tablas "Super"
            query = """
            SELECT 
                a.fecha_hora AS Fecha,
                al.matricula AS Matricula,
                al.nombre + ' ' + al.apellidos AS Alumno,
                m.nombre AS Maestro_Monitor,
                a.estado AS Estado
            FROM SuperAsistencias a
            JOIN SuperAlumnos al ON a.matricula_alumno = al.matricula
            JOIN SuperMaestros m ON a.id_maestro = m.id_maestro
            ORDER BY a.fecha_hora DESC
            """
            df = pd.read_sql(query, conexion)
            
            if not df.empty:
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Aún no hay asistencias registradas.")
            
            conexion.close()

