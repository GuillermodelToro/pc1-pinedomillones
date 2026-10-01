# Sistema IoT – Foco LED (ESP32 + Wokwi)

Práctica Calificada 1 – Diseño e Implementación en Ambientes Emergentes (USIL).

**Flujo:** App React Native / Dashboard → API (Vercel, FastAPI) → MQTT (broker.emqx.io) → ESP32 en Wokwi (LED) → API `/api/registrar` → Supabase (PostgreSQL) → App y Dashboard.

| Componente | Carpeta | Despliegue |
|---|---|---|
| ESP32 + LED (P2) | `esp32/` | Wokwi |
| App React Native – registro e historial (P1) | `app/` | Vercel (Expo web) |
| Backend API REST (P1, P2) | `api/index.py` | Vercel (Python) – docs en `/api/docs` |
| Base de datos (P1) | `supabase/schema.sql` | Supabase |
| Dashboard + analítica con Pandas (P3, P4) | `dashboard/app.py` | Streamlit Community Cloud |

**Endpoints:** `POST /api/comando/{ON|OFF|STATUS}`, `POST /api/registrar`, `GET /api/estado`, `GET /api/historial`.
