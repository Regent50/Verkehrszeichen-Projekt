import requests

# ngrok API URL, um die öffentliche URL zu bekommen
ngrok_api_url = "http://localhost:4040/api/tunnels"

def get_ngrok_url():
    """Holt die ngrok-URL über die ngrok-API."""
    try:
        # API-Anfrage an ngrok stellen
        response = requests.get(ngrok_api_url)
        
        # Falls die Antwort erfolgreich ist (Statuscode 200)
        if response.status_code == 200:
            tunnels = response.json().get('tunnels', [])
            if tunnels:
                # Hol die erste öffentliche URL
                public_url = tunnels[0]['public_url']
                print(f"Aktuelle ngrok URL: {public_url}")
                return public_url
            else:
                print("Keine ngrok-URLs verfügbar.")
                return None
        else:
            print(f"Fehler beim Abrufen der ngrok-URL: {response.status_code}")
            return None
    except Exception as e:
        print(f"Fehler beim Abrufen der ngrok-URL: {e}")
        return None
