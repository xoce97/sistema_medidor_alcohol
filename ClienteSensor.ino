#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <WebServer.h>

const char* ssid = "babychulos";
const char* password = "6478BA0D88";
const char* serverEstado = "http://192.168.1.72:8000/api/estado-medicion/";
const char* serverDatos = "http://192.168.1.72:8000/api/recibir-datos/";
int empleadoId = 0;
String empleadoNombre = "";
WebServer server(80);

void setup() {
    Serial.begin(115200);

    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nConectado al WiFi");
    Serial.print("IP ESP32: ");
    Serial.println(WiFi.localIP());

    // Endpoints
    server.on("/actualizar-usuario", HTTP_POST, handleActualizarUsuario);
    server.on("/control-medicion", HTTP_POST, handleControlMedicion);

    server.begin();
    Serial.println("Servidor web iniciado");
}

void loop() {
    server.handleClient();

    if (WiFi.status() == WL_CONNECTED && empleadoId != 0 && debeMedir()) {
        float valor = analogRead(34);
        enviarDatos(valor);
    }

    delay(1000);
}

void handleControlMedicion() {
    if (server.method() == HTTP_POST) {
        String body = server.arg("plain");
        Serial.println("Body recibido en /control-medicion:");
        Serial.println(body);

        DynamicJsonDocument doc(256);
        DeserializationError error = deserializeJson(doc, body);

        if (error) {
            server.send(400, "application/json", "{\"error\":\"JSON inválido\"}");
            return;
        }

        empleadoId = doc["empleado_id"];
        empleadoNombre = doc["nombre"].as<String>();

        Serial.printf("Medición iniciada para: ID=%d, Nombre=%s\n", empleadoId, empleadoNombre.c_str());

        // ✅ Respuesta JSON bien formateada
        DynamicJsonDocument responseDoc(128);
        responseDoc["status"] = "ok";

        String responseBody;
        serializeJson(responseDoc, responseBody);
        server.send(200, "application/json", responseBody);
    } else {
        server.send(405, "application/json", "{\"error\":\"Método no permitido\"}");
    }
}

void handleActualizarUsuario() {
    if (server.method() == HTTP_POST) {
        String body = server.arg("plain");
        DynamicJsonDocument doc(256);
        DeserializationError error = deserializeJson(doc, body);

        if (error) {
            server.send(400, "application/json", "{\"error\":\"JSON inválido\"}");
            return;
        }

        empleadoId = doc["empleado_id"];
        empleadoNombre = doc["nombre"].as<String>();

        Serial.printf("Usuario actualizado: ID=%d, Nombre=%s\n", empleadoId, empleadoNombre.c_str());

        DynamicJsonDocument responseDoc(128);
        responseDoc["status"] = "ok";

        String responseBody;
        serializeJson(responseDoc, responseBody);
        server.send(200, "application/json", responseBody);
    } else {
        server.send(405, "application/json", "{\"error\":\"Método no permitido\"}");
    }
}

bool debeMedir() {
    if (empleadoId == 0) return false;  // No se ha configurado el usuario

    HTTPClient http;

    // Construir URL con el parámetro empleado_id
    String url = String(serverEstado) + "?empleado_id=" + empleadoId;
    Serial.println("Consultando URL: " + url);

    http.begin(url);
    int httpCode = http.GET();

    if (httpCode == HTTP_CODE_OK) {
        String payload = http.getString();
        Serial.println("Respuesta de /estado-medicion: " + payload);

        DynamicJsonDocument doc(128);
        DeserializationError error = deserializeJson(doc, payload);

        if (error) {
            Serial.println("Error al parsear JSON de /estado-medicion");
            return false;
        }

        return doc["activa"];
    } else {
        Serial.print("Error en GET /estado-medicion: ");
        Serial.println(httpCode);
    }

    http.end();
    return false;
}

void enviarDatos(float valor) {
    HTTPClient http;
    http.begin(serverDatos);
    http.addHeader("Content-Type", "application/json");

    DynamicJsonDocument doc(256);
    doc["empleado_id"] = empleadoId;
    doc["valor_analogico"] = valor;
    doc["voltaje"] = valor * 0.0049;
    doc["alcohol_ppm"] = valor * 0.8;

    String jsonData;
    serializeJson(doc, jsonData);

    int httpCode = http.POST(jsonData);
    if (httpCode == HTTP_CODE_OK) {
        Serial.println("Datos enviados correctamente");
    } else {
        Serial.print("Error enviando datos: ");
        Serial.println(httpCode);
    }

    http.end();
}
