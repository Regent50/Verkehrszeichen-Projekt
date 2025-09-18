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
        
        # Sende POST-Anfrage mit dem 'sign' Parameter
        response = requests.post(f"{ngrok_url}/update", data={"sign": sign})
        
        if response.status_code == 200:
            print("Verkehrszeichen erfolgreich aktualisiert!")
            # Das Bild im Byte-Format erhalten, wenn es erfolgreich ist
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                image = Image.open(BytesIO(image_response.content))
                image.show()  # Zeige das Bild an
            else:
                print(f"Fehler beim Abrufen des Bildes: {image_response.status_code}")
        else:
            print(f"Fehler beim Aktualisieren des Verkehrszeichens: {response.status_code}")

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
