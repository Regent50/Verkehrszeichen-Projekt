const socket = io();

const systemStatus = document.getElementById("system-status");
const currentSign = document.getElementById("current-sign");
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
const mapController = SharedSocket.createRealMap({
    mapId: "map",
    statusElement: document.getElementById("map-status"),
    messageHelpers: messageHelpers,
    userLabel: "Dein Standort"
});

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
    sensorState.markConnected();
});

socket.on("disconnect", function() {
    systemStatus.innerText = "System offline";
    sensorState.markDisconnected();
});

socket.on("update_sign", function(data) {
    currentSign.innerText = data.sign || "Keines";
});

socket.on("sensor_data", function(data) {
    sensorState.handleIncoming(data, {
        uv: uvValue,
        druck: druckValue,
        temperatur: tempValue,
        luftfeuchtigkeit: lfValue
    });
});
