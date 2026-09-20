function openEditBox() {
    document.getElementById("editModal").classList.add("show");
}

function closeEditBox() {
    document.getElementById("editModal").classList.remove("show");
}



document.addEventListener("DOMContentLoaded", function () {

    const flashMessages = document.querySelectorAll(".flash-message");

    flashMessages.forEach(function (message) {

        setTimeout(function () {

            message.style.opacity = "0";

            setTimeout(function () {
                message.remove();
            }, 500);

        }, 5000);

    });

});




document.addEventListener("DOMContentLoaded", function () {

    const editField = document.getElementById("editField");
    const valueField = document.getElementById("valueField");

    editField.addEventListener("change", function () {

        if (this.value === "photo") {

            valueField.innerHTML = `
                <input
                    type="file"
                    name="photo"
                    id="editPhoto"
                    accept="image/*"
                >
            `;

        } else {

            valueField.innerHTML = `
                <input
                    type="text"
                    name="value"
                    id="editValue"
                    placeholder="Enter new value"
                    required
                >
            `;

        }

    });

});



function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");

    sidebar.classList.toggle("-translate-x-full");
}



function toggleSidebar() {

    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("sidebarOverlay");

    sidebar.classList.toggle("-translate-x-full");
    overlay.classList.toggle("hidden");
}