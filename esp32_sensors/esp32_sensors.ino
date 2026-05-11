#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <DHTesp.h>
#include <SPI.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// -------------------- LCD --------------------
LiquidCrystal_I2C lcd(0x27, 16, 2);

// -------------------- WLAN --------------------
const char* ssid = "Newton";
const char* password = "Andji1911";
const char* serverUrl = "http://172.20.10.4:5000/sensor-update";

// -------------------- DHT11 --------------------
#define DHTPIN 4
DHTesp dht;

// -------------------- ML8511 / GY-ML8511 --------------------
#define UV_PIN 34
#define EN_PIN 26

// -------------------- MS5540C --------------------
#define PIN_MCLK 25
#define PIN_MOSI 23
#define PIN_MISO 19
#define PIN_SCLK 18

unsigned long lastReadTime = 0;
const unsigned long readInterval = 10000;

// -------------------- MS5540C Kalibrierwerte --------------------
uint16_t W1, W2, W3, W4;
int32_t C1, C2, C3, C4, C5, C6;

SPISettings msSettings(500000, MSBFIRST, SPI_MODE1);

void ensureWifiConnection();

void lcdMessage(const String& line1, const String& line2 = "") {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(line1.substring(0, 16));
  lcd.setCursor(0, 1);
  lcd.print(line2.substring(0, 16));
}

void showSensorValues(bool hasDhtValues, float temperatur, float luftfeuchtigkeit, float druck, int uv) {
  lcd.clear();

  lcd.setCursor(0, 0);
  if (hasDhtValues) {
    lcd.print("T:");
    lcd.print(temperatur, 1);
    lcd.print(" P:");
    lcd.print(druck, 0);
  } else {
    lcd.print("T:Err P:");
    lcd.print(druck, 0);
  }

  lcd.setCursor(0, 1);
  lcd.print("U:");
  lcd.print(uv);

  if (hasDhtValues) {
    lcd.print(" H:");
    lcd.print(luftfeuchtigkeit, 0);
  } else {
    lcd.print(" H:Err");
  }
}

void connectWifi() {
  Serial.print("Verbinde mit WLAN");
  lcdMessage("WLAN verbindet", "...");

  WiFi.begin(ssid, password);

  int tries = 0;
  while (WiFi.status() != WL_CONNECTED && tries < 30) {
    delay(500);
    Serial.print(".");
    tries++;
  }

  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("WLAN verbunden");
    Serial.print("IP-Adresse: ");
    Serial.println(WiFi.localIP());

    lcdMessage("WLAN verbunden", WiFi.localIP().toString());
    delay(2000);
  } else {
    Serial.println("WLAN Verbindung fehlgeschlagen");
    lcdMessage("WLAN Fehler", "nicht verbunden");
    delay(2000);
  }
}

void ms5540Reset() {
  SPI.beginTransaction(msSettings);
  SPI.transfer(0x15);
  SPI.transfer(0x55);
  SPI.transfer(0x40);
  SPI.endTransaction();
  delay(10);
}

uint16_t ms5540ReadWord(byte command1, byte command2) {
  SPI.beginTransaction(msSettings);
  SPI.transfer(command1);
  SPI.transfer(command2);
  byte highByte = SPI.transfer(0x00);
  byte lowByte = SPI.transfer(0x00);
  SPI.endTransaction();

  return ((uint16_t)highByte << 8) | lowByte;
}

uint16_t ms5540ReadADC(byte command1, byte command2) {
  SPI.beginTransaction(msSettings);
  SPI.transfer(command1);
  SPI.transfer(command2);
  delay(40);
  byte highByte = SPI.transfer(0x00);
  byte lowByte = SPI.transfer(0x00);
  SPI.endTransaction();

  return ((uint16_t)highByte << 8) | lowByte;
}

void ms5540ReadCalibration() {
  ms5540Reset();

  W1 = ms5540ReadWord(0x1D, 0x50);
  W2 = ms5540ReadWord(0x1D, 0x60);
  W3 = ms5540ReadWord(0x1D, 0x90);
  W4 = ms5540ReadWord(0x1D, 0xA0);

  C1 = W1 >> 1;
  C5 = ((W1 & 0x0001) << 10) | (W2 >> 6);
  C6 = W2 & 0x003F;
  C4 = W3 >> 6;
  C2 = ((W3 & 0x003F) << 6) | (W4 & 0x003F);
  C3 = W4 >> 6;
}

float ms5540ReadPressure() {
  uint16_t D1 = ms5540ReadADC(0x0F, 0x40);
  uint16_t D2 = ms5540ReadADC(0x0F, 0x20);

  int32_t UT1 = 8 * C5 + 20224;
  int32_t dT = D2 - UT1;

  int32_t OFF = C2 * 4 + (((C4 - 512) * dT) >> 12);
  int32_t SENS = C1 + ((C3 * dT) >> 10) + 24576;

  int32_t X = ((SENS * ((int32_t)D1 - 7168)) >> 14) - OFF;
  int32_t P = ((X * 10) >> 5) + 2500;

  return P / 10.0;
}

int readUvRaw() {
  digitalWrite(EN_PIN, HIGH);
  delay(10);
  return analogRead(UV_PIN);
}

void sendSensorData(bool hasDhtValues, float temperatur, float luftfeuchtigkeit, float druck, int uv) {
  ensureWifiConnection();

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.setTimeout(4000);
    http.addHeader("Content-Type", "application/json");

    String json = "{";
    json += "\"uv\":" + String(uv) + ",";
    json += "\"druck\":" + String(druck, 1);

    if (hasDhtValues) {
      json += ",\"temperatur\":" + String(temperatur, 1);
      json += ",\"luftfeuchtigkeit\":" + String(luftfeuchtigkeit, 1);
    }

    json += "}";

    Serial.println("Sende JSON:");
    Serial.println(json);

    lcdMessage("Sende Daten...", "bitte warten");

    int httpResponseCode = http.POST(json);

    Serial.print("HTTP Response Code: ");
    Serial.println(httpResponseCode);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Server Antwort:");
      Serial.println(response);

      lcdMessage("Senden OK", "Code:" + String(httpResponseCode));
      delay(2000);
    } else {
      Serial.print("Fehler beim Senden: ");
      Serial.println(http.errorToString(httpResponseCode));

      lcdMessage("Sendefehler", "Code:" + String(httpResponseCode));
      delay(2500);
    }

    http.end();
  } else {
    lcdMessage("Kein WLAN", "nicht gesendet");
    delay(2000);
  }
}

void setup() {
  Serial.begin(115200);
  delay(2000);

  Wire.begin(21, 22);
  lcd.init();
  lcd.backlight();
  lcdMessage("System startet", "...");

  Serial.println("Starte Sensoren...");

  connectWifi();

  dht.setup(DHTPIN, DHTesp::DHT11);
  delay(2000);

  pinMode(EN_PIN, OUTPUT);
  digitalWrite(EN_PIN, HIGH);

  analogReadResolution(12);
  analogSetPinAttenuation(UV_PIN, ADC_11db);

  pinMode(PIN_MCLK, OUTPUT);
  ledcAttach(PIN_MCLK, 32768, 8);
  ledcWrite(PIN_MCLK, 128);

  SPI.begin(PIN_SCLK, PIN_MISO, PIN_MOSI, -1);

  ms5540ReadCalibration();

  Serial.println("Sensoren gestartet");
  lcdMessage("Sensoren bereit", "warte...");
  lastReadTime = millis() - readInterval;
}

void loop() {
  ensureWifiConnection();

  if (millis() - lastReadTime >= readInterval) {
    lastReadTime = millis();

    TempAndHumidity data = dht.getTempAndHumidity();
    float pressure = ms5540ReadPressure();
    int uvRaw = readUvRaw();

    Serial.println("-------------------------");

    float temperatur = NAN;
    float luftfeuchtigkeit = NAN;
    bool hasDhtValues = false;

    if (dht.getStatus() != 0) {
      Serial.print("DHT11 Fehler: ");
      Serial.println(dht.getStatusString());
      Serial.println("Temperatur: Fehler");
      Serial.println("Luftfeuchtigkeit: Fehler");
    } else {
      temperatur = data.temperature;
      luftfeuchtigkeit = data.humidity;
      hasDhtValues = true;

      Serial.print("Temperatur: ");
      Serial.print(temperatur, 1);
      Serial.println(" °C");

      Serial.print("Luftfeuchtigkeit: ");
      Serial.print(luftfeuchtigkeit, 1);
      Serial.println(" %");
    }

    Serial.print("Druck: ");
    Serial.print(pressure, 1);
    Serial.println(" mbar");

    Serial.print("UV Rohwert: ");
    Serial.println(uvRaw);

    showSensorValues(hasDhtValues, temperatur, luftfeuchtigkeit, pressure, uvRaw);
    delay(4000);

    if (hasDhtValues) {
      sendSensorData(true, temperatur, luftfeuchtigkeit, pressure, uvRaw);
    } else {
      Serial.println("DHT11 ungültig, sende Druck und UV trotzdem.");
      sendSensorData(false, temperatur, luftfeuchtigkeit, pressure, uvRaw);
    }

    lcdMessage("Warte auf", "naechste Messung");
  }
}

void ensureWifiConnection() {
  if (WiFi.status() == WL_CONNECTED) {
    return;
  }

  Serial.println("WLAN weg, verbinde neu...");
  lcdMessage("WLAN weg", "verbinde neu");
  WiFi.disconnect(true, true);
  delay(250);
  connectWifi();
}