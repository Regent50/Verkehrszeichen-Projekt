import socketio
import requests
from PIL import Image
from io import BytesIO

# Feste ngrok-URL
ngrok_url = "https://nontemporary-alise-piquantly.ngrok-free.app"

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
        image_url = f"{ngrok_url}/get_image/{sign}"
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
    print(f"Verbinde mit: {ngrok_url}")
    sio.connect(ngrok_url)  # Verwende die ngrok-URL
    sio.wait()  # Warte, bis die Verbindung hergestellt und aktiv bleibt

# Main-Schleife, die weiterhin läuft, um die Verbindung aufrechtzuerhalten
def start_ws_thread():
    run()

if __name__ == "__main__":
    start_ws_thread()
