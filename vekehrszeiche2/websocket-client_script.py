import websocket
import json
import threading
import time
import requests

# ngrok API URL, um die öffentliche URL zu bekommen
ngrok_api_url = "http://localhost:4040/api/tunnels"

def get_ngrok_url():
    """Holt die ngrok-URL über die ngrok-API."""
    try:
        response = requests.get(ngrok_api_url)
        tunnels = response.json().get('tunnels')
        if tunnels:
            # Hole die öffentliche URL (ngrok-URL)
            public_url = tunnels[0]['public_url']
            return public_url
        else:
            print("Keine ngrok-URLs verfügbar.")
            return None
    except Exception as e:
        print(f"Fehler beim Abrufen der ngrok-URL: {e}")
        return None

# WebSocket-Verbindung zum Flask-Server herstellen
def on_message(ws, message):
    data = json.loads(message)
    if "sign" in data:
        sign = data["sign"]
        print(f"Verkehrszeichen ändern zu: {sign}")
        # Hier kannst du Logik hinzufügen, um das Verkehrszeichen zu aktualisieren (auf dem VGA-Display anzeigen)

def on_error(ws, error):
    print(f"Fehler: {error}")

def on_close(ws, close_status_code, close_msg):
    print("Verbindung geschlossen")

def on_open(ws):
    print("Verbindung zum Server hergestellt")

# WebSocket-Verbindung starten, nachdem die ngrok-URL abgerufen wurde
def run():
    ngrok_url = get_ngrok_url()
    if ngrok_url:
        print(f"Verbinde mit: {ngrok_url}")
        ws = websocket.WebSocketApp(ngrok_url,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)
        ws.on_open = on_open
        ws.run_forever()
    else:
        print("ngrok URL konnte nicht abgerufen werden.")

# Starte WebSocket-Verbindung in einem separaten Thread
def start_ws_thread():
    ws_thread = threading.Thread(target=run)
    ws_thread.daemon = True
    ws_thread.start()

if __name__ == "__main__":
    start_ws_thread()

    # Main-Schleife, die weiterhin läuft, um WebSocket aufrechtzuerhalten
    while True:
        time.sleep(1)  # Dies hält das Skript am Laufen
