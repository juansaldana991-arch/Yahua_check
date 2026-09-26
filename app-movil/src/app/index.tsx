import React, { useState } from 'react';
import { StyleSheet, Text, View, TextInput, TouchableOpacity, Alert } from 'react-native';
import QRCode from 'react-native-qrcode-svg';
import { CameraView, useCameraPermissions } from 'expo-camera';

// 👇 PON AQUÍ LA IP DE TU COMPUTADORA CON EL PUERTO 8000 👇
const API_URL = "http://192.168.1.115:8000"; 

export default function App() {
  const [tipoUsuario, setTipoUsuario] = useState('maestro'); 
  
  // Estados del Maestro
  const [idMaestro, setIdMaestro] = useState('');
  const [codigo, setCodigo] = useState('');
  const [sesionIniciada, setSesionIniciada] = useState(false);
  const [escaneando, setEscaneando] = useState(false);
  const [permisoCamara, pedirPermisoCamara] = useCameraPermissions();
  
  // Estados del Alumno
  const [matricula, setMatricula] = useState('');
  const [qrGenerado, setQrGenerado] = useState<string | null>(null);

  // --- FUNCIONES DEL MAESTRO ---
  const handleLoginMaestro = async () => {
    try {
      const respuesta = await fetch(`${API_URL}/maestro/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id_maestro: parseInt(idMaestro), codigo: codigo })
      });
      
      const datos = await respuesta.json();
      
      if (respuesta.ok) {
        Alert.alert("Éxito", datos.mensaje);
        setSesionIniciada(true);
      } else {
        Alert.alert("Error", datos.detail || "Código incorrecto");
      }
    } catch (error) {
      Alert.alert("Error de Conexión", "No se pudo conectar a la API. Verifica tu IP y que la API esté encendida.");
    }
  };

  const handleEscanearQR = ({ data }: { data: string }) => {
    setEscaneando(false); 
    
    fetch(`${API_URL}/asistencia/registrar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ matricula_alumno: data, id_maestro: parseInt(idMaestro) })
    })
    .then(res => res.json())
    .then(datos => {
      if (datos.status === "Éxito") {
        Alert.alert("✅ Asistencia Registrada", datos.mensaje);
      } else {
        Alert.alert("❌ Error", datos.detail || "No se pudo registrar.");
      }
    })
    .catch(error => Alert.alert("Error", "Fallo al enviar a la base de datos."));
  };

  const abrirCamara = () => {
    if (!permisoCamara?.granted) {
      pedirPermisoCamara();
      return;
    }
    setEscaneando(true);
  };

  // --- FUNCIONES DEL ALUMNO ---
  const handleGenerarQR = () => {
    if (matricula.trim() === '') {
      Alert.alert("Error", "Por favor ingresa tu matrícula.");
      return;
    }
    setQrGenerado(matricula.trim().toUpperCase());
  };

  // VISTA DE LA CÁMARA
  if (escaneando) {
    return (
      <View style={styles.container}>
        <CameraView 
          style={StyleSheet.absoluteFill} 
          facing="back"
          onBarcodeScanned={handleEscanearQR}
          barcodeScannerSettings={{ barcodeTypes: ["qr"] }}
        />
        <TouchableOpacity style={styles.botonCancelar} onPress={() => setEscaneando(false)}>
          <Text style={styles.textoBoton}>Cancelar Escáner</Text>
        </TouchableOpacity>
      </View>
    );
  }

  // PANTALLA PRINCIPAL
  return (
    <View style={styles.container}>
      <Text style={styles.titulo}>Colegio Universitario</Text>
      <Text style={styles.subtitulo}>Control de Asistencia</Text>

      <View style={styles.selectorContainer}>
        <TouchableOpacity 
          style={[styles.botonSelector, tipoUsuario === 'maestro' && styles.botonActivo]}
          onPress={() => setTipoUsuario('maestro')}
        >
          <Text style={[styles.textoSelector, tipoUsuario === 'maestro' && {color: 'white'}]}>Soy Maestro</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.botonSelector, tipoUsuario === 'alumno' && styles.botonActivo]}
          onPress={() => {
            setTipoUsuario('alumno');
            setQrGenerado(null);
          }}
        >
          <Text style={[styles.textoSelector, tipoUsuario === 'alumno' && {color: 'white'}]}>Soy Alumno</Text>
        </TouchableOpacity>
      </View>

      {/* ---------------- FORMULARIO DE MAESTRO ---------------- */}
      {tipoUsuario === 'maestro' && !sesionIniciada && (
        <View style={styles.formulario}>
          <Text style={styles.label}>ID de Maestro:</Text>
          <TextInput style={styles.input} placeholder="Ej. 1001" value={idMaestro} onChangeText={setIdMaestro} keyboardType="numeric" />
          <Text style={styles.label}>Código de Acceso Único:</Text>
          <TextInput style={styles.input} placeholder="Ingresa el código" value={codigo} onChangeText={setCodigo} secureTextEntry />
          <TouchableOpacity style={styles.botonPrincipal} onPress={handleLoginMaestro}>
            <Text style={styles.textoBoton}>Iniciar Sesión</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* PANEL DEL MAESTRO AUTENTICADO */}
      {tipoUsuario === 'maestro' && sesionIniciada && (
        <View style={styles.formulario}>
          <Text style={styles.label}>¡Bienvenido, Maestro!</Text>
          <Text style={{marginBottom: 20}}>Usa el botón de abajo para escanear el código de los alumnos.</Text>
          <TouchableOpacity style={styles.botonPrincipal} onPress={abrirCamara}>
            <Text style={styles.textoBoton}>📷 Abrir Cámara</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.botonPrincipal, {backgroundColor: '#EF4444', marginTop: 10}]} onPress={() => setSesionIniciada(false)}>
            <Text style={styles.textoBoton}>Cerrar Sesión</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* ---------------- FORMULARIO DE ALUMNO ---------------- */}
      {tipoUsuario === 'alumno' && (
        <View style={styles.formulario}>
          <Text style={styles.label}>Matrícula del Alumno:</Text>
          <TextInput style={styles.input} placeholder="Ej. ALU24001" value={matricula} onChangeText={setMatricula} autoCapitalize="characters" />
          <TouchableOpacity style={styles.botonPrincipalSecundario} onPress={handleGenerarQR}>
            <Text style={styles.textoBoton}>Mostrar mi código QR</Text>
          </TouchableOpacity>
          {qrGenerado && (
            <View style={styles.qrContainer}>
              <Text style={styles.textoInstruccion}>Muestra este código al profesor:</Text>
              <View style={styles.qrMarco}>
                <QRCode value={qrGenerado} size={180} />
              </View>
            </View>
          )}
        </View>
      )}
    </View>
  );
}

// ESTILOS
const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F3F4F6', padding: 20, justifyContent: 'center' },
  titulo: { fontSize: 28, fontWeight: 'bold', textAlign: 'center', color: '#1F2937' },
  subtitulo: { fontSize: 16, textAlign: 'center', color: '#6B7280', marginBottom: 30 },
  selectorContainer: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 20 },
  botonSelector: { flex: 1, padding: 15, backgroundColor: '#E5E7EB', borderRadius: 10, marginHorizontal: 5, alignItems: 'center' },
  botonActivo: { backgroundColor: '#3B82F6' },
  textoSelector: { fontWeight: 'bold', color: '#374151' },
  formulario: { backgroundColor: 'white', padding: 20, borderRadius: 15, elevation: 3 },
  label: { fontSize: 16, marginBottom: 8, color: '#4B5563', fontWeight: '500' },
  input: { borderWidth: 1, borderColor: '#D1D5DB', borderRadius: 8, padding: 15, marginBottom: 20, fontSize: 16, backgroundColor: '#F9FAFB' },
  botonPrincipal: { backgroundColor: '#10B981', padding: 15, borderRadius: 10, alignItems: 'center' },
  botonPrincipalSecundario: { backgroundColor: '#F59E0B', padding: 15, borderRadius: 10, alignItems: 'center' },
  botonCancelar: { position: 'absolute', bottom: 50, alignSelf: 'center', backgroundColor: '#EF4444', padding: 15, borderRadius: 10 },
  textoBoton: { color: 'white', fontSize: 18, fontWeight: 'bold' },
  qrContainer: { marginTop: 30, alignItems: 'center' },
  textoInstruccion: { fontSize: 16, color: '#059669', fontWeight: 'bold', marginBottom: 15 },
  qrMarco: { padding: 15, backgroundColor: 'white', borderWidth: 2, borderColor: '#E5E7EB', borderRadius: 10, elevation: 2 }
});