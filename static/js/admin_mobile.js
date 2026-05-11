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

function setMode(mode) {
    fetch("/set-mode", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: "mode=" + encodeURIComponent(mode)
    })
    .then(function (response) {
        return response.json().then(function (data) {
            return { ok: response.ok, data: data };
        });
    })
    .then(function (result) {
        if (!result.ok) {
            throw new Error(result.data && result.data.message ? result.data.message : "Modus konnte nicht gesetzt werden");
        }
        messageHelpers.hide();
    })
    .catch(function (error) {
        messageHelpers.show(error.message || "Automatik konnte nicht umgeschaltet werden");
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
const automationMode = document.getElementById("automation-mode");
const automationRule = document.getElementById("automation-rule");
const automationTime = document.getElementById("automation-time");
const automationReason = document.getElementById("automation-reason");

const messageHelpers = SharedSocket.createMessageHelpers(uiMessage);
const sensorState = SharedSocket.createSensorState({
    lastUpdateElement: lastUpdate,
    freshnessElement: sensorFreshness,
    messageHelpers: messageHelpers,
    staleDelay: 45000
});

function applyAutomationStatus(data) {
    if (!data) return;

    automationMode.innerText = data.mode === "auto" ? "AUTOMATIK" : "MANUELL";
    automationRule.innerText = data.rule || "manual";
    automationTime.innerText = data.last_evaluated || "noch keine";
    automationReason.innerText = data.reason || "Kein Status verfügbar";
    automationMode.classList.toggle("auto-active", data.mode === "auto");
    automationReason.classList.toggle("is-stale", !!data.stale);

    document.querySelectorAll(".mode-button").forEach(function (button) {
        button.classList.toggle("active-mode", button.dataset.mode === data.mode);
    });
}

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

socket.on("automation_status", function (data) {
    applyAutomationStatus(data);
});
