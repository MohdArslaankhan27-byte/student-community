document.addEventListener("DOMContentLoaded", function () {

    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("sidebarOverlay");
    const menuToggle = document.getElementById("menuToggle");

    const menuItems = document.querySelectorAll(".menu-item[data-snippet]");
    const snippets = document.querySelectorAll("#snippets > div");

    /*
    ==========================================
    SIDEBAR OPEN / CLOSE
    ==========================================
    */

    function openSidebar() {
        sidebar.classList.add("active");
        overlay.classList.add("active");
    }

    function closeSidebar() {
        sidebar.classList.remove("active");
        overlay.classList.remove("active");
    }

    menuToggle.addEventListener("click", function () {

        if (sidebar.classList.contains("active")) {
            closeSidebar();
        } else {
            openSidebar();
        }

    });

    // Clicking outside sidebar closes it
    overlay.addEventListener("click", function () {
        closeSidebar();
    });


    /*
    ==========================================
    MANAGEMENT SNIPPETS
    ==========================================
    */

    // Hide all snippets when page loads
    snippets.forEach(function (snippet) {
        snippet.style.display = "none";
    });


    menuItems.forEach(function (item) {

        item.addEventListener("click", function (event) {

            event.preventDefault();

            const snippetId = this.getAttribute("data-snippet");

            // Hide all snippets
            snippets.forEach(function (snippet) {
                snippet.style.display = "none";
            });

            // Hide instruction message
            const instructions = document.getElementById("sidebarInstructions");

            if (instructions) {
                instructions.style.display = "none";
            }

            // Find selected snippet
            const selectedSnippet = document.getElementById(snippetId);

            if (selectedSnippet) {
                selectedSnippet.style.display = "block";
            }

            // Close sidebar after selecting an option
            closeSidebar();

        });

    });

});





const uploadMarksForm = document.getElementById("uploadMarksForm");

if (uploadMarksForm) {

    uploadMarksForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const formData = new FormData(uploadMarksForm);

        try {

            const response = await fetch(uploadMarksForm.action, {
                method: "POST",
                body: formData
            });

            const result = await response.json();

            if (result.success) {

                alert(result.message);

                uploadMarksForm.reset();

            } else {

                alert(result.message);

            }

        } catch (error) {

            console.error(error);

            alert("Something went wrong while uploading marks.");

        }

    });

}



