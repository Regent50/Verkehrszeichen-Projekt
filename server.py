from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify
from flask_socketio import SocketIO, emit
import os
import json

app = Flask(
    __name__,
    template_folder=os.path.abspath("templates"),
    static_folder=os.path.abspath("static")
)

app.secret_key = "geheimes_passwort"
socketio = SocketIO(app, cors_allowed_origins="*")

USERNAME = "htl"
PASSWORD = "5AHEL"

STATE_FILE = "state.json"

current_sign = None
current_sensor_data = {
    "uv": None,
    "druck": None,
    "temperatur": None,
    "luftfeuchtigkeit": None
}


def to_float_or_none(value):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def load_state():
    global current_sign, current_sensor_data

    if not os.path.exists(STATE_FILE):
        return

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)

        current_sign = state.get("current_sign")
        current_sensor_data = state.get("current_sensor_data", current_sensor_data)
    except Exception as e:
        print("Fehler beim Laden des Status:", e)


def save_state():
    state = {
        "current_sign": current_sign,
        "current_sensor_data": current_sensor_data
    }

    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Fehler beim Speichern des Status:", e)


@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "-1"
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response


@app.route("/", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        view_mode = request.form.get("view_mode", "desktop")

        if username == USERNAME and password == PASSWORD:
            session["logged_in"] = True
            print(f"Login erfolgreich für: {username}")

            if view_mode == "mobile":
                return redirect(url_for("admin_mobile"))
            return redirect(url_for("admin_desktop"))

        return render_template("login.html", error=True)

    return render_template("login.html", error=False)


@app.route("/admin")
def admin_desktop():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("admin_desktop.html")


@app.route("/admin-mobile")
def admin_mobile():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("admin_mobile.html")


@app.route("/live-sign")
def live_sign():
    return render_template("live_sign.html")


@app.route("/guest")
def guest_select():
    return render_template("guest_select.html")


@app.route("/guest-desktop")
def guest_desktop():
    return render_template("guest_desktop.html")


@app.route("/guest-mobile")
def guest_mobile():
    return render_template("guest_mobile.html")


# Rückwärtskompatible alte Routen
@app.route("/main")
def main():
    return redirect(url_for("admin_desktop"))


@app.route("/mobile")
def mobile():
    return redirect(url_for("admin_mobile"))


@app.route("/kontrolle")
def kontrolle():
    return redirect(url_for("admin_desktop"))


@app.route("/verkehrszeichen")
def verkehrszeichen():
    return redirect(url_for("admin_desktop"))


@app.route("/verkehrszeichen1")
def verkehrszeichen1():
    return redirect(url_for("live_sign"))


@app.route("/guestm")
def main_guest():
    return redirect(url_for("guest_desktop"))


@app.route("/guestmobile")
def mobile_guest():
    return redirect(url_for("guest_mobile"))


@app.route("/guestv")
def verkehrszeichen_guest():
    return redirect(url_for("live_sign"))


@app.route("/update", methods=["POST"])
def update_sign():
    global current_sign

    sign = request.form.get("sign")

    if not sign:
        return "Fehler: Kein Sign-Parameter", 400

    current_sign = sign
    save_state()
    print(f"Verkehrszeichen aktualisiert: {sign}")

    socketio.emit("update_sign", {"sign": sign})
    return "Update erfolgreich", 200


@app.route("/sensor-update", methods=["POST"])
@app.route("/sensor_update", methods=["POST"])
def sensor_update():
    global current_sensor_data

    data = request.get_json(silent=True)

    if not data:
        data = request.form.to_dict()

    if not data:
        return jsonify({"status": "error", "message": "Keine Sensordaten erhalten"}), 400

    current_sensor_data = {
        "uv": to_float_or_none(data.get("uv")),
        "druck": to_float_or_none(data.get("druck")),
        "temperatur": to_float_or_none(data.get("temperatur")),
        "luftfeuchtigkeit": to_float_or_none(data.get("luftfeuchtigkeit"))
    }

    if all(value is None for value in current_sensor_data.values()):
        return jsonify({"status": "error", "message": "Keine gültigen Sensordaten"}), 400

    save_state()
    print("Neue Sensordaten empfangen:", current_sensor_data)

    socketio.emit("sensor_data", current_sensor_data)
    return jsonify({"status": "ok", "data": current_sensor_data}), 200


@app.route("/get-image/<image_name>")
@app.route("/get_image/<image_name>")
def get_image(image_name):
    valid_images = [
        "50kmh_schild.png",
        "baustelle_schild.png",
        "freifahrt_schild.png",
        "stop_schild.png",
        "schild_30.png"
    ]

    if image_name not in valid_images:
        return "Invalid image name", 404

    try:
        image_path = os.path.join(app.static_folder, "signs", image_name)

        if not os.path.isfile(image_path):
            return f"Bild {image_name} nicht gefunden", 404

        return send_file(image_path, mimetype="image/png")
    except Exception as e:
        return f"Error: {str(e)}", 500


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@socketio.on("connect")
def handle_connect():
    print("Ein Client hat sich verbunden.")
    emit("message", {"message": "Verbindung hergestellt!"})

    if current_sign:
        emit("update_sign", {"sign": current_sign})

    emit("sensor_data", current_sensor_data)


if __name__ == "__main__":
    print("Server wird gestartet...")
    load_state()
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)