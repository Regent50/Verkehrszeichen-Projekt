from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__, 
            template_folder=os.path.abspath('templates'),
            static_folder=os.path.abspath('static'))
app.secret_key = "geheimes_passwort"
socketio = SocketIO(app, cors_allowed_origins="*")

USERNAME = "admin"
PASSWORD = "1234"

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
        print(f"Verkehrszeichen aktualisiert: {sign}")
        socketio.emit("update_sign", {"sign": sign})  
        return "Update erfolgreich", 200
    return "Fehler: Kein Sign-Parameter", 400

# Neue Route zum Abrufen der Bilder ohne VGA-Konvertierung
@app.route("/get_image/<image_name>")
def get_image(image_name):
    # Liste gültiger Bildnamen
    valid_images = ["50kmh_schild.png", "baustelle_schild.png", "freifahrt_schild.png", "stop_schild.png"]
    
    if image_name not in valid_images:
        return "Invalid image name", 404
    
    try:
        # Bildpfad im static/signs Ordner
        image_path = os.path.join(app.static_folder, "signs", image_name)
        
        # Überprüfe, ob das Bild existiert
        if not os.path.isfile(image_path):
            return f"Bild {image_name} nicht gefunden", 404
        
        # Gib das Bild direkt zurück, ohne es zu konvertieren
        return send_file(image_path, mimetype='image/png')
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
