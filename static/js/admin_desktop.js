function togglePanel(panelId, triggerButton) {
    const panel = document.getElementById(panelId);
    const willOpen = !panel.classList.contains("open");

    document.querySelectorAll(".panel").forEach(function (p) {
        p.classList.remove("open");
    });

    document.querySelectorAll(".section-toggle").forEach(function (btn) {
        btn.classList.remove("open");
    });

    sidebarElement.classList.remove("has-open-panel");

    if (willOpen) {
        panel.classList.add("open");
        if (triggerButton) {
            triggerButton.classList.add("open");
        }
        sidebarElement.classList.add("has-open-panel");
    }
}

const sidebarElement = document.getElementById("sidebar");
const sidebarOpenButton = document.getElementById("sidebar-open-button");

function openSidebar() {
    sidebarElement.classList.remove("hidden");
    sidebarOpenButton.classList.add("hidden");
    sidebarElement.classList.remove("has-open-panel");
    setTimeout(function () {
        map.invalidateSize();
    }, 260);
}

function closeSidebar() {
    sidebarElement.classList.add("hidden");
    sidebarElement.classList.remove("has-open-panel");
    sidebarOpenButton.classList.remove("hidden");
    setTimeout(function () {
        map.invalidateSize();
    }, 260);
}

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

const mapController = SharedSocket.createRealMap({
    mapId: "map",
    statusElement: document.getElementById("map-status"),
    messageHelpers: null,
    userLabel: "Browser-Standort"
});
const map = mapController.map;

const socket = io();

const textDisplay = document.getElementById("signText");
const imageDisplay = document.getElementById("signImage");
const uvValue = document.getElementById("uv-value");
const druckValue = document.getElementById("druck-value");
const tempValue = document.getElementById("temp-value");
const lfValue = document.getElementById("lf-value");
const serverStatus = document.getElementById("server-status");
const lastUpdate = document.getElementById("last-update");
const sensorFreshness = document.getElementById("sensor-freshness");
const uiMessage = document.getElementById("ui-message");

const messageHelpers = SharedSocket.createMessageHelpers(uiMessage);
const sensorState = SharedSocket.createSensorState({
    lastUpdateElement: lastUpdate,
    freshnessElement: sensorFreshness,
    messageHelpers: messageHelpers,
    staleDelay: 45000
});

socket.on("connect", function () {
    serverStatus.innerText = "verbunden";
    sensorState.markConnected();
});

socket.on("disconnect", function () {
    serverStatus.innerText = "getrennt";
    sensorState.markDisconnected();
});

socket.on("update_sign", function (data) {
    SharedSocket.applySign(data, {
        textElement: textDisplay,
        imageElement: imageDisplay,
        buttonSelector: "#control-panel button"
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

window.addEventListener("load", function () {
    if (window.innerWidth <= 1100) {
        closeSidebar();
    } else {
        openSidebar();
    }
});
