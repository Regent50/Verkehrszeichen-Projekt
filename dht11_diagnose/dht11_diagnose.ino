#include <Arduino.h>
#include <DHTesp.h>

// -------------------- DHT11 Test --------------------
#define DHTPIN 17

DHTesp dht;
unsigned long lastReadTime = 0;
const unsigned long readInterval = 3000;

void setup() {
  Serial.begin(115200);
  delay(2000);

  Serial.println();
  Serial.println("=== DHT11 Diagnose gestartet ===");
  Serial.print("Verwendeter Datenpin: GPIO ");
  Serial.println(DHTPIN);

  dht.setup(DHTPIN, DHTesp::DHT11);

  delay(1500);
  Serial.println("Sensor initialisiert. Lese alle 3 Sekunden...");
  Serial.println("Wenn dauerhaft TIMEOUT kommt: Verkabelung / Pull-up / Sensor pruefen.");
}

void loop() {
  if (millis() - lastReadTime < readInterval) {
    return;
  }

  lastReadTime = millis();

  TempAndHumidity data = dht.getTempAndHumidity();

  Serial.println("-------------------------");

  if (dht.getStatus() != 0) {
    Serial.print("DHT11 Fehlercode: ");
    Serial.println(dht.getStatus());
    Serial.print("DHT11 Fehlertext: ");
    Serial.println(dht.getStatusString());
    Serial.println("Keine gueltigen Messwerte.");
    return;
  }

  Serial.print("Temperatur: ");
  Serial.print(data.temperature, 1);
  Serial.println(" °C");

  Serial.print("Luftfeuchtigkeit: ");
  Serial.print(data.humidity, 1);
  Serial.println(" %");

  if (isnan(data.temperature) || isnan(data.humidity)) {
    Serial.println("Warnung: Messung kam als NaN zurueck.");
  } else {
    Serial.println("DHT11 Messung erfolgreich.");
  }
}
