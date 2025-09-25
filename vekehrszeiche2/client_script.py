import socketio
import pygame
from PIL import Image
import os

# Lokaler Ordner mit Bildern
IMAGE_FOLDER = "Verkehrszeichen-Projekt/static/signs"  # relativ zum Client-Script

# Mapping der Verkehrszeichen zum lokalen Bild
SIGN_IMAGES = {
    "STOP": "stop_schild.png",
    "Geschwindigkeit 50": "50kmh_schild.png",
    "Achtung Baustelle": "baustelle_schild.png",
    "Freie Fahrt": "freifahrt_schild.png"
}

# Initialisiere SocketIO-Client
sio = socketio.Client()

# Pygame initialisieren
pygame.init()
screen = pygame.display.set_mode((800, 600))  # Fenstergröße anpassen
pygame.display.set_caption("Verkehrszeichen Anzeige")

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
        image_file = SIGN_IMAGES.get(sign)
        if image_file:
            image_path = os.path.join(IMAGE_FOLDER, image_file)
            if os.path.isfile(image_path):
                # Bild öffnen
                image = Image.open(image_path).convert("RGB")
                # Bild in pygame konvertieren
                pygame_image = pygame.image.fromstring(image.tobytes(), image.size, image.mode)
                
                # Bildschirmgröße an Bild anpassen
                screen = pygame.display.set_mode(image.size)
                screen.blit(pygame_image, (0, 0))
                pygame.display.flip()
                print(f"Bild {image_file} auf Monitor angezeigt")
            else:
                print(f"Bild {image_file} nicht gefunden im Ordner {IMAGE_FOLDER}")
        else:
            print(f"Kein lokales Bild für Sign '{sign}' definiert")

def run():
    # Hier die ngrok-URL deines Servers eintragen
    sio.connect("https://nontemporary-alise-piquantly.ngrok-free.app")
    sio.wait()

if __name__ == "__main__":
    run()
