#include <WiFi.h>
#include <HTTPClient.h>

// WLAN-Zugangsdaten
const char* ssid = "Gravity";
const char* password = "joulian_.";

// URL des Servers
const String serverUrl = "http://172.20.10.4:5000/update";

// Variable to store current sign
String currentSign = "";

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
}

void loop() {
  // Check for new sign input from serial
  if (Serial.available()) {
    String newSign = Serial.readStringUntil('\n');
    newSign.trim();
    if (newSign.length() > 0 && newSign != currentSign) {
      if (sendUpdateRequest(newSign)) {
        currentSign = newSign;
        Serial.println("Sign updated to: " + currentSign);
      }
    }
  }
  
  // Add any periodic checks or sensor readings here
  delay(100); // Small delay to prevent CPU overload
}


// Funktion zum Senden der HTTP POST-Anfrage
bool sendUpdateRequest(String sign) {
  if(WiFi.status() != WL_CONNECTED) {
    Serial.println("Fehler: Keine Verbindung mit WLAN");
    return false;
  }

  HTTPClient http;
  if (!http.begin(serverUrl)) {
    Serial.println("Fehler: Konnte keine Verbindung zum Server herstellen");
    return false;
  }

  http.addHeader("Content-Type", "application/x-www-form-urlencoded");
  String httpRequestData = "sign=" + sign;

  int httpResponseCode = http.POST(httpRequestData);
  bool success = false;
  
  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.println("Antwort vom Server: " + response);
    if (httpResponseCode == 200) {
      success = true;
    }
  } else {
    Serial.println("Fehler bei der Anfrage: " + String(httpResponseCode));
  }

  http.end();
  return success;
}
