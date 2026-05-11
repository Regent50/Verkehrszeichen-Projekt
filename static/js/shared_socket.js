window.SharedSocket = (function () {
    const signImages = {
        "STOP": "/static/signs/stop_schild.png",
        "Geschwindigkeit 30": "/static/signs/schild_30.png",
        "Geschwindigkeit 50": "/static/signs/50kmh_schild.png",
        "Achtung Baustelle": "/static/signs/baustelle_schild.png",
        "Freie Fahrt": "/static/signs/freifahrt_schild.png",
        "Gefahrstelle": "/static/signs/gefahrstelle_schild.png",
        "Achtung Glätte": "/static/signs/glaette_schild.png",
        "Schleudergefahr": "/static/signs/schleudergefahr_schild.png"
    };

    function createMessageHelpers(messageElement) {
        return {
            show(text) {
                if (!messageElement) return;
                messageElement.innerText = text;
                messageElement.style.display = "block";
            },
            hide() {
                if (!messageElement) return;
                messageElement.style.display = "none";
                messageElement.innerText = "";
            }
        };
    }

    function formatTime(date) {
        return date.toLocaleTimeString("de-DE");
    }

    function applySign(data, options) {
        const sign = data && data.sign ? data.sign : "Kein Verkehrszeichen";

        if (options.textElement) {
            options.textElement.innerText = sign;
        }

        if (options.buttonSelector) {
            document.querySelectorAll(options.buttonSelector).forEach(function (button) {
                button.classList.remove("active-sign");
            });

            const activeButton = document.querySelector(options.buttonSelector + '[data-sign="' + (data ? data.sign : "") + '"]');
            if (activeButton) {
                activeButton.classList.add("active-sign");
            }
        }

        if (options.imageElement) {
            if (data && data.sign && signImages[data.sign]) {
                options.imageElement.src = signImages[data.sign];
                options.imageElement.style.display = "block";
            } else {
                options.imageElement.src = "";
                options.imageElement.style.display = "none";
            }
        }
    }

    function applySensors(data, sensorElements) {
        if (!data) return;

        if (data.uv !== undefined && data.uv !== null && sensorElements.uv) {
            sensorElements.uv.innerText = data.uv + " UV";
        }

        if (data.druck !== undefined && data.druck !== null && sensorElements.druck) {
            sensorElements.druck.innerText = data.druck + " hPa";
        }

        if (data.temperatur !== undefined && data.temperatur !== null && sensorElements.temperatur) {
            sensorElements.temperatur.innerText = data.temperatur + " °C";
        }

        if (data.luftfeuchtigkeit !== undefined && data.luftfeuchtigkeit !== null && sensorElements.luftfeuchtigkeit) {
            sensorElements.luftfeuchtigkeit.innerText = data.luftfeuchtigkeit + " %";
        }
    }

    function createSensorState(options) {
        const staleDelay = options && options.staleDelay ? options.staleDelay : 45000;
        const lastUpdateElement = options ? options.lastUpdateElement : null;
        const freshnessElement = options ? options.freshnessElement : null;
        const messageHelpers = options ? options.messageHelpers : null;
        const staleMessage = options && options.staleMessage ? options.staleMessage : "Keine neuen Sensordaten – letzte Werte bleiben sichtbar";
        const connectionMessage = options && options.connectionMessage ? options.connectionMessage : "Verbindung zum Server getrennt";

        let timeoutId = null;
        let lastTimestamp = null;

        function setFreshnessText(text, isStale) {
            if (!freshnessElement) return;
            freshnessElement.innerText = text;
            freshnessElement.classList.toggle("stale", !!isStale);
        }

        function markFresh(timestamp) {
            lastTimestamp = timestamp || new Date();
            if (lastUpdateElement) {
                lastUpdateElement.innerText = formatTime(lastTimestamp);
            }
            setFreshnessText("aktuell", false);
            if (messageHelpers) {
                messageHelpers.hide();
            }
        }

        function markStale() {
            if (!lastTimestamp) {
                setFreshnessText("warte auf erste Daten", true);
                return;
            }

            setFreshnessText("letzte Werte von " + formatTime(lastTimestamp), true);
            if (messageHelpers) {
                messageHelpers.show(staleMessage);
            }
        }

        function resetStaleTimer() {
            if (timeoutId) {
                clearTimeout(timeoutId);
            }

            timeoutId = setTimeout(function () {
                markStale();
            }, staleDelay);
        }

        return {
            handleIncoming(data, sensorElements) {
                applySensors(data, sensorElements);
                markFresh(new Date());
                resetStaleTimer();
            },
            markConnected() {
                if (messageHelpers) {
                    messageHelpers.hide();
                }
                if (lastTimestamp) {
                    setFreshnessText("letzte Werte von " + formatTime(lastTimestamp), false);
                } else {
                    setFreshnessText("warte auf erste Daten", false);
                }
            },
            markDisconnected() {
                if (timeoutId) {
                    clearTimeout(timeoutId);
                }

                if (lastTimestamp) {
                    setFreshnessText("letzte Werte von " + formatTime(lastTimestamp), true);
                } else {
                    setFreshnessText("offline – keine Daten", true);
                }

                if (messageHelpers) {
                    messageHelpers.show(connectionMessage);
                }
            }
        };
    }

    function createRealMap(options) {
        const map = L.map(options.mapId, {
            zoomControl: true,
            attributionControl: true
        }).setView([20, 0], 2);

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: "&copy; OpenStreetMap contributors"
        }).addTo(map);

        const messageHelpers = options.messageHelpers || null;
        const statusElement = options.statusElement || null;
        const userLabel = options.userLabel || "Dein Standort";
        const systemLabel = options.systemLabel || "System";
        const systemLocation = options.systemLocation || null;

        let userMarker = null;
        let userCircle = null;
        let systemMarker = null;

        function setStatus(text) {
            if (statusElement) {
                statusElement.innerText = text;
            }
        }

        if (systemLocation && Array.isArray(systemLocation) && systemLocation.length === 2) {
            systemMarker = L.marker(systemLocation).addTo(map);
            systemMarker.bindPopup(systemLabel);
        }

        function availablePoints() {
            const points = [];
            if (systemMarker) points.push(systemMarker.getLatLng());
            if (userMarker) points.push(userMarker.getLatLng());
            return points;
        }

        function fitAvailable() {
            const points = availablePoints();

            if (points.length >= 2) {
                map.fitBounds(L.latLngBounds(points), { padding: [32, 32] });
                return true;
            }

            if (points.length === 1) {
                map.setView(points[0], 15);
                return true;
            }

            map.setView([20, 0], 2);
            return false;
        }

        function focusOnUser() {
            if (userMarker) {
                map.setView(userMarker.getLatLng(), 15);
                userMarker.openPopup();
            } else if (messageHelpers) {
                messageHelpers.show("Noch kein echter Benutzerstandort verfügbar");
            }
        }

        function focusOnSystem() {
            if (systemMarker) {
                map.setView(systemMarker.getLatLng(), 15);
                systemMarker.openPopup();
            } else if (messageHelpers) {
                messageHelpers.show("Kein echter Systemstandort hinterlegt");
            }
        }

        function onLocationFound(e) {
            const radius = e.accuracy / 2;

            if (userMarker) {
                map.removeLayer(userMarker);
            }

            if (userCircle) {
                map.removeLayer(userCircle);
            }

            userMarker = L.marker(e.latlng).addTo(map);
            userMarker.bindPopup(userLabel);

            userCircle = L.circle(e.latlng, radius).addTo(map);

            fitAvailable();
            setStatus(systemMarker ? "Echte Punkte aktiv" : "Nur echter Benutzerstandort aktiv");
        }

        function onLocationError() {
            setStatus(systemMarker ? "Nur Systemstandort sichtbar" : "Keine echten Punkte verfügbar");
        }

        map.on("locationfound", onLocationFound);
        map.on("locationerror", onLocationError);

        map.locate({ setView: false, maxZoom: 16 });
        setStatus(systemMarker ? "Suche Benutzerstandort..." : "Suche echten Standort...");

        setTimeout(function () {
            map.invalidateSize();
            fitAvailable();
        }, 220);

        window.addEventListener("resize", function () {
            map.invalidateSize();
        });

        return {
            map,
            focusOnUser,
            focusOnSystem,
            fitAvailable,
            setStatus,
            hasSystemLocation() {
                return !!systemMarker;
            }
        };
    }

    function createSensorTimeout(callback, delay) {
        let timeoutId = null;

        return function reset() {
            if (timeoutId) {
                clearTimeout(timeoutId);
            }

            timeoutId = setTimeout(function () {
                callback();
            }, delay);
        };
    }

    return {
        signImages,
        createMessageHelpers,
        applySign,
        applySensors,
        createSensorState,
        createRealMap,
        createSensorTimeout
    };
})();
