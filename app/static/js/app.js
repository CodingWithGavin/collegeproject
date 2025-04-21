


function submitRoomForm() {
    const playerName = document.getElementById("player-name").value;
    if (playerName.length > 0 && playerName.length <= 10) {
        // Create a form to submit to the backend (use Flask form submission as before)
        const form = document.createElement("form");
        form.method = "POST";
        form.action = "/create_room";  // Your Flask route for creating rooms

        const nameField = document.createElement("input");
        nameField.type = "hidden";
        nameField.name = "name";
        nameField.value = playerName;

        form.appendChild(nameField);
        document.body.appendChild(form);
        form.submit();
    } else {
        alert("Name must be between 1 and 10 characters.");
    }
}

