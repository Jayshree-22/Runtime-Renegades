const fileInput = document.getElementById("fileInput");
const preview = document.getElementById("preview");
const uploadBtn = document.getElementById("uploadBtn");

// When file selected
fileInput.addEventListener("change", function () {
    const file = fileInput.files[0];

    if (file) {
        // Show preview
        preview.src = URL.createObjectURL(file);
        preview.style.display = "block";

        // Show upload button
        uploadBtn.style.display = "inline-block";
    }
});

async function uploadImage() {
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a file");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch("/upload", {
        method: "POST",
        body: formData
    });

    const data = await response.json();

    document.getElementById("result").innerText =
    "Uploaded: " + data.filename;
}