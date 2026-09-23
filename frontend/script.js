const API_URL = "http://127.0.0.1:8000";

const vehicleImage = document.getElementById("vehicleImage");
const imagePreview = document.getElementById("imagePreview");
const question = document.getElementById("question");
const inspectButton = document.getElementById("inspectButton");

const resultSection = document.getElementById("resultSection");
const detectedPart = document.getElementById("detectedPart");
const confidenceValue = document.getElementById("confidenceValue");
const confidenceBar = document.getElementById("confidenceBar");
const answerText = document.getElementById("answerText");
const sourcesList = document.getElementById("sourcesList");


// =========================
// IMAGE PREVIEW
// =========================

vehicleImage.addEventListener("change", () => {

    const file = vehicleImage.files[0];

    if (!file) {
        imagePreview.innerHTML = "";
        return;
    }

    const reader = new FileReader();

    reader.onload = (event) => {

        imagePreview.innerHTML = `
            <img
                src="${event.target.result}"
                alt="Selected vehicle image"
            >
        `;
    };

    reader.readAsDataURL(file);
});


// =========================
// INSPECT VEHICLE
// =========================

inspectButton.addEventListener("click", async () => {

    const file = vehicleImage.files[0];
    const userQuestion = question.value.trim();

    if (!file) {
        alert("Please upload a vehicle image first.");
        return;
    }

    if (!userQuestion) {
        alert("Please enter your maintenance question.");
        return;
    }


    // Show loading state

    inspectButton.disabled = true;

    inspectButton.innerHTML = `
        <span>
            <i class="fa-solid fa-spinner fa-spin"></i>
            Analyzing Vehicle...
        </span>

        <i class="fa-solid fa-gear fa-spin"></i>
    `;


    resultSection.classList.remove("hidden");

    detectedPart.textContent = "Scanning...";
    confidenceValue.textContent = "—";
    confidenceBar.style.width = "0%";

    answerText.textContent =
        "CarCare AI is analyzing the image and searching the maintenance knowledge base...";

    sourcesList.innerHTML = "Loading sources...";


    try {

        const formData = new FormData();

        formData.append("image", file);
        formData.append("question", userQuestion);


        const response = await fetch(
            `${API_URL}/ask-with-image`,
            {
                method: "POST",
                body: formData
            }
        );


        if (!response.ok) {

            throw new Error(
                `Server returned ${response.status}`
            );
        }


        const data = await response.json();


        // =========================
        // DETECTED PART
        // =========================

        if (data.part) {

            detectedPart.textContent = data.part;

        } else {

            detectedPart.textContent = "No part detected";
        }


        // =========================
        // CONFIDENCE
        // =========================

        if (data.confidence !== undefined) {

            const confidencePercent =
                Math.round(data.confidence * 100);

            confidenceValue.textContent =
                `${confidencePercent}%`;

            confidenceBar.style.width =
                `${confidencePercent}%`;

        } else {

            confidenceValue.textContent = "—";
            confidenceBar.style.width = "0%";
        }


        // =========================
        // AI ANSWER
        // =========================

        answerText.textContent =
            data.answer || "No answer was generated.";


        // =========================
        // SOURCES
        // =========================

        sourcesList.innerHTML = "";

        if (
            data.sources &&
            data.sources.length > 0
        ) {

            data.sources.forEach((source) => {

                const sourceElement =
                    document.createElement("div");

                sourceElement.className =
                    "source-item";

                sourceElement.textContent =
                    `PDF Page ${source.page}`;

                sourcesList.appendChild(
                    sourceElement
                );
            });

        } else {

            sourcesList.textContent =
                "No specific sources were available.";
        }


        // Scroll to result

        resultSection.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    }

    catch (error) {

        console.error(error);

        answerText.textContent =
            "Unable to connect to CarCare AI. Please make sure the FastAPI server is running.";

        detectedPart.textContent =
            "Connection Error";

        confidenceValue.textContent =
            "—";

        confidenceBar.style.width =
            "0%";

        sourcesList.textContent =
            "No sources available.";
    }


    // Restore button

    inspectButton.disabled = false;

    inspectButton.innerHTML = `
        <span>
            <i class="fa-solid fa-magnifying-glass-chart"></i>
            Inspect Vehicle
        </span>

        <i class="fa-solid fa-arrow-right"></i>
    `;

});