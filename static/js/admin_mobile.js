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

const map = L.map("map").setView([52.52, 13.40], 12);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors"
}).addTo(map);

const deviceMarker = L.marker([52.52, 13.40]).addTo(map);
deviceMarker.bindPopup("Verkehrszeichen Gerät");

map.locate({ setView: true, maxZoom: 16 });

function onLocationFound(e) {
    const radius = e.accuracy / 2;

    L.marker(e.latlng).addTo(map)
        .bindPopup("Du bist hier (Genauigkeit: " + radius.toFixed(0) + "m)")
        .openPopup();

    L.circle(e.latlng, radius).addTo(map);

    const bounds = L.latLngBounds([e.latlng, deviceMarker.getLatLng()]);
    map.fitBounds(bounds, { padding: [30, 30] });
}

function onLocationError(e) {
    console.log("Standort konnte nicht ermittelt werden: " + e.message);
}

map.on("locationfound", onLocationFound);
map.on("locationerror", onLocationError);

setTimeout(function () {
    map.invalidateSize();
}, 200);

window.addEventListener("resize", function () {
    map.invalidateSize();
});

const textDisplay = document.getElementById("signText");
const imageDisplay = document.getElementById("signImage");
const statusBox = document.getElementById("socket-status");
const lastUpdate = document.getElementById("last-update");
const uiMessage = document.getElementById("ui-message");
const uvValue = document.getElementById("uv-value");
const druckValue = document.getElementById("druck-value");
const tempValue = document.getElementById("temp-value");
const lfValue = document.getElementById("lf-value");

const messageHelpers = SharedSocket.createMessageHelpers(uiMessage);

const resetSensorTimeout = SharedSocket.createSensorTimeout(function () {
    uvValue.innerText = "keine aktuellen Daten";
    druckValue.innerText = "keine aktuellen Daten";
    tempValue.innerText = "keine aktuellen Daten";
    lfValue.innerText = "keine aktuellen Daten";
    lastUpdate.innerText = "abgelaufen";
    messageHelpers.show("Keine aktuellen Sensordaten");
}, 15000);

socket.on("connect", function () {
    statusBox.innerText = "Server Status: verbunden";
    messageHelpers.hide();
});

socket.on("disconnect", function () {
    statusBox.innerText = "Server Status: getrennt";
    messageHelpers.show("Verbindung zum Server getrennt");
});

socket.on("update_sign", function (data) {
    SharedSocket.applySign(data, {
        textElement: textDisplay,
        imageElement: imageDisplay,
        buttonSelector: "#sign-buttons button"
    });
});

socket.on("sensor_data", function (data) {
    lastUpdate.innerText = new Date().toLocaleTimeString("de-DE");
    messageHelpers.hide();
    resetSensorTimeout();
    SharedSocket.applySensors(data, {
        uv: uvValue,
        druck: druckValue,
        temperatur: tempValue,
        luftfeuchtigkeit: lfValue
    });
});
