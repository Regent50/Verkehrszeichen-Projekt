function updateClock() {
    document.getElementById("clock").innerText = new Date().toLocaleTimeString("de-DE");
}

setInterval(updateClock, 1000);
updateClock();

const socket = io({ transports: ["websocket"] });
const imageDisplay = document.getElementById("signImage");

socket.on("connect", function () {
    document.getElementById("statusText").innerText = "ONLINE";
    document.getElementById("statusText").style.color = "#00c851";
});

socket.on("disconnect", function () {
    document.getElementById("statusText").innerText = "OFFLINE";
    document.getElementById("statusText").style.color = "red";
});

socket.on("update_sign", function (data) {
    if (data.sign && SharedSocket.signImages[data.sign]) {
        imageDisplay.classList.remove("animate-fade");
        imageDisplay.src = SharedSocket.signImages[data.sign];
        imageDisplay.style.display = "block";
        setTimeout(function () {
            imageDisplay.classList.add("animate-fade");
        }, 10);
    } else {
        imageDisplay.style.display = "none";
    }
});
