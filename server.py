from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify
from flask_socketio import SocketIO, emit
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

app.secret_key = "geheimes_passwort"
socketio = SocketIO(app, cors_allowed_origins="*")

USERNAME = "htl"
PASSWORD = "5AHEL"

STATE_FILE = os.path.join(BASE_DIR, "state.json")
AUTOMATION_STALE_SECONDS = 45
VALID_SIGNS = [
    "STOP",
    "Geschwindigkeit 30",
    "Geschwindigkeit 50",
    "Achtung Baustelle",
    "Freie Fahrt",
    "Gefahrstelle",
    "Achtung Glätte",
    "Schleudergefahr"
]
SIGN_IMAGES = {
    "STOP": "stop_schild.png",
    "Geschwindigkeit 30": "schild_30.png",
    "Geschwindigkeit 50": "50kmh_schild.png",
    "Achtung Baustelle": "baustelle_schild.png",
    "Freie Fahrt": "freifahrt_schild.png",
    "Gefahrstelle": "gefahrstelle_schild.png",
    "Achtung Glätte": "glaette_schild.png",
    "Schleudergefahr": "schleudergefahr_schild.png"
}

current_sign = None
current_mode = "manual"
sensor_last_update = None
current_sensor_data = {
    "uv": None,
    "druck": None,
    "temperatur": None,
    "luftfeuchtigkeit": None
}
automation_status = {
    "mode": current_mode,
    "sign": current_sign,
    "rule": "manual",
    "reason": "Manuelle Steuerung aktiv",
    "stale": False,
    "last_evaluated": None
}


def to_float_or_none(value):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def parse_iso(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def sanitize_sign(sign):
    if sign in VALID_SIGNS:
        return sign
    return None


def sensor_data_is_fresh(reference_time=None):
    if sensor_last_update is None:
        return False

    reference = reference_time or datetime.now()
    return (reference - sensor_last_update).total_seconds() <= AUTOMATION_STALE_SECONDS


def build_manual_status():
    return {
        "mode": "manual",
        "sign": current_sign,
        "rule": "manual",
        "reason": "Manuelle Steuerung aktiv",
        "stale": False,
        "last_evaluated": now_iso()
    }


def describe_auto_decision(sign, reason, rule, stale=False):
    return {
        "mode": "auto",
        "sign": sign,
        "rule": rule,
        "reason": reason,
        "stale": stale,
        "last_evaluated": now_iso()
    }


def evaluate_auto_sign():
    uv = current_sensor_data.get("uv")
    temperatur = current_sensor_data.get("temperatur")
    luftfeuchtigkeit = current_sensor_data.get("luftfeuchtigkeit")

    if not sensor_data_is_fresh():
        return describe_auto_decision(
            "Gefahrstelle",
            "Keine frischen Sensordaten verfügbar – sichere Warnanzeige aktiv.",
            "stale_data",
            stale=True
        )

    if temperatur is not None and luftfeuchtigkeit is not None and temperatur <= 3 and luftfeuchtigkeit >= 85:
        return describe_auto_decision(
            "Achtung Glätte",
            f"Temperatur {temperatur:.1f} °C und Luftfeuchtigkeit {luftfeuchtigkeit:.1f} % deuten auf Glätte hin.",
            "ice_risk"
        )

    if temperatur is not None and luftfeuchtigkeit is not None and temperatur <= 5 and luftfeuchtigkeit >= 78:
        return describe_auto_decision(
            "Schleudergefahr",
            f"Kühl-feuchte Bedingungen ({temperatur:.1f} °C / {luftfeuchtigkeit:.1f} %) erhöhen das Rutschrisiko.",
            "skid_risk"
        )

    if uv is not None and luftfeuchtigkeit is not None and uv <= 250 and luftfeuchtigkeit >= 80:
        return describe_auto_decision(
            "Gefahrstelle",
            f"Sehr geringe Helligkeit (UV {uv:.0f}) bei hoher Feuchtigkeit ({luftfeuchtigkeit:.1f} %) – Sichtwarnung aktiv.",
            "poor_visibility"
        )

    if uv is not None and uv <= 350:
        return describe_auto_decision(
            "Geschwindigkeit 30",
            f"Niedrige Helligkeit (UV {uv:.0f}) – vorsichtige Temporeduktion aktiv.",
            "reduced_speed_low_light"
        )

    if uv is not None and temperatur is not None and luftfeuchtigkeit is not None and uv >= 800 and 12 <= temperatur <= 28 and luftfeuchtigkeit < 75:
        return describe_auto_decision(
            "Freie Fahrt",
            f"Gute Bedingungen erkannt: UV {uv:.0f}, Temperatur {temperatur:.1f} °C, Luftfeuchtigkeit {luftfeuchtigkeit:.1f} %.",
            "clear_conditions"
        )

    return describe_auto_decision(
        "Geschwindigkeit 50",
        "Normale Bedingungen erkannt – Standardfreigabe aktiv.",
        "default_normal"
    )


def emit_sign_and_mode():
    socketio.emit("update_sign", {"sign": current_sign})
    socketio.emit("automation_status", automation_status)


def apply_auto_sign():
    global current_sign, automation_status

    automation_status = evaluate_auto_sign()
    current_sign = automation_status["sign"]


def load_state():
    global current_sign, current_sensor_data, current_mode, sensor_last_update, automation_status

    if not os.path.exists(STATE_FILE):
        return

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)

        current_sign = sanitize_sign(state.get("current_sign"))
        current_mode = state.get("current_mode", "manual")
        if current_mode not in {"manual", "auto"}:
            current_mode = "manual"

        sensor_last_update = parse_iso(state.get("sensor_last_update"))
        loaded_sensor_data = state.get("current_sensor_data", {})

        current_sensor_data["uv"] = to_float_or_none(loaded_sensor_data.get("uv"))
        current_sensor_data["druck"] = to_float_or_none(loaded_sensor_data.get("druck"))
        current_sensor_data["temperatur"] = to_float_or_none(loaded_sensor_data.get("temperatur"))
        current_sensor_data["luftfeuchtigkeit"] = to_float_or_none(loaded_sensor_data.get("luftfeuchtigkeit"))

        if current_mode == "auto":
            apply_auto_sign()
        else:
            automation_status = build_manual_status()

    except Exception as e:
        print("Fehler beim Laden des Status:", e)


def save_state():
    state = {
        "current_sign": current_sign,
        "current_mode": current_mode,
        "sensor_last_update": sensor_last_update.isoformat(timespec="seconds") if sensor_last_update else None,
        "current_sensor_data": current_sensor_data,
        "automation_status": automation_status
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

        return render_template("LOGIN.html", error=True)

    return render_template("LOGIN.html", error=False)


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
    global current_sign, current_mode, automation_status

    sign = request.form.get("sign")

    if not sign:
        return "Fehler: Kein Sign-Parameter", 400

    sign = sanitize_sign(sign)
    if not sign:
        return "Fehler: Ungültiges Verkehrszeichen", 400

    current_mode = "manual"
    current_sign = sign
    automation_status = build_manual_status()
    save_state()
    print(f"Verkehrszeichen aktualisiert: {sign}")

    emit_sign_and_mode()
    return jsonify({"status": "ok", "sign": sign, "mode": current_mode}), 200


@app.route("/set-mode", methods=["POST"])
@app.route("/set_mode", methods=["POST"])
def set_mode():
    global current_mode, automation_status

    mode = request.form.get("mode") or (request.get_json(silent=True) or {}).get("mode")

    if mode not in {"manual", "auto"}:
        return jsonify({"status": "error", "message": "Ungültiger Modus"}), 400

    current_mode = mode

    if current_mode == "auto":
        apply_auto_sign()
    else:
        automation_status = build_manual_status()

    save_state()
    emit_sign_and_mode()
    return jsonify({"status": "ok", "mode": current_mode, "sign": current_sign, "automation": automation_status}), 200


@app.route("/sensor-update", methods=["POST"])
@app.route("/sensor_update", methods=["POST"])
def sensor_update():
    global current_sensor_data, sensor_last_update

    data = request.get_json(silent=True)

    if not data:
        data = request.form.to_dict()

    if not data:
        return jsonify({"status": "error", "message": "Keine Sensordaten erhalten"}), 400

    new_sensor_data = {
        "uv": to_float_or_none(data.get("uv")),
        "druck": to_float_or_none(data.get("druck")),
        "temperatur": to_float_or_none(data.get("temperatur")),
        "luftfeuchtigkeit": to_float_or_none(data.get("luftfeuchtigkeit"))
    }

    if all(value is None for value in new_sensor_data.values()):
        return jsonify({"status": "error", "message": "Keine gültigen Sensordaten"}), 400

    current_sensor_data = new_sensor_data
    sensor_last_update = datetime.now()

    if current_mode == "auto":
        apply_auto_sign()

    save_state()

    print("Neue Sensordaten empfangen:", current_sensor_data)

    socketio.emit("sensor_data", current_sensor_data)
    if current_mode == "auto":
        emit_sign_and_mode()
    else:
        socketio.emit("automation_status", automation_status)

    return jsonify({
        "status": "ok",
        "data": current_sensor_data,
        "mode": current_mode,
        "sign": current_sign,
        "automation": automation_status
    }), 200


@app.route("/get-sensor-data", methods=["GET"])
@app.route("/get_sensor_data", methods=["GET"])
def get_sensor_data():
    return jsonify(current_sensor_data), 200


@app.route("/get-current-sign", methods=["GET"])
@app.route("/get_current_sign", methods=["GET"])
def get_current_sign():
    return jsonify({"sign": current_sign}), 200


@app.route("/automation-status", methods=["GET"])
@app.route("/automation_status", methods=["GET"])
def get_automation_status():
    return jsonify(automation_status), 200


@app.route("/get-image/<image_name>")
@app.route("/get_image/<image_name>")
def get_image(image_name):
    valid_images = list(SIGN_IMAGES.values())

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
    emit("automation_status", automation_status)


if __name__ == "__main__":
    print("Server wird gestartet...")
    load_state()
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
