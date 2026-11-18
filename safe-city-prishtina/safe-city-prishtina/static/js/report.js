const map = createMap("map");
const form = document.getElementById("reportForm");
const formError = document.getElementById("formError");
const pinInfo = document.getElementById("pinInfo");
const locateBtn = document.getElementById("locateBtn");
let pin = null;

function updatePinInfo() {
    const position = pin.getLatLng();
    pinInfo.textContent = "Pin placed at " + position.lat.toFixed(5) + ", " + position.lng.toFixed(5);
}

function placePin(latlng) {
    if (pin === null) {
        pin = L.marker(latlng, { draggable: true, icon: pinIcon("#c0392b", false) }).addTo(map);
        pin.on("dragend", updatePinInfo);
    } else {
        pin.setLatLng(latlng);
    }
    updatePinInfo();
}

function showError(message) {
    formError.textContent = message;
    formError.classList.remove("hidden");
}

map.on("click", function (event) {
    placePin(event.latlng);
});

locateBtn.addEventListener("click", function () {
    if (!navigator.geolocation) {
        showError("Your browser does not support location.");
        return;
    }
    navigator.geolocation.getCurrentPosition(
        function (result) {
            const latlng = L.latLng(result.coords.latitude, result.coords.longitude);
            placePin(latlng);
            map.setView(latlng, 17);
        },
        function () {
            showError("Could not get your location. Click on the map instead.");
        }
    );
});

form.addEventListener("submit", async function (event) {
    event.preventDefault();
    formError.classList.add("hidden");

    if (pin === null) {
        showError("Please click on the map to place a pin first.");
        return;
    }

    const position = pin.getLatLng();
    const payload = {
        title: document.getElementById("title").value,
        category: document.getElementById("category").value,
        description: document.getElementById("description").value,
        latitude: position.lat,
        longitude: position.lng
    };

    const response = await fetch("/api/reports", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });
    const data = await response.json();

    if (response.ok) {
        window.location.href = "/map?focus=" + data.id;
    } else {
        showError(data.error || "Something went wrong.");
    }
});
