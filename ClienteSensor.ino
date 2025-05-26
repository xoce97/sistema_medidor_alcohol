#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "TU_WIFI";
const char* password = "TU_PASSWORD";
const char* serverEstado = "http://TU_IP_DJANGO/estado-medicion/";
const char* serverDatos = "http://TU_IP_DJANGO/recibir-datos-api/";

void setup() {
    Serial.begin(115200);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
}

void loop() {
    if (WiFi.status() == WL_CONNECTED && debeMedir()) {
        float valorAnalogico = analogRead(34); // Ajusta el pin
        enviarDatos(valorAnalogico);
    }
    delay(1000); // Ajusta el intervalo
}

bool debeMedir() {
    HTTPClient http;
    http.begin(serverEstado);
    int httpCode = http.GET();
    
    if (httpCode == HTTP_CODE_OK) {
        String payload = http.getString();
        return payload.indexOf("\"activa\":true") != -1;
    }
    return false;
}

void enviarDatos(float valor) {
    HTTPClient http;
    http.begin(serverDatos);
    http.addHeader("Content-Type", "application/json");
    
    String jsonData = "{\"empleado_id\":\"123\", \"valor_analogico\":" + String(valor) + 
                     ", \"voltaje\":" + String(valor*0.0049) + 
                     ", \"alcohol_ppm\":" + String(valor*0.8) + "}";
    
    int httpCode = http.POST(jsonData);
    if (httpCode != HTTP_CODE_OK) {
        Serial.println("Error enviando datos");
    }
    http.end();
}