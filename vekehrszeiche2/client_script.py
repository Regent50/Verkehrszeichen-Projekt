import socketio
import pygame
from PIL import Image
import os

# Lokaler Ordner mit Bildern
IMAGE_FOLDER = "Verkehrszeichen-Projekt/static/signs"

# Mapping Verkehrszeichen → Bilddatei
SIGN_IMAGES = {
    "STOP": "stop_schild.png",
    "Geschwindigkeit 50": "50kmh_schild.png",
    "Achtung Baustelle": "baustelle_schild.png",
    "Freie Fahrt": "freifahrt_schild.png"
}

# SocketIO-Client initialisieren
sio = socketio.Client()

# Pygame initialisieren
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Verkehrszeichen Anzeige")

# Variable, die das aktuelle Bild hält
current_image = None

@sio.event
def connect():
    print("Verbindung zum Flask-Server hergestellt")

@sio.event
def disconnect():
    print("Verbindung getrennt")

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
                # Bild öffnen und in pygame konvertieren
                image = Image.open(image_path).convert("RGB")
                current_image = pygame.image.fromstring(image.tobytes(), image.size, image.mode)
                # Fenstergröße an Bildgröße anpassen
                pygame.display.set_mode(image.size)
                # Direktes Update auf dem Screen
                screen.blit(current_image, (0, 0))
                pygame.display.flip()
                print(f"Bild {image_file} auf Monitor angezeigt")
            else:
                print(f"Bild {image_file} nicht gefunden im Ordner {IMAGE_FOLDER}")
        else:
            print(f"Kein lokales Bild für Sign '{sign}' definiert")

def run():
    # Verbindung zum Server über HTTP und WebSocket erzwingen
    sio.connect(
        "http://nontemporary-alise-piquantly.ngrok-free.app",  # HTTP-URL von ngrok
        transports=["websocket"]
    )

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
