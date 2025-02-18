from flask import Flask, render_template, request, redirect, url_for, session
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

if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
