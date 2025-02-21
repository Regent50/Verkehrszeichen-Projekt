#include <WiFi.h>
#include <HTTPClient.h>
#include <ESP32Lib.h>
#include <ESP32Video.h>
#include <VGA/VGA14Bit.h>
#include "image_handler.h"
#include <SocketIoClient.h>
SocketIoClient socketIO; // Use SocketIoClient instead of SocketIOclient

// WLAN-Zugangsdaten
const char* ssid = "Gravity";
const char* password = "joulian_.";

// Server URL
const String serverUrl = "http://172.20.10.4:5000/update";

// VGA instance and image handler
VGA14Bit vga;
ImageHandler imageHandler(vga);

// Socket.IO client
void socketIOEvent(socketIOmessageType_t type, uint8_t *payload, size_t length);

// Socket.IO event handler
void socketIOEvent(socketIOmessageType_t type, uint8_t * payload, size_t length) {
  if (type == sIOtype_EVENT) {
    DynamicJsonDocument doc(1024);
    DeserializationError error = deserializeJson(doc, payload, length);
    if (!error) {
      const char* event = doc[0];
      if (strcmp(event, "update_sign") == 0) {
        currentSign = doc[1].as<String>();
        Serial.println("Sign updated via Socket.IO: " + currentSign);
      }
    }
  }
}

// ✅ Correct VGA pin configuration
const int redPins[] = {13, 12, 14};
const int greenPins[] = {27, 26, 25};
const int bluePins[] = {33, 32, 15};
const int hsyncPin = 4;
const int vsyncPin = 2;

// Variable to store current sign
String currentSign = "";

void setup() {
  Serial.begin(115200);

  // ✅ Correct VGA initialization
  vga.init(vga.MODE320x240, redPins, greenPins, bluePins, hsyncPin, vsyncPin);
  vga.clear(vga.RGB(0, 0, 0));

  // ✅ Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("Verbinde mit WLAN");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nVerbunden!");

  // ✅ Connect to Socket.IO server
  socketIO.begin("c847-193-171-62-34", 5000, "/socket.io/?EIO=4");
  socketIO.onEvent(SocketIOEvent);
}

void loop() {
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
  
  socketIO.loop();

  renderWebsite();
  delay(100);
}

// ✅ Send sign update request to the server
bool sendUpdateRequest(String sign) {
  if (WiFi.status() != WL_CONNECTED) {
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
  bool success = (httpResponseCode == 200);
  
  if (httpResponseCode > 0) {
    Serial.println("Antwort vom Server: " + http.getString());
  } else {
    Serial.println("Fehler bei der Anfrage: " + String(httpResponseCode));
  }

  http.end();
  return success;
}

// ✅ Map sign names to image filenames
const char* getImageForSign(const String& sign) {
  if (sign == "STOP") return "stop_schild.png";
  if (sign == "Geschwindigkeit 50") return "50kmh_schild.png";
  if (sign == "Achtung Baustelle") return "baustelle_schild.png";
  if (sign == "Freie Fahrt") return "freifahrt_schild.png";
  return "";
}

int currentSignIndex = 0;

// ✅ Display the sign on the VGA screen
void renderWebsite() {
  vga.clear(vga.RGB(0, 0, 0));
  
  // Build image URL based on current sign
  const char* imageName = getImageForSign(currentSign);
  
  if (imageName != nullptr && strlen(imageName) > 0) {
    String imageUrl = "http://172.20.10.4:5000/get_image/" + String(imageName);

    if (imageHandler.displayImage(imageUrl.c_str())) {
      Serial.println("Image loaded successfully: " + imageUrl);
      return;
    }
  }

  // Fallback to text if image fails
  vga.setCursor(10, 10);
  vga.setTextColor(vga.RGB(255, 255, 255));
  vga.print("Verkehrszeichen Anzeige");

  vga.setCursor(10, 30);
  vga.setTextColor(vga.RGB(255, 255, 0));
  vga.print("Aktuelles Schild: ");
  vga.print(currentSign);
}

// ✅ Change sign by cycling through a predefined list
void changeSign(int direction) {
  const char* trafficSigns[] = {
    "STOP",
    "Geschwindigkeit 50",
    "Achtung Baustelle",
    "Freie Fahrt"
  };
  int signCount = sizeof(trafficSigns) / sizeof(trafficSigns[0]);

  currentSignIndex = (currentSignIndex + direction) % signCount;
  if (currentSignIndex < 0) currentSignIndex = signCount - 1;

  currentSign = trafficSigns[currentSignIndex];
  Serial.println("Changed sign to: " + String(currentSign));
}
