import socketio
import json
import time
import requests
from PIL import Image
from io import BytesIO

# ngrok API URL, um die öffentliche URL zu bekommen
ngrok_api_url = "http://localhost:4040/api/tunnels"

def get_ngrok_url():
    """Holt die ngrok-URL über die ngrok-API."""
    try:
        response = requests.get(ngrok_api_url)
        tunnels = response.json().get('tunnels')
        if tunnels:
            public_url = tunnels[0]['public_url']
            print(f"Aktuelle ngrok URL: {public_url}")
            return public_url
        else:
            print("Keine ngrok-URLs verfügbar.")
            return None
    except Exception as e:
        print(f"Fehler beim Abrufen der ngrok-URL: {e}")
        return None

# Initialisiere den SocketIO-Client
sio = socketio.Client()

@sio.event
def connect():
    print("Verbindung zum Flask-Server hergestellt")

@sio.event
def disconnect():
    print("Verbindung getrennt")

@sio.event
def update_sign(data):
    sign = data.get("sign")
    if sign:
        print(f"Verkehrszeichen ändern zu: {sign}")
        # Fordere das Bild des Verkehrszeichens vom Server an
        image_url = f"{get_ngrok_url()}/get_image/{sign}"
        print(f"Fordere Bild an: {image_url}")
        response = requests.get(image_url)
        
        if response.status_code == 200:
            # Das Bild im Byte-Format erhalten
            image = Image.open(BytesIO(response.content))
            # Hier kannst du das Bild anzeigen oder verarbeiten (z.B. auf dem Bildschirm ausgeben)
            image.show()
        else:
            print(f"Fehler beim Abrufen des Bildes: {response.status_code}")

# WebSocket-Verbindung herstellen
def run():
    ngrok_url = get_ngrok_url()
    if ngrok_url:
        print(f"Verbinde mit: {ngrok_url}")
        sio.connect(ngrok_url)  # Verwende die ngrok-URL
        sio.wait()  # Warte, bis die Verbindung hergestellt und aktiv bleibt
    else:
        print("ngrok URL konnte nicht abgerufen werden.")

# Main-Schleife, die weiterhin läuft, um die Verbindung aufrechtzuerhalten
def start_ws_thread():
    run()

if __name__ == "__main__":
    start_ws_thread()
