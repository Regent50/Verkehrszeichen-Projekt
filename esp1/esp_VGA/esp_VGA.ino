#include <WiFi.h>
#include <HTTPClient.h>
#include <ESP32Lib.h>
#include <ESP32Video.h>
#include <VGA/VGA14Bit.h>
#include "image_handler.h"
#include <SocketIoClient.h>




// WLAN-Zugangsdaten
const char* ssid = "Gravity";
const char* password = "joulian_.";

// URL des Servers
const String serverUrl = "http://172.20.10.4:5000/update";

// VGA instance and image handler
VGA14Bit vga;
ImageHandler imageHandler(vga);

// Socket.IO client
SocketIOclient socketIO;

// Socket.IO event handler
void socketIOEvent(socketIOmessageType_t type, uint8_t * payload, size_t length) {
  switch(type) {
    case sIOtype_EVENT:
      // Parse JSON payload
      DynamicJsonDocument doc(1024);
      DeserializationError error = deserializeJson(doc, payload, length);
      if (!error) {
        const char* event = doc[0];
        if (strcmp(event, "update_sign") == 0) {
          currentSign = doc[1].as<String>();
          Serial.println("Sign updated via Socket.IO: " + currentSign);
        }
      }
      break;
    default:
      break;
  }
}




// VGA pins using ESP32Lib
const int redPins[] = {13, 12, 14};
const int greenPins[] = {27, 26, 25};
const int bluePins[] = {33, 32, 15};
const int hsyncPin = 4;
const int vsyncPin = 2;

// Variable to store current sign
String currentSign = "";

void setup() {
  Serial.begin(115200);

  // Correct VGA initialization
  vga.init(vga.MODE320x240, redPins, greenPins, bluePins, hsyncPin, vsyncPin);
  vga.clear(vga.RGB(0, 0, 0));

  // Mit WLAN verbinden
  WiFi.begin(ssid, password);
  Serial.print("Verbinde mit WLAN");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("Verbunden!");

  // Socket.IO connection
  socketIO.begin("172.20.10.4", 5000, "/socket.io/?EIO=4");
  socketIO.onEvent(socketIOEvent);


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

// Map sign names to image filenames
const char* getImageForSign(const String& sign) {
  if (sign == "STOP") return "stop_schild.png";
  if (sign == "Geschwindigkeit 50") return "50kmh_schild.png";
  if (sign == "Achtung Baustelle") return "baustelle_schild.png";
  if (sign == "Freie Fahrt") return "freifahrt_schild.png";
  return "";
}

int currentSignIndex = 0;

void renderWebsite() {
  vga.clear(vga.RGB(0, 0, 0));
  
  // Build image URL based on current sign
  const char* imageName = getImageForSign(currentSign);
  String imageUrl = "http://172.20.10.4:5000/get_image/signs/" + String(imageName);

  
  if (!imageHandler.displayImage(imageUrl.c_str())) {
    // Fallback to text if image fails
    vga.setCursor(10, 10);
    vga.setTextColor(vga.RGB(255, 255, 255));
    vga.print("Verkehrszeichen Anzeige");

    vga.setCursor(10, 30);
    vga.setTextColor(vga.RGB(255, 255, 0));
  vga.print("Aktuelles Schild: ");
  vga.print(currentSign);

  }
}

void changeSign(int direction) {
  currentSignIndex = (currentSignIndex + direction) % 4;
  if (currentSignIndex < 0) currentSignIndex = 3;
  Serial.println("Changed sign to: " + String(trafficSigns[currentSignIndex]));
}
