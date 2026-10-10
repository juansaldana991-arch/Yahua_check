import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, TextInput, TouchableOpacity, Alert, FlatList } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface Alumno {
  matricula: string;
  nombre: string;
  estado: string;
}

const API_URL = "https://api-asistencias-yahualica.onrender.com";

export default function App() {
  const [idMaestro, setIdMaestro] = useState('');
  const [sesionIniciada, setSesionIniciada] = useState(false);
  const [pantallaActual, setPantallaActual] = useState('menu');
  
  const [alumnosOffline, setAlumnosOffline] = useState<Alumno[]>([]);
  
  // NUEVO ESTADO: Para saber cuál fue el último alumno nombrado
  const [ultimoNombrado, setUltimoNombrado] = useState<string | null>(null);

  useEffect(() => {
    if (sesionIniciada) {
      cargarMemoriaLocal();
    }
  }, [sesionIniciada]);

  const cargarMemoriaLocal = async () => {
    try {
      const datosGuardados = await AsyncStorage.getItem('@alumnos_offline');
      if (datosGuardados !== null) {
        setAlumnosOffline(JSON.parse(datosGuardados));
      }
    } catch (e) {
      console.log("Error al cargar memoria local");
    }
  };

  const guardarMemoriaLocal = async (nuevosDatos: Alumno[]) => {
    try {
      setAlumnosOffline(nuevosDatos);
      await AsyncStorage.setItem('@alumnos_offline', JSON.stringify(nuevosDatos));
    } catch (e) {
      console.log("Error al guardar en memoria local");
    }
  };

  const handleLoginMaestro = async () => {
    if (!idMaestro.trim()) {
      Alert.alert("Error", "Por favor ingresa tu ID de maestro.");
      return;
    }

    try {
      const respuesta = await fetch(`${API_URL}/maestro/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id_maestro: parseInt(idMaestro) })
      });
      const datos = await respuesta.json();
      
      if (respuesta.ok) {
        Alert.alert("Éxito", datos.mensaje);
        setSesionIniciada(true);
      } else {
        const mensajeError = typeof datos.detail === 'string' 
          ? datos.detail 
          : "Faltan datos o el servidor en Render sigue actualizándose.";
          
        Alert.alert("Error", mensajeError);
      }
    } catch (error) {
      Alert.alert("Error", "No hay conexión a internet para iniciar sesión.");
    }
  };

  const descargarAlumnos = async () => {
    try {
      Alert.alert("Descargando...", "Obteniendo lista de la nube...");
      const respuesta = await fetch(`${API_URL}/alumnos/descargar`);
      const datos = await respuesta.json();
      
      if (respuesta.ok) {
        const listaPreparada: Alumno[] = datos.alumnos.map((alumno: {matricula: string, nombre: string}) => ({
          ...alumno,
          estado: 'Presente' 
        }));
        await guardarMemoriaLocal(listaPreparada);
        Alert.alert("¡Listo!", "Base de datos descargada. Ya puedes trabajar sin internet.");
      }
    } catch (error) {
      Alert.alert("Error", "Necesitas internet para descargar la lista.");
    }
  };

  const sincronizarNube = async () => {
    try {
      Alert.alert("Subiendo...", "Sincronizando datos con el servidor...");
      
      const registrosParaEnviar = alumnosOffline.map((alumno) => ({
        matricula_alumno: alumno.matricula,
        id_maestro: parseInt(idMaestro),
        estado: alumno.estado
      }));

      const respuesta = await fetch(`${API_URL}/asistencia/sincronizar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(registrosParaEnviar)
      });
      
      const datos = await respuesta.json();
      if (respuesta.ok) {
        Alert.alert("¡Sincronización Exitosa!", datos.mensaje);
      } else {
        Alert.alert("Error", "Hubo un problema al guardar en la nube.");
      }
    } catch (error) {
      Alert.alert("Error", "Necesitas internet para subir los reportes.");
    }
  };

  const alternarAsistencia = (matricula: string) => {
    const nuevosDatos = alumnosOffline.map((alumno) => {
      if (alumno.matricula === matricula) {
        return { ...alumno, estado: alumno.estado === 'Presente' ? 'Faltó' : 'Presente' };
      }
      return alumno;
    });
    guardarMemoriaLocal(nuevosDatos);
    setUltimoNombrado(matricula); // También marca a este alumno como el último interactuado
  };

  const alternarJustificante = (matricula: string) => {
    const nuevosDatos = alumnosOffline.map((alumno) => {
      if (alumno.matricula === matricula) {
        return { ...alumno, estado: alumno.estado === 'Faltó' ? 'Justificado' : 'Faltó' };
      }
      return alumno;
    });
    guardarMemoriaLocal(nuevosDatos);
  };

  if (sesionIniciada && pantallaActual === 'lista') {
    return (
      <View style={styles.container}>
        <Text style={styles.titulo}>Pase de Lista</Text>
        <Text style={styles.subtitulo}>Toca el nombre del alumno para marcar dónde vas.</Text>
        
        <FlatList 
          data={alumnosOffline}
          keyExtractor={(item) => item.matricula}
          renderItem={({ item }) => (
            // Cambio de diseño: Le agregamos un color diferente si es el "ultimoNombrado"
            <View style={[styles.filaAlumno, ultimoNombrado === item.matricula && styles.filaResaltada]}>
              
              {/* Aquí el maestro puede tocar el nombre para poner el marcador */}
              <TouchableOpacity 
                style={styles.infoTextContainer} 
                onPress={() => setUltimoNombrado(item.matricula)}
                activeOpacity={0.6}
              >
                <Text style={styles.nombre}>
                  {ultimoNombrado === item.matricula ? '📍 ' : ''}{item.nombre}
                </Text>
                <Text style={styles.matriculaTexto}>{item.matricula}</Text>
              </TouchableOpacity>

              <TouchableOpacity 
                style={[styles.botonEstado, item.estado === 'Presente' ? styles.bgVerde : styles.bgRojo]}
                onPress={() => alternarAsistencia(item.matricula)}
              >
                <Text style={styles.textoBotonEstado}>
                  {item.estado === 'Presente' ? '✅ Asistió' : '❌ Faltó'}
                </Text>
              </TouchableOpacity>
            </View>
          )}
        />
        <TouchableOpacity style={styles.botonAccion} onPress={() => setPantallaActual('menu')}>
          <Text style={styles.textoBoton}>Guardar y Volver al Menú</Text>
        </TouchableOpacity>
      </View>
    );
  }

  if (sesionIniciada && pantallaActual === 'justificantes') {
    const alumnosConFalta = alumnosOffline.filter(a => a.estado !== 'Presente');

    return (
      <View style={styles.container}>
        <Text style={styles.titulo}>Justificantes</Text>
        <Text style={styles.subtitulo}>Solo se muestran alumnos ausentes</Text>
        
        {alumnosConFalta.length === 0 ? (
          <Text style={{textAlign: 'center', marginTop: 50, fontSize: 16}}>No hay alumnos con faltas hoy. 🎉</Text>
        ) : (
          <FlatList 
            data={alumnosConFalta}
            keyExtractor={(item) => item.matricula}
            renderItem={({ item }) => (
              <View style={styles.filaAlumno}>
                <View style={styles.infoTextContainer}>
                  <Text style={styles.nombre}>{item.nombre}</Text>
                  <Text style={styles.matriculaTexto}>{item.matricula}</Text>
                </View>
                <TouchableOpacity 
                  style={[styles.botonEstado, item.estado === 'Justificado' ? styles.bgAmarillo : styles.bgRojo]}
                  onPress={() => alternarJustificante(item.matricula)}
                >
                  <Text style={styles.textoBotonEstado}>
                    {item.estado === 'Justificado' ? '⚠️ Justif.' : '❌ Faltó'}
                  </Text>
                </TouchableOpacity>
              </View>
            )}
          />
        )}
        <TouchableOpacity style={styles.botonAccion} onPress={() => setPantallaActual('menu')}>
          <Text style={styles.textoBoton}>Guardar y Volver al Menú</Text>
        </TouchableOpacity>
      </View>
    );
  }

  if (sesionIniciada && pantallaActual === 'menu') {
    return (
      <View style={styles.container}>
        <Text style={styles.titulo}>Panel del Maestro</Text>
        <Text style={styles.subtitulo}>Selecciona una opción</Text>

        <TouchableOpacity style={styles.botonMenuSecundario} onPress={descargarAlumnos}>
          <Text style={styles.textoBotonNegro}>1. 📥 Descargar Lista (Internet)</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.botonMenu} onPress={() => setPantallaActual('lista')}>
          <Text style={styles.textoBoton}>2. 📝 Tomar Asistencia (Offline)</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.botonMenuAzul} onPress={() => setPantallaActual('justificantes')}>
          <Text style={styles.textoBoton}>3. 📄 Aplicar Justificantes (Offline)</Text>
        </TouchableOpacity>

        <View style={styles.separador}></View>

        <TouchableOpacity style={styles.botonMenuNaranja} onPress={sincronizarNube}>
          <Text style={styles.textoBoton}>4. ☁️ Subir Reportes a la Nube</Text>
        </TouchableOpacity>

        <TouchableOpacity style={[styles.botonMenuSecundario, {marginTop: 30}]} onPress={() => setSesionIniciada(false)}>
          <Text style={styles.textoBotonNegro}>Cerrar Sesión</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.titulo}>Colegio Universitario</Text>
      <Text style={styles.subtitulo}>Portal de Maestros</Text>

      <View style={styles.formulario}>
        <Text style={styles.label}>ID de Maestro:</Text>
        <TextInput 
          style={styles.input} 
          placeholder="Ej. 1001" 
          value={idMaestro} 
          onChangeText={setIdMaestro} 
          keyboardType="numeric" 
        />
        <TouchableOpacity style={styles.botonAccion} onPress={handleLoginMaestro}>
          <Text style={styles.textoBoton}>Iniciar Sesión</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F3F4F6', padding: 20, justifyContent: 'center' },
  titulo: { fontSize: 28, fontWeight: 'bold', textAlign: 'center', color: '#1F2937' },
  subtitulo: { fontSize: 16, textAlign: 'center', color: '#6B7280', marginBottom: 20 },
  formulario: { backgroundColor: 'white', padding: 20, borderRadius: 15, elevation: 3 },
  label: { fontSize: 16, marginBottom: 8, color: '#4B5563', fontWeight: '500' },
  input: { borderWidth: 1, borderColor: '#D1D5DB', borderRadius: 8, padding: 15, marginBottom: 20, fontSize: 16, backgroundColor: '#F9FAFB' },
  
  botonMenu: { backgroundColor: '#10B981', padding: 18, borderRadius: 10, alignItems: 'center', marginBottom: 15, elevation: 2 },
  botonMenuAzul: { backgroundColor: '#3B82F6', padding: 18, borderRadius: 10, alignItems: 'center', marginBottom: 15, elevation: 2 },
  botonMenuNaranja: { backgroundColor: '#F59E0B', padding: 18, borderRadius: 10, alignItems: 'center', marginBottom: 15, elevation: 2 },
  botonMenuSecundario: { backgroundColor: '#E5E7EB', padding: 18, borderRadius: 10, alignItems: 'center', marginBottom: 15 },
  botonAccion: { backgroundColor: '#10B981', padding: 15, borderRadius: 10, alignItems: 'center', marginTop: 10 },
  textoBoton: { color: 'white', fontSize: 16, fontWeight: 'bold' },
  textoBotonNegro: { color: '#374151', fontSize: 16, fontWeight: 'bold' },
  separador: { height: 1, backgroundColor: '#D1D5DB', marginVertical: 15 },

  // ARREGLOS DE LA LISTA: Se agregó flex: 1 al contenedor del texto para que no empuje al botón
  filaAlumno: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', backgroundColor: 'white', padding: 15, marginBottom: 10, borderRadius: 10, elevation: 1 },
  filaResaltada: { backgroundColor: '#DBEAFE', borderColor: '#3B82F6', borderWidth: 1 }, // Color azul clarito cuando está marcado
  infoTextContainer: { flex: 1, paddingRight: 10 }, // ESTO EVITA QUE LOS NOMBRES LARGUEN EMPUJEN EL BOTÓN
  nombre: { fontSize: 15, fontWeight: 'bold', color: '#1F2937', flexWrap: 'wrap' }, // flexWrap permite 2 renglones
  matriculaTexto: { fontSize: 13, color: '#6B7280', marginTop: 3 },
  
  botonEstado: { paddingVertical: 10, paddingHorizontal: 10, borderRadius: 8, width: 110, alignItems: 'center', justifyContent: 'center' }, // Tamaño fijo
  textoBotonEstado: { color: 'white', fontWeight: 'bold', fontSize: 14 },
  
  bgVerde: { backgroundColor: '#10B981' },
  bgRojo: { backgroundColor: '#EF4444' },
  bgAmarillo: { backgroundColor: '#F59E0B' },
});

