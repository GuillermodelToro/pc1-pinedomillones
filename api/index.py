"""
Backend (API REST) del sistema IoT – desplegado en Vercel (FastAPI).
- Recibe comandos de la app/dashboard y los publica por MQTT al ESP32.
- Recibe las confirmaciones del ESP32 (/api/registrar) y las guarda en Supabase (PostgreSQL).
- Entrega estado e historial a la app React Native y al dashboard Streamlit.
"""
import os
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
import paho.mqtt.publish as publish
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ---------- Configuración ----------
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
REST = f"{SUPABASE_URL}/rest/v1"
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}
BROKER = "broker.emqx.io"
TOPIC_CMD = "usil/wpinedo/foco/cmd"
TZ = ZoneInfo("America/Lima")


def ahora():
    return datetime.now(TZ).replace(tzinfo=None)


def db_get(tabla, params):
    r = requests.get(f"{REST}/{tabla}", headers=HEADERS, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def db_insert(tabla, data):
    r = requests.post(f"{REST}/{tabla}", headers=HEADERS, json=data, timeout=10)
    r.raise_for_status()


def db_update(tabla, filtro, data):
    r = requests.patch(f"{REST}/{tabla}", headers=HEADERS, params=filtro, json=data, timeout=10)
    r.raise_for_status()


# ---------- API ----------
app = FastAPI(title="API Foco IoT", docs_url="/api/docs", openapi_url="/api/openapi.json")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class Operacion(BaseModel):
    dispositivo: str
    accion: str
    estado: str


@app.get("/api")
def inicio():
    return {"servicio": "API Foco IoT", "docs": "/api/docs"}


@app.post("/api/comando/{cmd}")
def enviar_comando(cmd: str):
    """Envía ON / OFF / STATUS al ESP32 por MQTT."""
    cmd = cmd.upper()
    if cmd not in ("ON", "OFF", "STATUS"):
        raise HTTPException(400, "Comando no válido. Use ON, OFF o STATUS")
    publish.single(TOPIC_CMD, cmd, hostname=BROKER, port=1883)
    return {"enviado": cmd}


@app.post("/api/registrar")
def registrar(op: Operacion):
    """El ESP32 llama a este endpoint después de ejecutar cada instrucción."""
    if op.accion not in ("ENCENDER", "APAGAR", "CONSULTAR"):
        return {"ignorado": op.accion}

    fecha = ahora()
    filas = db_get("dispositivo_estado", {"dispositivo": f"eq.{op.dispositivo}", "select": "*"})
    fila = filas[0] if filas else None

    # Duración de funcionamiento: segundos encendido (se calcula al apagar)
    duracion = 0
    if op.accion == "APAGAR" and fila and fila["estado"] == "ON":
        inicio = datetime.fromisoformat(fila["ultimo_cambio"])
        duracion = max(0, int((fecha - inicio).total_seconds()))

    db_insert("operaciones", {
        "fecha_hora": fecha.isoformat(), "accion": op.accion, "estado": op.estado,
        "dispositivo": op.dispositivo, "duracion_seg": duracion,
    })

    # Actualiza el estado del dispositivo si cambió
    if fila is None:
        db_insert("dispositivo_estado", {"dispositivo": op.dispositivo, "estado": op.estado,
                                         "ultimo_cambio": fecha.isoformat()})
    elif fila["estado"] != op.estado:
        db_update("dispositivo_estado", {"dispositivo": f"eq.{op.dispositivo}"},
                  {"estado": op.estado, "ultimo_cambio": fecha.isoformat()})

    return {"registrado": op.accion, "estado": op.estado, "duracion_seg": duracion}


@app.get("/api/estado")
def estado():
    return db_get("dispositivo_estado", {"select": "*"})


@app.get("/api/historial")
def historial(limite: int = 500):
    return db_get("operaciones", {"select": "*", "order": "fecha_hora.desc", "limit": limite})
