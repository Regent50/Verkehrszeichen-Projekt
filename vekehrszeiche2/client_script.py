import socketio
import pygame
from PIL import Image
import os

# Lokaler Ordner mit Bildern
IMAGE_FOLDER = "Verkehrszeichen-Projekt/static/signs"

# Mapping der Verkehrszeichen zu Bilddateien
SIGN_IMAGES = {
    "STOP": "stop_schild.png",
    "Geschwindigkeit 50": "50kmh_schild.png",
    "Achtung Baustelle": "baustelle_schild.png",
    "Freie Fahrt": "freifahrt_schild.png"
}

# Initialisierung des SocketIO-Clients
sio = socketio.Client(logger=True, engineio_logger=True)

# Pygame initialisieren
pygame.init()
# Vollbildmodus für den Pi Zero
screen = pygame.display.set_mode((800, 600))  # Größe anpassen, falls nötig
pygame.display.set_caption("Verkehrszeichen Anzeige")

# Variable, die das aktuelle Bild speichert
current_image = None

# Event: Verbindung zum Server hergestellt
@sio.event
def connect():
    print("Verbindung zum Flask-Server hergestellt")

# Event: Verbindung getrennt
@sio.event
def disconnect():
    print("Verbindung getrennt")

# Event: Verkehrszeichen wurde geändert
@sio.event
def update_sign(data):
    global current_image
    sign = data.get("sign")
    if sign:
        print(f"Verkehrszeichen ändern zu: {sign}")
        image_file = SIGN_IMAGES.get(sign)
        if image_file:
            image_path = os.path.join(IMAGE_FOLDER, image_file)
            if os.path.isfile(image_path):
                # Bild öffnen und in Pygame-Format konvertieren
                image = Image.open(image_path).convert("RGB")
                current_image = pygame.image.fromstring(image.tobytes(), image.size, image.mode)
                # Fenstergröße auf Bildgröße anpassen
                pygame.display.set_mode(image.size)
                # Bild auf Bildschirm anzeigen
                screen.blit(current_image, (0, 0))
                pygame.display.flip()
                print(f"Bild {image_file} auf Monitor angezeigt")
            else:
                print(f"Bild {image_file} nicht gefunden im Ordner {IMAGE_FOLDER}")
        else:
            print(f"Kein lokales Bild für Sign '{sign}' definiert")

# Funktion zum Verbinden und Warten auf WebSocket
def run():
    # HTTP-URL von ngrok verwenden
    ngrok_url = "https://nontemporary-alise-piquantly.ngrok-free.app"  # ngrok HTTP-URL
    print(f"Verbinde mit: {ngrok_url}")
    
    try:
        sio.connect(ngrok_url, transports=["websocket"])
        print("Verbindung erfolgreich!")
    except Exception as e:
        print(f"Verbindungsfehler: {e}")

    # Hauptloop für Pygame, Fenster dauerhaft offen
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        # Wenn ein Bild geladen ist, dauerhaft anzeigen
        if current_image:
            screen.blit(current_image, (0, 0))
            pygame.display.flip()

    # SocketIO trennen, wenn Fenster geschlossen wird
    sio.disconnect()
    pygame.quit()

if __name__ == "__main__":
    run()
