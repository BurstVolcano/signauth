document.getElementById("uploadForm").addEventListener("submit", async function (event) {
    event.preventDefault();

    const genuineInput = document.getElementById("genuineFile");
    const forgedInput = document.getElementById("forgedFile");

    const genuineFile = genuineInput.files[0];
    const forgedFile = forgedInput.files[0];

    if (!genuineFile || !forgedFile) {
        alert("Please upload both genuine and forged signature files before submitting.");
        return;
    }

    const formData = new FormData();
    formData.append("genuineFile", genuineFile);
    formData.append("forgedFile", forgedFile);
    console.log("Sending files:", genuineFile.name, forgedFile.name);
    try {
        const response = await fetch("/compare", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error("Failed to upload the files.");
        }

        const result = await response.json();

        const resultDiv = document.getElementById("result");
        const resultText = document.getElementById("resultText");
        resultText.innerHTML = `
            <strong>Result:</strong> ${result.result}<br>
            <strong>Genuine Signature Probability:</strong> ${result.genuine_probability}<br>
            <strong>Forged Signature Probability:</strong> ${result.forged_probability}
        `;
        resultDiv.classList.remove("hidden");
    } catch (error) {
        alert("An error occurred: " + error.message);
    }
});