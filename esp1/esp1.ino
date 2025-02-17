#include <WiFi.h>
#include <HTTPClient.h>

// WLAN-Zugangsdaten
const char* ssid = "Gravity";
const char* password = "joulian_.";

// URL des Servers
const String serverUrl = "http://localhost:5000/update";  // Ersetze localhost durch die IP-Adresse des Servers, wenn du es von einem anderen Gerät verwendest

void setup() {
  // Serielle Verbindung starten
  Serial.begin(115200);

  // Mit WLAN verbinden
  WiFi.begin(ssid, password);
  Serial.print("Verbinde mit WLAN");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("Verbunden!");

  // HTTP-Request
  sendUpdateRequest("sperre");  // Beispiel: Sende "sperre" als Sign-Parameter
}

void loop() {
  // Hier kannst du die Logik für den Periodischen Update-Request hinzufügen, falls notwendig
}

// Funktion zum Senden der HTTP POST-Anfrage
void sendUpdateRequest(String sign) {
  if(WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl); // Server URL
    http.addHeader("Content-Type", "application/x-www-form-urlencoded"); // Header festlegen

    // POST-Daten
    String httpRequestData = "sign=" + sign;

    // Sende POST-Anfrage
    int httpResponseCode = http.POST(httpRequestData);
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Antwort: " + response);
    } else {
      Serial.println("Fehler bei der Anfrage: " + String(httpResponseCode));
    }

    http.end(); // Verbindung schließen
  } else {
    Serial.println("Fehler: Keine Verbindung mit WLAN");
  }
}
