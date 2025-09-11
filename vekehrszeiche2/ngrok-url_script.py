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
            print(f"Aktuelle ngrok URL: {public_url}")
            return public_url
        else:
            print("Keine ngrok-URLs verfügbar.")
            return None
    except Exception as e:
        print(f"Fehler beim Abrufen der ngrok-URL: {e}")
        return None

if __name__ == "__main__":
    # Hole die ngrok URL und gebe sie aus
    ngrok_url = get_ngrok_url()
    if ngrok_url:
        print(f"Die ngrok URL lautet: {ngrok_url}")
    else:
        print("ngrok URL konnte nicht abgerufen werden.")
