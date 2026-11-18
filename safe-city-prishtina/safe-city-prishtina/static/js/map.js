const map = createMap("map");
const markerLayer = L.layerGroup().addTo(map);
const categoryLabels = JSON.parse(document.getElementById("categoryData").textContent);
const filterCategory = document.getElementById("filterCategory");
const filterStatus = document.getElementById("filterStatus");
const focusId = new URLSearchParams(window.location.search).get("focus");
let focusDone = false;

function buildLegend() {
    const legend = document.getElementById("legend");
    Object.keys(categoryLabels).forEach(function (key) {
        const item = document.createElement("span");
        item.className = "legend-item";
        item.innerHTML = '<span class="legend-dot" style="background:' + CATEGORY_COLORS[key] + '"></span>' +
            escapeHtml(categoryLabels[key]);
        legend.appendChild(item);
    });
    const faded = document.createElement("span");
    faded.className = "legend-item";
    faded.textContent = "Faded pin = resolved";
    legend.appendChild(faded);
}

function popupHtml(report) {
    const statusText = report.status === "resolved" ? "Resolved" : "Open";
    return '<div class="popup-title">' + escapeHtml(report.title) + "</div>" +
        '<span class="badge badge-' + report.category + '">' + escapeHtml(report.category_label) + "</span> " +
        '<span class="badge status-' + report.status + '">' + statusText + "</span>" +
        '<p class="popup-text">' + escapeHtml(report.description) + "</p>" +
        '<div class="popup-meta">by ' + escapeHtml(report.username) + " &middot; " + report.created_at + "</div>";
}

async function loadReports() {
    const params = new URLSearchParams();
    if (filterCategory.value) {
        params.set("category", filterCategory.value);
    }
    if (filterStatus.value) {
        params.set("status", filterStatus.value);
    }

    const response = await fetch("/api/reports?" + params.toString());
    const reports = await response.json();

    markerLayer.clearLayers();

    reports.forEach(function (report) {
        const color = CATEGORY_COLORS[report.category] || CATEGORY_COLORS.other;
        const marker = L.marker([report.latitude, report.longitude], {
            icon: pinIcon(color, report.status === "resolved")
        });
        marker.bindPopup(popupHtml(report));
        marker.addTo(markerLayer);

        if (focusId && !focusDone && String(report.id) === focusId) {
            focusDone = true;
            map.setView([report.latitude, report.longitude], 17);
            marker.openPopup();
        }
    });
}

buildLegend();
filterCategory.addEventListener("change", loadReports);
filterStatus.addEventListener("change", loadReports);
loadReports();
