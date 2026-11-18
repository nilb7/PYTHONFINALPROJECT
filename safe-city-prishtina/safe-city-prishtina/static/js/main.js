const menuToggle = document.getElementById("menuToggle");
const mainNav = document.getElementById("mainNav");

if (menuToggle) {
    menuToggle.addEventListener("click", function () {
        mainNav.classList.toggle("open");
    });
}

document.addEventListener("click", async function (event) {
    const resolveButton = event.target.closest(".js-resolve");
    const deleteButton = event.target.closest(".js-delete");

    if (resolveButton) {
        const response = await fetch("/api/reports/" + resolveButton.dataset.id + "/resolve", { method: "POST" });
        if (response.ok) {
            window.location.reload();
        } else {
            const data = await response.json();
            alert(data.error || "Something went wrong.");
        }
    }

    if (deleteButton) {
        if (!confirm("Are you sure you want to delete this report?")) {
            return;
        }
        const response = await fetch("/api/reports/" + deleteButton.dataset.id, { method: "DELETE" });
        if (response.ok) {
            window.location.reload();
        } else {
            const data = await response.json();
            alert(data.error || "Something went wrong.");
        }
    }
});
