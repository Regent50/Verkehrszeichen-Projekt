from flask import Flask, render_template, request  # request importieren
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

# Webseite anzeigen
@app.route("/")
def home():
    return render_template("index.html")

# WebSocket für Statusänderungen
@app.route("/update", methods=["POST"])
def update():
    sign = request.form.get("sign")
    if sign:
        print(f"Verkehrszeichen aktualisiert: {sign}")
        # Hier kannst du den WebSocket senden, um alle Clients zu benachrichtigen
        socketio.emit("update_sign", {"sign": sign})
    return "OK"


if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
