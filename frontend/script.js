const API_URL = window.__API_URL__ || "http://127.0.0.1:5000";

const startCameraBtn = document.getElementById("startCameraBtn");
const capturePhotoBtn = document.getElementById("capturePhotoBtn");
const fileInput = document.getElementById("fileInput");
const cameraView = document.getElementById("cameraView");
const capturedImage = document.getElementById("capturedImage");
const statusBox = document.getElementById("status");
const measurementResult = document.getElementById("measurementResult");
const chatMessages = document.getElementById("chatMessages");
const chatInput = document.getElementById("chatInput");
const sendChatBtn = document.getElementById("sendChatBtn");

let stream = null;

function setStatus(message, isError = false) {
  statusBox.textContent = message;
  statusBox.style.color = isError ? "#d94c4c" : "#5d6b7f";
}

function addChatMessage(text, isUser = false) {
  const div = document.createElement("div");
  div.className = `message ${isUser ? "user" : "bot"}`;
  div.textContent = text;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showMeasurementSummary(result) {
  if (!result || !result.measurements) {
    measurementResult.textContent = "No measurement yet.";
    measurementResult.classList.add("empty");
    return;
  }

  const details = result.measurements;
  const summary = `${result.summary}\n\nLength: ${details.length_cm} cm\nChest: ${details.chest_cm} cm\nShoulder: ${details.shoulder_cm} cm\nWaist: ${details.waist_cm} cm\nSleeve: ${details.sleeve_cm} cm`;
  measurementResult.textContent = summary;
  measurementResult.classList.remove("empty");
}

async function captureAndMeasure(imageDataUrl) {
  setStatus("Measuring…");

  try {
    const response = await fetch(`${API_URL}/measure`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image: imageDataUrl }),
    });

    const data = await response.json();
    if (!response.ok || !data.ok) {
      throw new Error(data.error || "Measurement failed.");
    }

    showMeasurementSummary(data.result);
    setStatus("Measurement complete.");
    addChatMessage(data.result.summary, false);
  } catch (error) {
    setStatus(error.message, true);
    addChatMessage(error.message, false);
  }
}

async function startCamera() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    cameraView.srcObject = stream;
    cameraView.style.display = "block";
    capturedImage.style.display = "none";
    setStatus("Camera is live. Capture the garment when it is centered.");
  } catch (error) {
    setStatus("Camera access failed. You can still upload an image.", true);
  }
}

function stopCamera() {
  if (stream) {
    stream.getTracks().forEach((track) => track.stop());
    stream = null;
  }
  if (cameraView.srcObject) {
    cameraView.srcObject = null;
  }
}

function captureFromCamera() {
  if (!cameraView.srcObject) {
    setStatus("Start the camera first.", true);
    return;
  }

  const canvas = document.getElementById("captureCanvas");
  const context = canvas.getContext("2d");
  canvas.width = cameraView.videoWidth || 640;
  canvas.height = cameraView.videoHeight || 480;
  context.drawImage(cameraView, 0, 0, canvas.width, canvas.height);
  const dataUrl = canvas.toDataURL("image/png");

  capturedImage.src = dataUrl;
  capturedImage.style.display = "block";
  cameraView.style.display = "none";

  captureAndMeasure(dataUrl);
}

fileInput.addEventListener("change", async (event) => {
  const [file] = event.target.files;
  if (!file) return;

  const reader = new FileReader();
  reader.onload = async () => {
    const dataUrl = reader.result;
    capturedImage.src = dataUrl;
    capturedImage.style.display = "block";
    cameraView.style.display = "none";
    stopCamera();
    await captureAndMeasure(dataUrl);
  };
  reader.readAsDataURL(file);
});

startCameraBtn.addEventListener("click", startCamera);
capturePhotoBtn.addEventListener("click", captureFromCamera);

sendChatBtn.addEventListener("click", async () => {
  const message = chatInput.value.trim();
  if (!message) return;

  addChatMessage(message, true);
  chatInput.value = "";

  try {
    const response = await fetch(`${API_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const data = await response.json();
    addChatMessage(data.reply || "I could not answer that yet.", false);
  } catch (error) {
    addChatMessage("The chatbot is unavailable right now.", false);
  }
});

chatInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    sendChatBtn.click();
  }
});
