import streamlit as st
import pyodbc
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Coordinación Académica", page_icon="🎓", layout="wide")

# --- CONEXIÓN A SQL SERVER ---
@st.cache_resource
def conectar_bd():
    try:
        conexion = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};' 
            'SERVER=CBTis139.mssql.somee.com;'        
            'DATABASE=CBTis139;' 
            'UID=TovarLara_SQLLogin_1;'            
            'PWD=1hmetvyyiv'          
        )
        return conexion
    except Exception as e:
        st.error(f"Error crítico: No se pudo conectar a la base de datos. Detalles: {e}")
        return None

# --- CABECERA ---
st.title("🎓 Panel de Coordinación y Monitoreo")
st.markdown("Sistema inteligente de control de asistencia y alertas tempranas de deserción.")
st.divider()

# --- TABS (PESTAÑAS) PRINCIPALES ---
tab_general, tab_justificados, tab_alertas = st.tabs([
    "📊 Reportes Generales", 
    "📑 Registro de Justificantes", 
    "🚨 Alertas de Atención (Bajas Potenciales)"
])

# ==========================================
# PESTAÑA 1: REPORTES GENERALES (Filtros y Excel)
# ==========================================
with tab_general:
    st.subheader("Búsqueda y Filtro de Asistencias")
    
    # Controles de filtro en columnas
    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_estado = st.selectbox("Estado de Asistencia", ["Todos", "Presente", "Faltó", "Justificado"])
    with col2:
        fecha_inicio = st.date_input("Desde", datetime.today() - timedelta(days=7))
    with col3:
        fecha_fin = st.date_input("Hasta", datetime.today())

    if st.button("Generar Reporte", type="primary"):
        conexion = conectar_bd()
        if conexion:
            # Construimos la consulta base
            query = """
            SELECT 
                CONVERT(date, a.fecha_hora) AS Fecha,
                al.matricula AS Matricula,
                al.nombre + ' ' + ISNULL(al.apellidos, '') AS Alumno,
                m.nombre AS Maestro,
                a.estado AS Estado
            FROM SuperAsistencias a
            JOIN SuperAlumnos al ON a.matricula_alumno = al.matricula
            JOIN SuperMaestros m ON a.id_maestro = m.id_maestro
            WHERE CONVERT(date, a.fecha_hora) >= ? AND CONVERT(date, a.fecha_hora) <= ?
            """
            parametros = [fecha_inicio, fecha_fin]

            # Si el usuario eligió un estado específico, lo agregamos al filtro
            if filtro_estado != "Todos":
                query += " AND a.estado = ?"
                parametros.append(filtro_estado)
                
            query += " ORDER BY a.fecha_hora DESC"

            # Ejecutamos y pasamos a Pandas
            df = pd.read_sql(query, conexion, params=parametros)
            
            if not df.empty:
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Botón nativo para descargar Excel (CSV)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Descargar Reporte en Excel (CSV)",
                    data=csv,
                    file_name=f"Reporte_Asistencias_{fecha_inicio}_al_{fecha_fin}.csv",
                    mime="text/csv",
                )
                st.info("💡 Tip para PDF: Usa Ctrl+P en tu navegador mientras ves la tabla y guárdalo como PDF.")
            else:
                st.warning("No se encontraron registros para estas fechas y filtros.")

# ==========================================
# PESTAÑA 2: LISTA ÚNICA DE JUSTIFICANTES
# ==========================================
with tab_justificados:
    st.subheader("Historial de Alumnos Justificados")
    st.markdown("Lista exclusiva de inasistencias marcadas en **Amarillo (Justificado)** por los maestros.")
    
    if st.button("Cargar Justificantes"):
        conexion = conectar_bd()
        if conexion:
            query_justificados = """
            SELECT 
                CONVERT(date, a.fecha_hora) AS Fecha,
                al.matricula AS Matricula,
                al.nombre + ' ' + ISNULL(al.apellidos, '') AS Alumno,
                m.nombre AS Maestro_Autoriza
            FROM SuperAsistencias a
            JOIN SuperAlumnos al ON a.matricula_alumno = al.matricula
            JOIN SuperMaestros m ON a.id_maestro = m.id_maestro
            WHERE a.estado = 'Justificado'
            ORDER BY a.fecha_hora DESC
            """
            df_just = pd.read_sql(query_justificados, conexion)
            
            if not df_just.empty:
                st.dataframe(df_just, use_container_width=True, hide_index=True)
            else:
                st.success("No hay alumnos con justificantes registrados actualmente.")

# ==========================================
# PESTAÑA 3: ALERTAS DE ATENCIÓN (EL MOTOR LÓGICO)
# ==========================================
with tab_alertas:
    st.subheader("🚨 Alumnos en Riesgo (Requieren Atención de Coordinación)")
    st.markdown("El sistema analiza automáticamente el historial de los alumnos en busca de patrones de deserción.")
    
    if st.button("Ejecutar Análisis de Riesgo", type="primary"):
        conexion = conectar_bd()
        if conexion:
            st.write("Analizando base de datos...")
            
            # --- LÓGICA 1: MÁS DE 7 FALTAS EN EL CUATRIMESTRE (ÚLTIMOS 4 MESES) ---
            query_limite_faltas = """
            SELECT 
                al.matricula AS Matricula,
                al.nombre + ' ' + ISNULL(al.apellidos, '') AS Alumno,
                COUNT(a.id_asistencia) AS Total_Faltas
            FROM SuperAsistencias a
            JOIN SuperAlumnos al ON a.matricula_alumno = al.matricula
            WHERE a.estado = 'Faltó' 
              AND a.fecha_hora >= DATEADD(month, -4, GETDATE())
            GROUP BY al.matricula, al.nombre, al.apellidos
            HAVING COUNT(a.id_asistencia) >= 7
            ORDER BY Total_Faltas DESC
            """
            df_limite = pd.read_sql(query_limite_faltas, conexion)
            
            st.markdown("### ⚠️ Límite de Faltas Excedido (Más de 7 en el Cuatrimestre)")
            if not df_limite.empty:
                st.error(f"Se detectaron {len(df_limite)} alumnos que superaron el límite de inasistencias permitido.")
                st.dataframe(df_limite, use_container_width=True, hide_index=True)
            else:
                st.success("Ningún alumno ha superado las 7 faltas en este cuatrimestre.")

            st.divider()

            # --- LÓGICA 2: DOS SEMANAS SEGUIDAS DE AUSENCIA (ÚLTIMOS 14 DÍAS) ---
            # Explicación: Buscamos alumnos que tengan registros en los últimos 14 días, 
            # pero cuyo TOTAL de registros en ese tiempo sean PURAS faltas (0 asistencias, 0 justificantes).
            query_ausencia_prolongada = """
            WITH ActividadReciente AS (
                SELECT 
                    matricula_alumno,
                    SUM(CASE WHEN estado = 'Faltó' THEN 1 ELSE 0 END) AS Total_Faltas,
                    SUM(CASE WHEN estado IN ('Presente', 'Justificado') THEN 1 ELSE 0 END) AS Total_Presencias
                FROM SuperAsistencias
                WHERE fecha_hora >= DATEADD(day, -14, GETDATE())
                GROUP BY matricula_alumno
            )
            SELECT 
                al.matricula AS Matricula,
                al.nombre + ' ' + ISNULL(al.apellidos, '') AS Alumno,
                ar.Total_Faltas AS Dias_Ausente_Consecutivos
            FROM ActividadReciente ar
            JOIN SuperAlumnos al ON ar.matricula_alumno = al.matricula
            WHERE ar.Total_Presencias = 0 AND ar.Total_Faltas >= 10 
            -- (Se asumen 10 días hábiles en 2 semanas. Si van menos días a la semana, puedes bajar este número)
            """
            
            df_ausencia = pd.read_sql(query_ausencia_prolongada, conexion)
            
            st.markdown("### 🚫 Ausencia Prolongada (2 Semanas Consecutivas sin asistir)")
            if not df_ausencia.empty:
                st.error("Urge contactar a los siguientes alumnos. No se han presentado a ninguna clase en los últimos 14 días.")
                st.dataframe(df_ausencia, use_container_width=True, hide_index=True)
            else:
                st.success("No hay alumnos con rachas ininterrumpidas de ausencia de 2 semanas.")

