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



async function fetchStudentMarks() {
    const rollNumber = document.getElementById("search_roll_number").value.trim();
    const resultDiv = document.getElementById("marksResult");
    const studentName = document.getElementById("studentName");

    if (!rollNumber) {
        alert("Please enter a student roll number.");
        return;
    }

    resultDiv.innerHTML = "Loading...";
    studentName.textContent = "";

    try {
        const response = await fetch(
            `/api/marks/${encodeURIComponent(rollNumber)}`
        );

        const data = await response.json();

        if (!response.ok) {
            resultDiv.textContent = data.error || "Failed to fetch marks.";
            return;
        }

        studentName.textContent = "Student: " + data.name;
        resultDiv.innerHTML = "";

        for (const semester in data.semesters) {
            const semesterHeading = document.createElement("h3");
            semesterHeading.textContent = "Semester " + semester;
            resultDiv.appendChild(semesterHeading);

            const table = document.createElement("table");
            table.border = "1";
            table.cellPadding = "8";
            table.style.width = "100%";
            table.style.borderCollapse = "collapse";
            table.style.marginBottom = "20px";

            table.innerHTML = `
                <thead>
                    <tr>
                        <th>Subject Code</th>
                        <th>Subject</th>
                        <th>Sessional 1</th>
                        <th>Sessional 2</th>
                        <th>Semester Exam</th>
                        <th>Actions</th>
                    </tr>
                </thead>
            `;

            const tbody = document.createElement("tbody");

            data.semesters[semester].forEach(mark => {
                const row = document.createElement("tr");

                row.innerHTML = `
                    <td>${mark.subcode}</td>
                    <td>${mark.subject}</td>
                    <td>${mark.sessional_1 ?? ""}</td>
                    <td>${mark.sessional_2 ?? ""}</td>
                    <td>${mark.semExam ?? ""}</td>
                    <td>
                        <button type="button"
                            onclick="editMark(${Number(mark.id)})">
                            Update
                        </button>
                        <button type="button"
                            onclick="deleteMark(${Number(mark.id)})">
                            Delete
                        </button>
                    </td>
                `;

                tbody.appendChild(row);
            });

            table.appendChild(tbody);
            resultDiv.appendChild(table);
        }

    } catch (error) {
        console.error(error);
        resultDiv.textContent = "Something went wrong while fetching marks.";
    }
}

function editMark(markId) {
    alert("Update feature will be added in the next step. Mark ID: " + markId);
}



async function deleteMark(markId) {
    if (!confirm("Are you sure you want to delete these marks?")) {
        return;
    }

    try {
        const response = await fetch(`/api/marks/delete/${markId}`, {
            method: "DELETE"
        });

        const result = await response.json();

        alert(result.message || "Request completed.");

        if (response.ok && result.success) {
            fetchStudentMarks();
        }

    } catch (error) {
        console.error(error);
        alert("Something went wrong while deleting marks.");
    }
}





async function editMark(markId) {
    const choice = prompt(
        "Which marks do you want to update?\n" +
        "1. Sessional 1\n" +
        "2. Sessional 2\n" +
        "3. Semester Exam"
    );

    if (choice === null) return;

    const fields = {
        "1": "sessional_1",
        "2": "sessional_2",
        "3": "semester_exam"
    };

    const field = fields[choice];

    if (!field) {
        alert("Invalid choice.");
        return;
    }

    const value = prompt("Enter the new marks:");

    if (value === null) return;

    if (value.trim() === "" || !Number.isFinite(Number(value)) || Number(value) < 0) {
        alert("Please enter valid, non-negative marks.");
        return;
    }

    try {
        const response = await fetch(`/api/marks/update/${markId}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ [field]: value })
        });

        const result = await response.json();

        alert(result.message || "Request completed.");

        if (response.ok && result.success) {
            fetchStudentMarks();
        }
    } catch (error) {
        console.error(error);
        alert("Something went wrong while updating marks.");
    }
}


async function saveUpdatedMarks(markId, marks) {
    try {
        const response = await fetch(`/api/marks/update/${markId}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(marks)
        });

        const result = await response.json();

        alert(result.message || "Request completed.");

        if (response.ok && result.success) {
            fetchStudentMarks();
        }
    } catch (error) {
        console.error(error);
        alert("Something went wrong while updating marks.");
    }
}



document.addEventListener('submit', async function (event) {
    if (event.target.id !== 'coordinatorForm') return;

    event.preventDefault();

    const form = event.target;
    const message = document.getElementById('coordinator-message');

    try {
        const response = await fetch('/admin/create-coordinator', {
            method: 'POST',
            body: new FormData(form)
        });

        const result = await response.json();

        message.textContent = result.message;
        message.style.color = result.success ? 'green' : 'red';

        if (result.success) {
            form.reset();
        }
    } catch (error) {
        message.textContent = 'Unable to contact the server.';
        message.style.color = 'red';
    }
});
