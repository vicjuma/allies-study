document.getElementById("myForm").addEventListener("submit", function (event) {
    event.preventDefault();
  
    var field1Value = document.getElementById("field1").value;
    var field2Value = document.getElementById("field2").value;
  
    // Check if values exist in the backend
    fetch("backend_url", {
      method: "POST",
      body: JSON.stringify({ field1: field1Value, field2: field2Value }),
      headers: {
        "Content-Type": "application/json"
      }
    })
      .then(function (response) {
        if (!response.ok) {
          throw new Error("Error occurred in the backend.");
        }
        return response.json();
      })
      .then(function (data) {
        // Check the response from the backend
        if (data.field1Exists) {
          showError("Field 1 already exists.");
        } else if (data.field2Exists) {
          showError("Field 2 already exists.");
        } else {
          // Submit the form if values don't exist
          document.getElementById("myForm").submit();
        }
      })
      .catch(function (error) {
        showError("Error occurred: " + error.message);
      });
  });
  
function showError(message) {
    // Display error message to the user
    var errorElement = document.createElement("div");
    errorElement.classList.add("error");
    errorElement.textContent = message;
    document.body.appendChild(errorElement);
}
