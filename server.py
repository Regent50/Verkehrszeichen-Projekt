from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_socketio import SocketIO, emit
import os
from vga_image_converter import convert_to_vga_format
from io import BytesIO

app = Flask(__name__, 
            template_folder=os.path.abspath('templates'),
            static_folder=os.path.abspath('static'))
app.secret_key = "geheimes_passwort"
socketio = SocketIO(app, cors_allowed_origins="*")

USERNAME = "admin"
PASSWORD = "1234"

# Existing routes remain unchanged
@app.route("/", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == USERNAME and password == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("main"))
        return render_template("login.html", error=True)
    return render_template("login.html")

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

@app.route("/update", methods=["POST"])
def update_sign():
    sign = request.form.get("sign")
    if sign:
        print(f"Verkehrszeichen aktualisiert: {sign}")
        socketio.emit("update_sign", {"sign": sign})
        return "Update erfolgreich", 200
    return "Fehler: Kein Sign-Parameter", 400

# New image handling endpoint
@app.route("/get_image/<image_name>")
def get_image(image_name):
    # List of valid image names
    valid_images = {
        "50kmh_schild.png",
        "baustelle_schild.png",
        "freifahrt_schild.png",
        "stop_schild.png"
    }
    
    if image_name not in valid_images:
        return "Invalid image name", 404
        
    # List of valid image names
    valid_images = ["50kmh_schild.png", "baustelle_schild.png", 
                   "freifahrt_schild.png", "stop_schild.png"]
    
    if image_name not in valid_images:
        return "Invalid image name", 404
        
    try:
        # Get path to image in static/signs folder
        image_path = os.path.join(app.static_folder, "signs", image_name)
        
        # Convert image to VGA format
        image_data = convert_to_vga_format(image_path)
        
        if image_data:
            # Return image as binary data
            return send_file(
                BytesIO(image_data),
                mimetype='application/octet-stream',
                as_attachment=True,
                download_name=f"{image_name}.vga"
            )
        return "Image conversion failed", 500
    except Exception as e:
        return f"Error: {str(e)}", 500




if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
