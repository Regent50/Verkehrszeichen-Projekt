# **Dynamische Verkehrszeichen mit Wetterdaten und ESP32 Steuerung**

Dieses Projekt ermöglicht es, ein **dynamisches Verkehrszeichen** mit Wetterdaten und anderen Sensoren zu steuern. Es basiert auf einem **Flask Webserver**, der über **WebSockets** eine Echtzeitkommunikation mit mehreren **ESP32** verwendet, um das Verkehrszeichen zu steuern.

## **Verwendete Technologien:**

- **Flask**: Ein leichtgewichtiges Python Webframework, das für den Server zuständig ist.
- **Flask-SocketIO**: Ermöglicht die Echtzeit-Kommunikation über WebSockets zwischen Server und Browser.
- **ESP32**: Mikrocontroller, der die Verbindung zum Server und zu den Sensoren herstellt.
- **HTML / JavaScript**: Für die Frontend-Webseite, die das Verkehrszeichen visualisiert und in Echtzeit aktualisiert wird.
- **VGA-Ansteuerung**: Der ESP32 mit Displaycontroller zur Anzeige des Verkehrszeichens auf einem normalen VGA-Monitor.

---

## **Deployment Options**

### **Local Development:**
The server can be run on your local machine for development and testing.

### **Raspberry Pi 3 Deployment:**
The server runs perfectly on Raspberry Pi 3, making it ideal for production deployments. The lightweight Flask server is well-suited for the Pi's resources.

### **Online Accessibility:**
The server can be accessed online anytime using port forwarding or a tunneling service ngrok, allowing remote control and monitoring of the traffic signs.

## **Installation und Setup**
Simple Setup through the ngrok interface via HTTP
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
Pillow==6.2.0
```

### **3. Webserver starten:**

Der Server kann auf verschiedenen Plattformen ausgeführt werden, einschließlich Raspberry Pi 3. Führe den folgenden Befehl aus, um den Webserver zu starten:

```sh
python server.py
```

Der Server läuft standardmäßig auf `http://localhost:5000`, kann aber auch online über eine öffentliche IP-Adresse oder Domain zugänglich gemacht werden. Die Webseite zeigt das dynamische Verkehrszeichen an und ist jederzeit online verfügbar.


---

## **Projektstruktur**

```
Verkehrszeichen/
│
├── arduino libraries/       # Arduino libraries for ESP32 communication
├── cezar server funktionsfähig/  # Functional server templates and files
│   ├── guest_verkehrszeichen.html
│   ├── index.html
│   ├── kontrolle.html
│   ├── LOGIN.html
│   ├── main_guest.html
│   ├── main.html
│   ├── VERKEHRSZEICHEN.html
│   └── website.html
├── esp1/                    # ESP32 VGA display controller code
│   └── esp_VGA/
│       ├── esp_VGA.ino      # Main ESP32 VGA controller code
│       └── image_handler.h  # Image handling functions
├── koni integration/       # Integration templates and files
│   ├── index.html
│   ├── kontrolle.html
│   ├── LOGIN.html
│   ├── MAIN_gast.html
│   ├── MAIN.html
│   ├── VERKEHRSZEICHEN.html
│   ├── website_template.html
│   └── website.html
├── lib_test/               # Library test files
│   └── espvgatest/
│       └── espvgatest.ino   # ESP32 VGA test code
├── static/                  # Static files for web server
│   ├── script.js            # JavaScript for web interface
│   ├── styles.css           # CSS styles for web interface
│   └── signs/               # Traffic sign images
│       ├── 50kmh_schild.png
│       ├── baustelle_schild.png
│       ├── freifahrt_schild.png
│       └── stop_schild.png
├── templates/              # Flask template files
│   ├── guest_verkehrszeichen.html
│   ├── index.html
│   ├── kontrolle.html
│   ├── LOGIN.html
│   ├── main_guest.html
│   ├── MAIN.html
│   ├── VERKEHRSZEICHEN.html
│   ├── website_template.html
│   └── website.html
├── .gitattributes           # Git attributes file
├── .gitignore               # Git ignore file
├── frame.png                # Example frame image
├── ngrok.exe                # Ngrok executable for tunneling
├── README.md                 # Project documentation
├── requirements.txt          # Python dependencies
├── server.py                 # Flask server main file
└── vga_image_converter.py    # VGA image conversion utility
```

### **ESP32 Kommunikation:**

- **ESP32 (Controller 2 - Displayeinheit):** Empfangt Befehle über WebSockets oder eine direkte Server-zu-ESP32-Kommunikation und zeigt das Verkehrszeichen auf einem VGA-Monitor an.

---

## **Verwendung**

### **Webseite anzeigen:**

Öffne in deinem Webbrowser die URL `http://localhost:5000` für lokalen Zugriff oder die öffentliche IP/Domain für den Online-Zugriff. Du wirst die aktuelle Anzeige des Verkehrszeichens sehen, die jederzeit online verfügbar ist.

### **Verkehrszeichen ändern:**

Du kannst das Verkehrszeichen über eine POST-Anfrage ändern. Zum Beispiel:

```sh
curl -X POST -d "sign=sperre" http://localhost:5000/update
```

Der ESP32 empfängt das Signal und sendet es weiter an den zweiten ESP32, der das Bild entsprechend auf dem Monitor anzeigt.

### **ESP32-zu-ESP32 Kommunikation:**

Der erste ESP32/Server sendet das aktualisierte Verkehrszeichen per **LoRa (nicht intergriert)** oder über **Wi-Fi** direkt an den zweiten ESP32, der den Bildschirm ansteuert. Das geschieht entweder über eine einfache HTTP-Anfrage oder über ein WebSocket-Protokoll.

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
