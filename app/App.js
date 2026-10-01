import { useEffect, useState } from 'react';
import { View, Text, TouchableOpacity, FlatList, StyleSheet, ScrollView } from 'react-native';

// La API (backend) está en el mismo dominio de Vercel: /api/...
const API = '/api';

export default function App() {
  const [estado, setEstado] = useState('...');
  const [historial, setHistorial] = useState([]);
  const [mensaje, setMensaje] = useState('');

  // Consulta el estado actual y el historial registrado en Supabase
  const cargar = async () => {
    try {
      const e = await (await fetch(`${API}/estado`)).json();
      setEstado(e[0]?.estado ?? '-');
      setHistorial(await (await fetch(`${API}/historial`)).json());
    } catch (err) {
      setMensaje('No se pudo conectar con la API');
    }
  };

  // Envía la instrucción al ESP32 (vía API -> MQTT)
  const enviar = async (cmd) => {
    setMensaje(`Enviando ${cmd} al ESP32...`);
    await fetch(`${API}/comando/${cmd}`, { method: 'POST' });
    setTimeout(() => { cargar(); setMensaje(''); }, 4000); // espera la respuesta del ESP32
  };

  useEffect(() => {
    cargar();
    const t = setInterval(cargar, 5000); // refresco automático
    return () => clearInterval(t);
  }, []);

  return (
    <ScrollView style={s.container}>
      <Text style={s.titulo}>💡 Registro de Operaciones – Foco LED</Text>
      <Text style={s.estado}>Estado actual: {estado === 'ON' ? '🟢 ON' : '⚫ OFF'}</Text>

      <View style={s.fila}>
        <TouchableOpacity style={[s.btn, { backgroundColor: '#16a34a' }]} onPress={() => enviar('ON')}><Text style={s.btnTxt}>Encender</Text></TouchableOpacity>
        <TouchableOpacity style={[s.btn, { backgroundColor: '#dc2626' }]} onPress={() => enviar('OFF')}><Text style={s.btnTxt}>Apagar</Text></TouchableOpacity>
        <TouchableOpacity style={[s.btn, { backgroundColor: '#2563eb' }]} onPress={() => enviar('STATUS')}><Text style={s.btnTxt}>Consultar</Text></TouchableOpacity>
        <TouchableOpacity style={[s.btn, { backgroundColor: '#6b7280' }]} onPress={cargar}><Text style={s.btnTxt}>Ver historial</Text></TouchableOpacity>
      </View>
      {mensaje ? <Text style={s.msg}>{mensaje}</Text> : null}

      <Text style={s.sub}>Historial de operaciones</Text>
      <View style={[s.item, { backgroundColor: '#e5e7eb' }]}>
        <Text style={s.col}>Fecha y hora</Text><Text style={s.col}>Acción</Text>
        <Text style={s.col}>Estado</Text><Text style={s.col}>Dispositivo</Text><Text style={s.col}>Duración (s)</Text>
      </View>
      <FlatList
        data={historial}
        keyExtractor={(i) => String(i.id)}
        renderItem={({ item }) => (
          <View style={s.item}>
            <Text style={s.col}>{String(item.fecha_hora).replace('T', ' ').slice(0, 19)}</Text>
            <Text style={s.col}>{item.accion}</Text>
            <Text style={s.col}>{item.estado}</Text>
            <Text style={s.col}>{item.dispositivo}</Text>
            <Text style={s.col}>{item.duracion_seg}</Text>
          </View>
        )}
      />
    </ScrollView>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, padding: 24, backgroundColor: '#f9fafb' },
  titulo: { fontSize: 24, fontWeight: 'bold', marginBottom: 12 },
  estado: { fontSize: 20, marginBottom: 16 },
  fila: { flexDirection: 'row', gap: 10, marginBottom: 12, flexWrap: 'wrap' },
  btn: { paddingVertical: 10, paddingHorizontal: 18, borderRadius: 8 },
  btnTxt: { color: '#fff', fontWeight: 'bold' },
  msg: { color: '#2563eb', marginBottom: 12 },
  sub: { fontSize: 18, fontWeight: 'bold', marginVertical: 8 },
  item: { flexDirection: 'row', paddingVertical: 6, borderBottomWidth: 1, borderColor: '#ddd' },
  col: { flex: 1, fontSize: 13 },
});
