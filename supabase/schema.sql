-- Ejecutar en Supabase > SQL Editor
CREATE TABLE IF NOT EXISTS operaciones (
  id            BIGSERIAL PRIMARY KEY,
  fecha_hora    TIMESTAMP NOT NULL DEFAULT NOW(),
  accion        VARCHAR(20) NOT NULL,      -- ENCENDER / APAGAR / CONSULTAR
  estado        VARCHAR(10) NOT NULL,      -- ON / OFF
  dispositivo   VARCHAR(50) NOT NULL,
  duracion_seg  INTEGER NOT NULL DEFAULT 0 -- segundos encendido
);

CREATE TABLE IF NOT EXISTS dispositivo_estado (
  dispositivo   VARCHAR(50) PRIMARY KEY,
  estado        VARCHAR(10) NOT NULL,
  ultimo_cambio TIMESTAMP NOT NULL DEFAULT NOW()
);

INSERT INTO dispositivo_estado VALUES ('ESP32-FOCO-01', 'OFF', NOW())
ON CONFLICT (dispositivo) DO NOTHING;

-- Seguridad: solo el backend (service_role) accede a las tablas
ALTER TABLE operaciones ENABLE ROW LEVEL SECURITY;
ALTER TABLE dispositivo_estado ENABLE ROW LEVEL SECURITY;
