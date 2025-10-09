import socketio
import pygame
from PIL import Image
import os
import time

# Lokaler Ordner mit Bildern
IMAGE_FOLDER = "Verkehrszeichen-Projekt/static/signs"

# Mapping Verkehrszeichen → Bilddateien
SIGN_IMAGES = {
    "STOP": "stop_schild.png",
    "Geschwindigkeit 50": "50kmh_schild.png",
    "Achtung Baustelle": "baustelle_schild.png",
    "Freie Fahrt": "freifahrt_schild.png"
}

# SocketIO-Client initialisieren
sio = socketio.Client(logger=True, engineio_logger=True, reconnection=True)

# Pygame initialisieren
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Verkehrszeichen Anzeige")

# Aktuelles Bild
current_image = None

def display_image(image_path):
    """Bild öffnen und in Pygame anzeigen"""
    global current_image
    if os.path.isfile(image_path):
        image = Image.open(image_path).convert("RGB")
        current_image = pygame.image.fromstring(image.tobytes(), image.size, image.mode)
        pygame.display.set_mode(image.size)
        screen.blit(current_image, (0, 0))
        pygame.display.flip()
        print(f"Bild {os.path.basename(image_path)} angezeigt")
    else:
        print(f"Bild {os.path.basename(image_path)} nicht gefunden im Ordner {IMAGE_FOLDER}")

# SocketIO Events
@sio.event
def connect():
    print("Verbindung zum Flask-Server hergestellt")

@sio.event
def disconnect():
    print("Verbindung getrennt, versuche erneut zu verbinden...")
    # Automatische Wiederverbindung
    while True:
        try:
            sio.connect(ngrok_url)
            break
        except Exception:
            print("Reconnect fehlgeschlagen, erneut in 5 Sekunden...")
            time.sleep(5)

@sio.event
def update_sign(data):
    sign = data.get("sign")
    if sign:
        print(f"Verkehrszeichen ändern zu: {sign}")
        image_file = SIGN_IMAGES.get(sign)
        if image_file:
            image_path = os.path.join(IMAGE_FOLDER, image_file)
            display_image(image_path)
        else:
            print(f"Kein lokales Bild für Sign '{sign}' definiert")

# Hauptfunktion
def run():
    global ngrok_url
    ngrok_url = "https://nontemporary-alise-piquantly.ngrok-free.app"  # HTTPS-URL von ngrok
    print(f"Verbinde mit: {ngrok_url}")

    try:
        sio.connect(ngrok_url)
    except Exception as e:
        print(f"Verbindungsfehler: {e}")
        return

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if current_image:
            screen.blit(current_image, (0, 0))
            pygame.display.flip()
        pygame.time.wait(50)  # kleine Pause, CPU schonen

    sio.disconnect()
    pygame.quit()

if __name__ == "__main__":
    run()
