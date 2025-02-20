# **Dynamische Verkehrszeichen mit Wetterdaten und ESP32 Steuerung**

Dieses Projekt ermöglicht es, ein **dynamisches Verkehrszeichen** mit Wetterdaten und anderen Sensoren zu steuern. Es basiert auf einem **Flask Webserver**, der über **WebSockets** eine Echtzeitkommunikation mit mehreren **ESP32** verwendet, um das Verkehrszeichen zu steuern.

## **Verwendete Technologien:**

- **Flask**: Ein leichtgewichtiges Python Webframework, das für den Server zuständig ist.
- **Flask-SocketIO**: Ermöglicht die Echtzeit-Kommunikation über WebSockets zwischen Server und Browser.
- **ESP32**: Mikrocontroller, der die Verbindung zum Server und zu den Sensoren herstellt.
- **LoRa**: Kommunikationstechnologie, die für die Verbindung zwischen mehreren ESP32-Geräten verwendet wird.
- **HTML / JavaScript**: Für die Frontend-Webseite, die das Verkehrszeichen visualisiert und in Echtzeit aktualisiert wird.
- **VGA-Ansteuerung**: Ein zweiter ESP32 mit Displaycontroller zur Anzeige des Verkehrszeichens auf einem normalen VGA-Monitor.

---

## **Installation und Setup**

### **1. Benötigte Software:**

Stelle sicher, dass du folgende Programme installiert hast:

- **Python** (Version 3.6 oder höher): [Python Download](https://www.python.org/downloads/)
- **Pip** (Python Package Installer): Wird normalerweise zusammen mit Python installiert.
- **Flask** und **Flask-SocketIO** für den Webserver.
- **Visual Studio Code** oder einen anderen Code-Editor.
- **Arduino IDE** mit ESP32-Unterstützung zur Programmierung der Mikrocontroller.

### **2. Abhängigkeiten installieren:**

Installiere die benötigten Python-Pakete, indem du den folgenden Befehl im Projektordner ausführst:

```sh
pip install -r requirements.txt
```

Erstelle eine `requirements.txt`-Datei im Projektordner mit den folgenden Inhalten:

```
Flask==2.1.1
Flask-SocketIO==5.2.0
```

### **3. Webserver starten:**

Führe den folgenden Befehl aus, um den Webserver zu starten:

```sh
python server.py
```

Der Server wird auf `http://localhost:5000` laufen. Die Webseite zeigt das dynamische Verkehrszeichen an.

---

## **Projektstruktur**

```
Verkehrszeichen/
│
├── server.py                # Haupt-Python-Datei für den Flask-Server
├── templates/
│   └── index.html           # HTML-Datei für das Frontend der Webseite
├── esp32_controller/        # ESP32 Code für den ersten Controller
│   └── main.ino             # Steuerung und Kommunikation mit dem Server
├── esp32_display/           # ESP32 Code für den zweiten Controller mit Display
│   └── display.ino          # VGA-Signalsteuerung für Verkehrszeichen
├── requirements.txt         # Listet alle Python-Abhängigkeiten auf
└── README.md                # Diese Datei
```

### **ESP32 Kommunikation:**

- **ESP32 (Controller 1):** Verbindet sich mit dem Server und sendet Updates basierend auf Sensordaten oder externen Befehlen.
- **ESP32 (Controller 2 - Displayeinheit):** Empfangt Befehle über WebSockets oder eine direkte ESP32-zu-ESP32-Kommunikation und zeigt das Verkehrszeichen auf einem VGA-Monitor an.

---

## **Verwendung**

### **Webseite anzeigen:**

Öffne in deinem Webbrowser die URL `http://localhost:5000`. Du wirst die aktuelle Anzeige des Verkehrszeichens sehen. 

### **Verkehrszeichen ändern:**

Du kannst das Verkehrszeichen über eine POST-Anfrage ändern. Zum Beispiel:

```sh
curl -X POST -d "sign=sperre" http://192.168.1.100:5000/update
```

Der ESP32 empfängt das Signal und sendet es weiter an den zweiten ESP32, der das Bild entsprechend auf dem Monitor anzeigt.

### **ESP32-zu-ESP32 Kommunikation:**

Der erste ESP32 sendet das aktualisierte Verkehrszeichen per **LoRa** oder über **Wi-Fi** direkt an den zweiten ESP32, der den Bildschirm ansteuert. Das geschieht entweder über eine einfache HTTP-Anfrage oder über ein WebSocket-Protokoll.

---

## **Fehlerbehebung**

- Falls der ESP32 nicht mit dem Server kommunizieren kann, überprüfe, ob die richtige IP-Adresse verwendet wird.
- Falls der VGA-Monitor keine Anzeige hat, stelle sicher, dass der zweite ESP32 mit einem kompatiblen **VGA-Adapter** verbunden ist.
- Falls der Webserver nicht startet, überprüfe, ob alle Abhängigkeiten korrekt installiert wurden.

---

## **Zukünftige Erweiterungen:**

- **Sensorintegration**: Das System kann erweitert werden, um Wetterdaten und Sensordaten (z. B. Temperatur, Luftfeuchtigkeit) zu berücksichtigen, um die Verkehrszeichen automatisch zu ändern.
- **Verbesserte Anzeige**: Nutzung eines hochwertigen LCDs anstelle eines VGA-Monitors.
- **Erweiterte Steuerung**: Möglichkeit, Verkehrszeichen über eine mobile App zu ändern.
- **Datenbankintegration**: Die gespeicherten Verkehrsdaten könnten in einer Datenbank gespeichert werden, um ein langfristiges Monitoring zu ermöglichen.

---

### **Vielen Dank für deinen Besuch!** 😊

