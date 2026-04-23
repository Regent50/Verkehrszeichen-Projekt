window.SharedSocket = (function () {
    const signImages = {
        "STOP": "/static/signs/stop_schild.png",
        "Geschwindigkeit 30": "/static/signs/schild_30.png",
        "Geschwindigkeit 50": "/static/signs/50kmh_schild.png",
        "Achtung Baustelle": "/static/signs/baustelle_schild.png",
        "Freie Fahrt": "/static/signs/freifahrt_schild.png"
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
        createSensorTimeout
    };
})();
