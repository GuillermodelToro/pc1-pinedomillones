#include <WiFi.h>
#include <PubSubClient.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>

// --- Configuración WiFi, MQTT y API ---
const char* SSID   = "Wokwi-GUEST";
const char* PASS   = "";
const char* BROKER = "broker.emqx.io";
// CAMBIA ESTO por la URL de tu proyecto en Vercel:
const char* API_REGISTRAR = "https://TU-PROYECTO.vercel.app/api/registrar";

const char* TOPIC_CMD    = "usil/wpinedo/foco/cmd";     // recibe: ON / OFF / STATUS
const char* TOPIC_ESTADO = "usil/wpinedo/foco/estado";  // envía: JSON con el estado
const char* DISPOSITIVO  = "ESP32-FOCO-01";
const char* CLIENT_ID    = "wpinedo-esp32-foco-01";

const int LED_PIN = 2;   // LED que representa el foco
bool ledOn = false;

WiFiClient espClient;
PubSubClient client(espClient);

// Envía la operación al backend (Vercel) para guardarla en Supabase
void registrarEnApi(const char* json) {
  WiFiClientSecure https;
  https.setInsecure();               // simulación: sin validar certificado
  HTTPClient http;
  http.begin(https, API_REGISTRAR);
  http.addHeader("Content-Type", "application/json");
  int code = http.POST(json);
  Serial.print("API registrar -> HTTP ");
  Serial.println(code);
  http.end();
}

// Publica el estado por MQTT y lo registra en la API
void publicarEstado(const char* accion, bool registrar = true) {
  char msg[150];
  snprintf(msg, sizeof(msg),
    "{\"dispositivo\":\"%s\",\"accion\":\"%s\",\"estado\":\"%s\"}",
    DISPOSITIVO, accion, ledOn ? "ON" : "OFF");
  client.publish(TOPIC_ESTADO, msg);
  Serial.println(msg);
  if (registrar) registrarEnApi(msg);
}

// Procesa las instrucciones recibidas
void callback(char* topic, byte* payload, unsigned int length) {
  String cmd;
  for (unsigned int i = 0; i < length; i++) cmd += (char)payload[i];
  cmd.trim();
  cmd.toUpperCase();
  Serial.print("Comando recibido: ");
  Serial.println(cmd);

  if (cmd == "ON") {
    ledOn = true;  digitalWrite(LED_PIN, HIGH); publicarEstado("ENCENDER");
  } else if (cmd == "OFF") {
    ledOn = false; digitalWrite(LED_PIN, LOW);  publicarEstado("APAGAR");
  } else if (cmd == "STATUS") {
    publicarEstado("CONSULTAR");
  } else {
    Serial.println("Comando no valido");
  }
}

void reconectar() {
  while (!client.connected()) {
    Serial.print("Conectando a MQTT... ");
    if (client.connect(CLIENT_ID)) {
      Serial.println("OK");
      client.subscribe(TOPIC_CMD);
      publicarEstado("CONECTADO", false);
    } else {
      Serial.print("fallo, estado=");
      Serial.println(client.state());
      delay(2000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  WiFi.begin(SSID, PASS, 6);
  Serial.print("Conectando WiFi");
  while (WiFi.status() != WL_CONNECTED) { delay(300); Serial.print("."); }
  Serial.println(" OK");

  client.setServer(BROKER, 1883);
  client.setCallback(callback);
  client.setKeepAlive(60);
}

void loop() {
  if (!client.connected()) reconectar();
  client.loop();
}
