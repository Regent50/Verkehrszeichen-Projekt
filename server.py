from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_socketio import SocketIO, emit
import os

# Flask App Setup
app = Flask(__name__,  # Verwende __name__ anstelle von 'name'
            template_folder=os.path.abspath('templates'),
            static_folder=os.path.abspath('static'))
app.secret_key = "geheimes_passwort"
socketio = SocketIO(app, cors_allowed_origins="*")

# Benutzername und Passwort
USERNAME = "htl"
PASSWORD = "5AHEL"

# Verzeichnis für Bilder
image_folder = "./images"
if not os.path.exists(image_folder):
    os.makedirs(image_folder)

# WebSocket Events
@app.route("/", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        if "guest" in request.form:
            return redirect(url_for("main_guest"))
        username = request.form.get("username")
        password = request.form.get("password")
        if username == USERNAME and password == PASSWORD:
            session["logged_in"] = True
            print(f"Login erfolgreich für: {username}")  # Log-Ausgabe für erfolgreichen Login
            return redirect(url_for("main"))
    return render_template("login.html", error=True)

@app.route("/main")
def main():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("main.html")

@app.route("/kontrolle")
def kontrolle():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("kontrolle.html")

@app.route("/verkehrszeichen")
def verkehrszeichen():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("verkehrszeichen.html")

@app.route("/guestm")
def main_guest():
    return render_template("main_guest.html")

@app.route("/guestv")
def verkehrszeichen_guest():
    return render_template("guest_verkehrszeichen.html")

@app.route("/update", methods=["POST"])
def update_sign():
    sign = request.form.get("sign")
    if sign:
        print(f"Verkehrszeichen aktualisiert: {sign}")  # Ausgabe, wenn ein Update stattfindet
        socketio.emit("update_sign", {"sign": sign})  # Sende das Bild an den Client
        return "Update erfolgreich", 200
    return "Fehler: Kein Sign-Parameter", 400

# Neue Route zum Abrufen der Bilder ohne VGA-Konvertierung
@app.route("/get_image/<image_name>")
def get_image(image_name):
    valid_images = ["50kmh_schild.png", "baustelle_schild.png", "freifahrt_schild.png", "stop_schild.png"]
    
    if image_name not in valid_images:
        return "Invalid image name", 404
    
    try:
        image_path = os.path.join(app.static_folder, "signs", image_name)
        
        if not os.path.isfile(image_path):
            print(f"Bild {image_name} nicht gefunden")  # Ausgabe, wenn Bild nicht gefunden wird
            return f"Bild {image_name} nicht gefunden", 404
        
        print(f"Bild {image_name} wird gesendet.")  # Ausgabe, wenn Bild gefunden und gesendet wird
        return send_file(image_path, mimetype='image/png')
    except Exception as e:
        print(f"Error beim Abrufen des Bildes: {str(e)}")  # Ausgabe bei Fehlern
        return f"Error: {str(e)}", 500

# Event, wenn ein Client eine Verbindung herstellt
@socketio.on('connect')
def handle_connect():
    print("Ein Client hat sich verbunden.")  # Ausgabe, wenn ein Client erfolgreich verbunden ist
    # Weitere spezifische Ausgabe, um den Client-Typ zu erkennen
    emit('message', {'message': 'Verkehrszeichen-Client erfolgreich verbunden!'})

# Hauptprogramm für den Flask-Server
if __name__ == "__main__":  # Verwende __name__ anstelle von 'name'
    print("Server wird gestartet...")  # Ausgabe, wenn der Server gestartet wird
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
