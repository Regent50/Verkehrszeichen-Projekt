function updateSign(sign) {
    fetch("/update", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: "sign=" + encodeURIComponent(sign)
    })
    .then(function (response) {
        if (response.ok) {
            messageHelpers.hide();
        } else {
            messageHelpers.show("Fehler beim Senden des Befehls");
        }
    })
    .catch(function () {
        messageHelpers.show("Server nicht erreichbar");
    });
}

const socket = io();
const mapController = SharedSocket.createRealMap({
    mapId: "map",
    statusElement: document.getElementById("map-status"),
    messageHelpers: null,
    userLabel: "Browser-Standort"
});

const textDisplay = document.getElementById("signText");
const imageDisplay = document.getElementById("signImage");
const statusBox = document.getElementById("socket-status");
const lastUpdate = document.getElementById("last-update");
const sensorFreshness = document.getElementById("sensor-freshness");
const uiMessage = document.getElementById("ui-message");
const uvValue = document.getElementById("uv-value");
const druckValue = document.getElementById("druck-value");
const tempValue = document.getElementById("temp-value");
const lfValue = document.getElementById("lf-value");

const messageHelpers = SharedSocket.createMessageHelpers(uiMessage);
const sensorState = SharedSocket.createSensorState({
    lastUpdateElement: lastUpdate,
    freshnessElement: sensorFreshness,
    messageHelpers: messageHelpers,
    staleDelay: 45000
});

socket.on("connect", function () {
    statusBox.innerText = "Server verbunden";
    sensorState.markConnected();
});

socket.on("disconnect", function () {
    statusBox.innerText = "Server getrennt";
    sensorState.markDisconnected();
});

socket.on("update_sign", function (data) {
    SharedSocket.applySign(data, {
        textElement: textDisplay,
        imageElement: imageDisplay,
        buttonSelector: "#sign-buttons button"
    });
});

socket.on("sensor_data", function (data) {
    sensorState.handleIncoming(data, {
        uv: uvValue,
        druck: druckValue,
        temperatur: tempValue,
        luftfeuchtigkeit: lfValue
    });
});
