
const fileInput = document.getElementById("fileInput");
const preview = document.getElementById("preview");
const uploadBtn = document.getElementById("uploadBtn");
const result = document.getElementById("result");

console.log("JS LOADED ✅");

// Show preview + button
fileInput.addEventListener("change", function () {
    const file = fileInput.files[0];

    if (file) {
        preview.src = URL.createObjectURL(file);
        preview.style.display = "block";
        uploadBtn.style.display = "inline-block";
        result.innerText = "";
    }
});

// ✅ Attach button click properly
uploadBtn.addEventListener("click", uploadImage);

// Upload function
async function uploadImage() {
    console.log("UPLOAD FUNCTION CALLED 🚀");

    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a file");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        console.log(data);

        if (data.error) {
            result.innerText = "❌ " + data.error;
        } 
        else if (data.message && data.message.includes("Duplicate")) {
            result.innerText =
                "⚠️ Duplicate Image Detected\n" +
                "Matched with: " + data.matched_with + "\n" +
                "Difference: " + data.difference;
        } 
        else {
            result.innerText =
                "✅ No Duplicate Found\n" +
                "File: " + data.filename + "\n" +
                "Hash: " + data.phash;
        }

    } catch (err) {
        console.error(err);
        result.innerText = "❌ Duplicate Image Detected";
    }
}
