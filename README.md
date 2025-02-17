
# **Dynamische Verkehrszeichen mit Wetterdaten und ESP32 Steuerung**

Dieses Projekt ermöglicht es, ein **dynamisches Verkehrszeichen** mit Wetterdaten und anderen Sensoren zu steuern. Es basiert auf einem **Flask Webserver**, der über **WebSockets** eine Echtzeitkommunikation mit einem **ESP32** verwendet, um das Verkehrszeichen zu steuern.

## **Verwendete Technologien:**

- **Flask**: Ein leichtgewichtiges Python Webframework, das für den Server zuständig ist.
- **Flask-SocketIO**: Ermöglicht die Echtzeit-Kommunikation über WebSockets zwischen Server und Browser.
- **ESP32**: Mikrocontroller, der die Verbindung zum Server und zu den Sensoren herstellt.
- **LoRa**: Kommunikationstechnologie, die für die Verbindung zwischen ESP32 und anderen Geräten verwendet wird.
- **HTML / JavaScript**: Für die Frontend-Webseite, die das Verkehrszeichen visualisiert und in Echtzeit aktualisiert wird.

---

## **Installation und Setup**

### **1. Benötigte Software:**

Stelle sicher, dass du folgende Programme installiert hast:

- **Python** (Version 3.6 oder höher): [Python Download](https://www.python.org/downloads/)
- **Pip** (Python Package Installer): Wird normalerweise zusammen mit Python installiert.
- **Flask** und **Flask-SocketIO** für den Webserver.
- **Visual Studio Code** oder einen anderen Code-Editor.

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
├── requirements.txt         # Listet alle Python-Abhängigkeiten auf
└── README.md                # Diese Datei
```

### **Server-Code (`server.py`)**

- Der Flask-Server empfängt POST-Anfragen und sendet die Daten an alle verbundenen Webclients.
- Über **WebSockets** wird das Verkehrszeichen auf der Webseite automatisch aktualisiert, sobald der Server eine Änderung erhält.

### **Frontend (`index.html`)**

- Diese HTML-Datei zeigt das aktuelle Verkehrszeichen an und aktualisiert sich automatisch, wenn der Server eine Änderung über WebSockets sendet.

---

## **Verwendung**

### **Webseite anzeigen:**

Öffne in deinem Webbrowser die URL `http://localhost:5000`. Du wirst die aktuelle Anzeige des Verkehrszeichens sehen. 

### **Verkehrszeichen ändern:**

Du kannst das Verkehrszeichen über eine POST-Anfrage ändern. Zum Beispiel:

```sh
curl -X POST -d "sign=sperre" http://localhost:5000/update
```

Wenn du dies tust, wird das Verkehrszeichen auf der Webseite in Echtzeit auf "Sperre" geändert.

### **WebSocket-Update:**

Jedes Mal, wenn der Server eine Änderung der Verkehrszeichen-Daten empfängt, wird er alle verbundenen Clients (Webbrowser) benachrichtigen und das Verkehrszeichen auf der Webseite automatisch aktualisieren.

---

## **Fehlerbehebung**

- Wenn du beim Starten des Servers eine Fehlermeldung bekommst, stelle sicher, dass alle Abhängigkeiten korrekt installiert sind und dass der Server mit der richtigen Version von Python läuft.
- Achte darauf, dass der Port `5000` nicht von einer anderen Anwendung blockiert wird.

---

## **Zukünftige Erweiterungen:**

- **Sensorintegration**: Das System kann erweitert werden, um Wetterdaten und Sensordaten (z. B. Temperatur, Luftfeuchtigkeit) zu berücksichtigen, um die Verkehrszeichen automatisch zu ändern.
- **ESP32-Integration**: Der ESP32 kann für die tatsächliche Steuerung von physischen Verkehrszeichen (z. B. LEDs oder Bildschirmen) verwendet werden.
- **Datenbankintegration**: Die gespeicherten Verkehrsdaten könnten in einer Datenbank gespeichert werden, um ein langfristiges Monitoring zu ermöglichen.

---

### **Vielen Dank für deinen Besuch!** 😊
