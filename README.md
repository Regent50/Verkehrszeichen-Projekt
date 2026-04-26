# Dynamische Verkehrszeichen mit Wetterdaten und ESP32-Steuerung

## Projektübersicht

Dieses Projekt entstand im Rahmen einer **Diplomarbeit an der HTLW 10 in Wien**. Ziel ist die Entwicklung eines Systems zur **dynamischen Anzeige und Steuerung von Verkehrszeichen** über eine webbasierte Oberfläche. Die Anwendung verbindet einen **Flask-Webserver**, eine **Echtzeitkommunikation per Socket.IO**, mehrere **Benutzeroberflächen für unterschiedliche Geräteklassen** sowie die Anbindung von **ESP32-Mikrocontrollern** und Sensordaten.

Die Anzeige der Verkehrszeichen kann über eine Administrationsoberfläche gesteuert werden. Gleichzeitig können aktuelle Sensordaten wie **UV-Wert, Luftdruck, Temperatur und Luftfeuchtigkeit** erfasst und in Echtzeit an verbundene Clients übertragen werden.

---

## Ziele des Projekts

- Entwicklung eines webbasierten Systems zur Steuerung dynamischer Verkehrszeichen
- Echtzeitübertragung von Verkehrszeichen- und Sensordaten
- Trennung von **Admin-** und **Gastansichten**
- Unterstützung für **Desktop-** und **Mobilgeräte**
- Vorbereitung einer Anbindung an **ESP32-Hardware** zur Anzeige und Sensorerfassung
- Einsatz des Systems lokal oder im Netzwerk, z. B. auf einem Raspberry Pi

---

## Funktionen

### Webanwendung
- Login-basierte Administrationsoberfläche
- Auswahl und Umschaltung verschiedener Verkehrszeichen
- Getrennte Ansichten für:
  - Admin Desktop
  - Admin Mobile
  - Gast Desktop
  - Gast Mobile
  - Live-Schild-Anzeige
- Automatische Aktualisierung der Anzeige in Echtzeit
- Anzeige von Sensordaten direkt in der Oberfläche

### Echtzeitkommunikation
- Verwendung von **Flask-SocketIO** zur Live-Kommunikation zwischen Server und Clients
- Sofortige Übertragung von Verkehrszeichenänderungen
- Sofortige Übertragung neuer Sensordaten
- Wiederherstellung des letzten Zustands über `state.json`

### Sensordaten
Das System kann folgende Sensordaten verarbeiten:
- UV
- Luftdruck
- Temperatur
- Luftfeuchtigkeit

Die Daten werden vom Server entgegengenommen, validiert, gespeichert und live an alle verbundenen Clients weitergegeben.

### Hardwarebezug
- Einbindung von **ESP32-Mikrocontrollern** für Sensorik und Anzeige
- Vorbereitung zur Nutzung eines externen Displays bzw. einer Verkehrszeichenanzeige
- Arduino-bezogene Komponenten und Bibliotheken sind im Repository enthalten

---

## Verwendete Technologien

- **Python**
- **Flask**
- **Flask-SocketIO**
- **eventlet**
- **HTML, CSS, JavaScript**
- **ESP32**
- **Socket.IO**
- **Arduino / Embedded-Komponenten**

---

## Projektstruktur

```text
Verkehrszeichen-Projekt/
├── Documentation/
│   └── Dynamische Verkehrszeichen.pptx
├── static/
│   ├── css/
│   │   ├── admin_desktop.css
│   │   ├── admin_mobile.css
│   │   ├── guest_desktop.css
│   │   ├── guest_mobile.css
│   │   └── live_sign.css
│   ├── js/
│   │   ├── admin_desktop.js
│   │   ├── admin_mobile.js
│   │   ├── guest_desktop.js
│   │   ├── guest_mobile.js
│   │   ├── live_sign.js
│   │   └── shared_socket.js
│   └── signs/
│       ├── 50kmh_schild.png
│       ├── baustelle_schild.png
│       ├── freifahrt_schild.png
│       ├── schild_30.png
│       └── stop_schild.png
├── templates/
│   ├── admin_desktop.html
│   ├── admin_mobile.html
│   ├── guest_desktop.html
│   ├── guest_mobile.html
│   ├── guest_select.html
│   ├── live_sign.html
│   └── LOGIN.html
├── arduino libraries/
├── server.py
├── state.json
├── requirements.txt
└── README.md
```

---

## Installation

### Voraussetzungen

Folgende Software sollte installiert sein:
- **Python 3.10+** empfohlen
- **pip**
- optional: **Arduino IDE** mit ESP32-Unterstützung
- optional: **VS Code** oder ein anderer Editor

### Abhängigkeiten installieren

**PowerShell:**
```powershell
pip install -r requirements.txt
```

Die aktuell verwendeten Python-Abhängigkeiten sind in `requirements.txt` definiert.

---

## Server starten

**PowerShell:**
```powershell
python server.py
```

Der Server startet standardmäßig unter:

- `http://localhost:5000`

Der Start erfolgt aktuell mit aktiviertem Debug-Modus und ist damit vor allem für Entwicklung und Demonstration geeignet.

---

## Routen und Ansichten

### Hauptseiten
- `/` - Login
- `/admin` - Admin-Ansicht Desktop
- `/admin-mobile` - Admin-Ansicht Mobil
- `/live-sign` - reine Verkehrszeichenanzeige
- `/guest` - Auswahl für Gastansichten
- `/guest-desktop` - Gastansicht Desktop
- `/guest-mobile` - Gastansicht Mobil
- `/logout` - Logout

### Rückwärtskompatible Routen
Zusätzlich existieren ältere Weiterleitungsrouten wie:
- `/main`
- `/mobile`
- `/kontrolle`
- `/verkehrszeichen`
- `/verkehrszeichen1`
- `/guestm`
- `/guestmobile`
- `/guestv`

---

## Schnittstellen für Aktualisierungen

### Verkehrszeichen ändern
Das aktive Verkehrszeichen wird per POST-Anfrage an `/update` gesetzt.

Beispiel:

**PowerShell:**
```powershell
Invoke-WebRequest -Method Post -Uri http://localhost:5000/update -Body @{ sign = 'STOP' }
```

### Sensordaten senden
Sensordaten können per POST an `/sensor-update` oder `/sensor_update` gesendet werden.

Beispiel mit JSON:

**PowerShell:**
```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:5000/sensor-update -ContentType 'application/json' -Body '{"uv":3.5,"druck":1013,"temperatur":22.4,"luftfeuchtigkeit":48}'
```

---

## Aktueller Projektstand

Der aktuelle Stand des Repositorys zeigt eine funktionsfähige Webanwendung mit:
- Login-System
- Echtzeitkommunikation
- Zustandsverwaltung über `state.json`
- mehreren Ansichten für unterschiedliche Rollen und Geräte
- vorbereiteter Sensorintegration
- vorhandener Präsentationsdokumentation im Ordner `Documentation`

Damit eignet sich das Projekt gut als Demonstrator für eine webgestützte, dynamische Verkehrszeichensteuerung im Rahmen der Diplomarbeit.

---

## Hinweise

- Die Login-Daten sind derzeit direkt im Quellcode in `server.py` hinterlegt.
- Der Server verwendet aktuell `debug=True` und ist damit nicht als abgesicherte Produktivkonfiguration gedacht.
- In `server.py` wird `login.html` gerendert, während im Repository die Datei `LOGIN.html` vorhanden ist. Auf Windows kann das unauffällig sein, auf Linux-Systemen wie einem Raspberry Pi kann die Groß-/Kleinschreibung jedoch relevant werden.
- Dateien wie `githubkey.txt` oder `ngrok.txt` sollten nur dann im Repository bleiben, wenn sie für die Projektdokumentation bewusst benötigt werden.

---

## Mögliche Erweiterungen

- automatische Verkehrszeichensteuerung auf Basis definierter Sensorgrenzen
- Integration zusätzlicher Sensoren
- Anbindung einer Datenbank zur Protokollierung von Messwerten
- Rollen- und Benutzerverwaltung mit sicherer Authentifizierung
- produktive Bereitstellung auf Raspberry Pi oder einem anderen lokalen Server
- Erweiterung um mobile Fernsteuerung oder externe API-Anbindung

---

## Dokumentation

Eine Präsentationsdatei zur Diplomarbeit befindet sich hier:

- `Documentation/Dynamische Verkehrszeichen.pptx`

---

## Kurzfazit

Das Projekt zeigt praxisnah, wie sich **Webentwicklung**, **Echtzeitkommunikation**, **Embedded-Hardware** und **Sensorintegration** zu einem funktionalen Gesamtsystem für dynamische Verkehrszeichen verbinden lassen. Damit bildet es eine gute technische Grundlage für eine HTL-Diplomarbeit mit Fokus auf Software, Vernetzung und Hardwareanbindung.