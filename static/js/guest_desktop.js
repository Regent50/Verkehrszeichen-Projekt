const socket = io();

const systemStatus = document.getElementById("system-status");
const socketText = document.getElementById("socket-text");
const currentSign = document.getElementById("current-sign");
const signStateText = document.getElementById("sign-state-text");
const deviceSignLabel = document.getElementById("device-sign-label");
const lastUpdate = document.getElementById("last-update");
const sensorFreshness = document.getElementById("sensor-freshness");
const headerSensorFreshness = document.getElementById("header-sensor-freshness");
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
const mapController = SharedSocket.createRealMap({
    mapId: "map",
    statusElement: document.getElementById("map-status"),
    messageHelpers: messageHelpers,
    userLabel: "Dein Standort"
});

function syncHeaderFreshness() {
    headerSensorFreshness.innerText = sensorFreshness.innerText;
    headerSensorFreshness.classList.toggle("stale", sensorFreshness.classList.contains("stale"));
}

function focusOnSystem() {
    mapController.focusOnSystem();
}

function focusOnUser() {
    mapController.focusOnUser();
}

function fitAllMarkers() {
    mapController.fitAvailable();
}

socket.on("connect", function() {
    systemStatus.innerText = "System online";
    socketText.innerText = "verbunden";
    sensorState.markConnected();
    syncHeaderFreshness();
});

socket.on("disconnect", function() {
    systemStatus.innerText = "System offline";
    socketText.innerText = "getrennt";
    sensorState.markDisconnected();
    syncHeaderFreshness();
});

socket.on("update_sign", function(data) {
    const sign = data.sign || "Keines";
    currentSign.innerText = sign;
    deviceSignLabel.innerText = sign;
    signStateText.innerText = "aktuell aktiv: " + sign;
});

socket.on("sensor_data", function(data) {
    sensorState.handleIncoming(data, {
        uv: uvValue,
        druck: druckValue,
        temperatur: tempValue,
        luftfeuchtigkeit: lfValue
    });
    syncHeaderFreshness();
});
