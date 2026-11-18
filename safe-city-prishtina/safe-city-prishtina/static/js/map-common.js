const PRISHTINA_CENTER = [42.6629, 21.1655];
const PRISHTINA_BOUNDS = [[42.55, 21.0], [42.75, 21.3]];

const CATEGORY_COLORS = {
    trash: "#8d6e63",
    road: "#e67e22",
    light: "#c9a100",
    water: "#3498db",
    traffic: "#9b59b6",
    other: "#7f8c8d"
};

function createMap(elementId) {
    const map = L.map(elementId, {
        maxBounds: PRISHTINA_BOUNDS,
        maxBoundsViscosity: 0.8,
        minZoom: 11
    }).setView(PRISHTINA_CENTER, 13);

    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: "&copy; OpenStreetMap contributors"
    }).addTo(map);

    return map;
}

function pinIcon(color, faded) {
    const opacity = faded ? 0.55 : 1;
    return L.divIcon({
        className: "pin-wrapper",
        html: '<span class="pin" style="background:' + color + ";opacity:" + opacity + '"></span>',
        iconSize: [30, 38],
        iconAnchor: [15, 36],
        popupAnchor: [0, -34]
    });
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}
