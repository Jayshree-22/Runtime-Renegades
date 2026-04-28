const fileInput = document.getElementById("fileInput");
const preview = document.getElementById("preview");
const result = document.getElementById("result");

fileInput.addEventListener("change", async function () {
    const file = fileInput.files[0];
    if (!file) return;

    // preview selected image
    preview.src = URL.createObjectURL(file);
    preview.style.display = "block";

    const formData = new FormData();
    formData.append("file", file);

    result.innerHTML = "<p>Uploading...</p>";

    try {
        const res = await fetch("/upload?t=" + Date.now(), {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        if (data.error) {
            result.innerHTML = `<p style="color:red;">${data.error}</p>`;
            return;
        }

        result.innerHTML = "<h3>Result</h3>";

        if (data.status === "no_data") {
            result.innerHTML += `<p>${data.message}</p>`;
        } else {
            result.innerHTML += `
                <div style="
                    margin:12px;
                    padding:15px;
                    border-radius:10px;
                    background:#f9f9f9;
                    text-align:center;
                ">
                    <img src="/uploads/${data.match.filename}?t=${Date.now()}" 
                         style="
                            width:180px;
                            height:180px;
                            object-fit:cover;
                            border-radius:10px;
                            border:1px solid #ddd;
                         "
                         onerror="this.src='/static/logo.jpg'"><br><br>

                    <strong>${data.message}</strong><br>
                    Score: ${data.match.score.toFixed(2)}
                </div>
            `;
        }

    } catch (err) {
        console.error(err);
        result.innerHTML = "<p style='color:red;'>Upload failed</p>";
    }
});
