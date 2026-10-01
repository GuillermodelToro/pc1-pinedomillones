"""Dashboard IoT + analítica (Streamlit Community Cloud). Lee los datos desde la API en Vercel."""
import pandas as pd, plotly.express as px, streamlit as st, requests

st.set_page_config(page_title="Dashboard Foco IoT", layout="wide")
API = st.secrets.get("API_URL", "https://TU-PROYECTO.vercel.app").rstrip("/") + "/api"

st.title("💡 Dashboard IoT – Foco LED (ESP32 + Wokwi)")

# --- Control del foco ---
c1, c2, c3, c4 = st.columns(4)
if c1.button("Encender"): requests.post(f"{API}/comando/ON", timeout=10)
if c2.button("Apagar"): requests.post(f"{API}/comando/OFF", timeout=10)
if c3.button("Consultar estado"): requests.post(f"{API}/comando/STATUS", timeout=10)
if c4.button("🔄 Actualizar"): st.rerun()

# --- Carga de datos con Pandas ---
df = pd.DataFrame(requests.get(f"{API}/historial", timeout=15).json())
est = pd.DataFrame(requests.get(f"{API}/estado", timeout=15).json())

if df.empty:
    st.warning("Aún no hay operaciones registradas.")
    st.stop()

df["fecha_hora"] = pd.to_datetime(df["fecha_hora"])
df = df.sort_values("fecha_hora", ascending=False)

estado_actual = est["estado"].iloc[0] if not est.empty else "-"
ultima = df.iloc[0]
total = len(df)
encendidos = int((df["accion"] == "ENCENDER").sum())
apagados = int((df["accion"] == "APAGAR").sum())
consultas = int((df["accion"] == "CONSULTAR").sum())
tiempo_total = int(df["duracion_seg"].sum())

# --- P3: Estado e indicadores ---
st.subheader("Estado del dispositivo")
k = st.columns(4)
k[0].metric("Estado actual", "🟢 ON" if estado_actual == "ON" else "⚫ OFF")
k[1].metric("Última operación", ultima["accion"])
k[2].metric("Fecha y hora", ultima["fecha_hora"].strftime("%d/%m/%Y %H:%M:%S"))
k[3].metric("Dispositivo", ultima["dispositivo"])

st.subheader("Indicadores de operaciones")
m = st.columns(5)
m[0].metric("Total operaciones", total)
m[1].metric("Encendidos", encendidos)
m[2].metric("Apagados", apagados)
m[3].metric("Consultas de estado", consultas)
m[4].metric("Tiempo total encendido", f"{tiempo_total} s")

# --- P4: Analítica y gráficos ---
st.subheader("Analítica de datos")
g1, g2 = st.columns(2)
por_tipo = df["accion"].value_counts().reset_index()
por_tipo.columns = ["accion", "cantidad"]
g1.plotly_chart(px.bar(por_tipo, x="accion", y="cantidad", color="accion",
                       title="Operaciones por tipo"), use_container_width=True)
por_estado = df["estado"].value_counts().reset_index()
por_estado.columns = ["estado", "cantidad"]
g2.plotly_chart(px.pie(por_estado, names="estado", values="cantidad",
                       title="Estados del foco"), use_container_width=True)

df["hora"] = df["fecha_hora"].dt.strftime("%Y-%m-%d %H:%M")
por_hora = df.groupby("hora").size().reset_index(name="operaciones")
st.plotly_chart(px.bar(por_hora, x="hora", y="operaciones",
                       title="Operaciones por fecha y hora"), use_container_width=True)

# --- Interpretación ---
st.subheader("Interpretación de resultados")
prom = tiempo_total / apagados if apagados else 0
st.info(
    f"Se registraron **{total} operaciones**: {encendidos} encendidos, {apagados} apagados y "
    f"{consultas} consultas de estado. El foco estuvo encendido **{tiempo_total} segundos** en total, "
    f"con un promedio de **{prom:.1f} s** por ciclo de encendido. "
    f"La acción más frecuente fue **{por_tipo.iloc[0]['accion']}**. "
    f"Actualmente el foco se encuentra **{estado_actual}**."
)

st.subheader("Historial de operaciones")
st.dataframe(df.drop(columns=["hora"]), use_container_width=True)
