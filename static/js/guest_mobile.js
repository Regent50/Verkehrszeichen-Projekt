
const socket = io();

const systemStatus = document.getElementById("system-status");
const currentSign = document.getElementById("current-sign");
const lastUpdate = document.getElementById("last-update");
const uiMessage = document.getElementById("ui-message");

const uvValue = document.getElementById("uv-value");
const druckValue = document.getElementById("druck-value");
const tempValue = document.getElementById("temp-value");
const lfValue = document.getElementById("lf-value");

let userMarker = null;
let userCircle = null;

const map = L.map("map").setView([48.2082, 16.3738], 12);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors"
}).addTo(map);

const systemMarker = L.marker([48.2082, 16.3738]).addTo(map);
systemMarker.bindPopup("Hauptsystem");

const infoMarker = L.marker([48.2140, 16.3810]).addTo(map);
infoMarker.bindPopup("Infopunkt");

function showMessage(text) {
    uiMessage.innerText = text;
    uiMessage.style.display = "block";
}

function hideMessage() {
    uiMessage.innerText = "";
    uiMessage.style.display = "none";
}

function focusOnSystem() {
    map.setView(systemMarker.getLatLng(), 15);
    systemMarker.openPopup();
}

function focusOnUser() {
    if (userMarker) {
        map.setView(userMarker.getLatLng(), 15);
        userMarker.openPopup();
    } else {
        showMessage("Kein Benutzerstandort verfügbar");
    }
}

function fitAllMarkers() {
    const points = [systemMarker.getLatLng(), infoMarker.getLatLng()];
    if (userMarker) {
        points.push(userMarker.getLatLng());
    }
    const bounds = L.latLngBounds(points);
    map.fitBounds(bounds, { padding: [30, 30] });
}

map.locate({ setView: false, maxZoom: 16 });

function onLocationFound(e) {
    const radius = e.accuracy / 2;

    if (userMarker) {
        map.removeLayer(userMarker);
    }

    if (userCircle) {
        map.removeLayer(userCircle);
    }

    userMarker = L.marker(e.latlng).addTo(map);
    userMarker.bindPopup("Dein Standort");

    userCircle = L.circle(e.latlng, radius).addTo(map);
    fitAllMarkers();
}

function onLocationError(e) {
    console.log("Standort konnte nicht ermittelt werden: " + e.message);
}

map.on("locationfound", onLocationFound);
map.on("locationerror", onLocationError);

setTimeout(function() {
    map.invalidateSize();
}, 200);

window.addEventListener("resize", function() {
    map.invalidateSize();
});

socket.on("connect", function() {
    systemStatus.innerText = "System online";
    hideMessage();
});

socket.on("disconnect", function() {
    systemStatus.innerText = "System offline";
    showMessage("Verbindung zum Server getrennt");
});

socket.on("update_sign", function(data) {
    currentSign.innerText = data.sign || "Keines";
});

socket.on("sensor_data", function(data) {
    const now = new Date();
    lastUpdate.innerText = now.toLocaleTimeString("de-DE");
    hideMessage();

    if (data.uv !== undefined && data.uv !== null) {
        uvValue.innerText = data.uv + " UV";
    }

    if (data.druck !== undefined && data.druck !== null) {
        druckValue.innerText = data.druck + " hPa";
    }

    if (data.temperatur !== undefined && data.temperatur !== null) {
        tempValue.innerText = data.temperatur + " °C";
    }

    if (data.luftfeuchtigkeit !== undefined && data.luftfeuchtigkeit !== null) {
        lfValue.innerText = data.luftfeuchtigkeit + " %";
    }
});
