from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_socketio import SocketIO, emit
import os

# Flask App Setup
app = Flask(__name__, 
            template_folder=os.path.abspath('templates'),
            static_folder=os.path.abspath('static'))
app.secret_key = "geheimes_passwort"
socketio = SocketIO(app, cors_allowed_origins="*")

# Benutzername und Passwort
USERNAME = "htl"
PASSWORD = "5AHEL"

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
            print(f"Login erfolgreich für: {username}")
            return redirect(url_for("main"))
    return render_template("login.html", error=True)

# ==========================================================
# HAUPTROUTEN (Alle zeigen jetzt auf adminmain.html)
# ==========================================================
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route("/main")
def main():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    # HIER: Wir laden jetzt deine neue integrierte Datei
    return render_template("adminmain.html")

@app.route("/kontrolle")
def kontrolle():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    # Auch hier laden wir die Hauptdatei, da die Kontrolle jetzt in der Sidebar ist
    return render_template("adminmain.html")

@app.route("/verkehrszeichen")
def verkehrszeichen():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    # Die Vorschau ist ebenfalls in der Hauptdatei enthalten
    return render_template("adminmain.html")

# Diese Route lassen wir für die "Vollbild"-Anzeige (z.B. für das echte Schild draußen)
@app.route("/verkehrszeichen1")
def verkehrszeichen1():
    # Falls du eine separate Datei für Vollbild hast (ohne Sidebar), lade diese hier.
    # Wenn du auch hier das Dashboard willst, ändere es zu "adminmain.html"
    return render_template("Verkehrszeichen1.html") 

# ==========================================================
# GUEST ROUTEN
# ==========================================================

@app.route("/guestm")
def main_guest():
    return render_template("main_guest.html")

@app.route("/guestv")
def verkehrszeichen_guest():
    return render_template("guest_verkehrszeichen.html")

# ==========================================================
# LOGIK & UPDATES
# ==========================================================

@app.route("/update", methods=["POST"])
def update_sign():
    sign = request.form.get("sign")
    if sign:
        print(f"Verkehrszeichen aktualisiert: {sign}")
        # Sende das Signal an ALLE verbundenen Clients (Admin Dashboard + echtes Schild)
        socketio.emit("update_sign", {"sign": sign})
        return "Update erfolgreich", 200
    return "Fehler: Kein Sign-Parameter", 400

# Route für Bilder (falls benötigt, aber Flask static folder macht das meist automatisch)
@app.route("/get_image/<image_name>")
def get_image(image_name):
    valid_images = ["50kmh_schild.png", "baustelle_schild.png", "freifahrt_schild.png", "stop_schild.png"]
    
    if image_name not in valid_images:
        return "Invalid image name", 404
    
    try:
        # Pfad angepasst auf static/signs
        image_path = os.path.join(app.static_folder, "signs", image_name)
        
        if not os.path.isfile(image_path):
            return f"Bild {image_name} nicht gefunden", 404
        
        return send_file(image_path, mimetype='image/png')
    except Exception as e:
        return f"Error: {str(e)}", 500

# Event, wenn ein Client eine Verbindung herstellt
@socketio.on('connect')
def handle_connect():
    print("Ein Client hat sich verbunden.")
    emit('message', {'message': 'Verbindung hergestellt!'})

# Hauptprogramm
if __name__ == "__main__":
    print("Server wird gestartet...")
    # host="0.0.0.0" macht den Server im Netzwerk verfügbar
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)