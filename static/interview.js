// Google Meet-Style Interview Room JavaScript

let localStream = null;
let videoElement = null;

// Initialize webcam
async function initializeWebcam() {
    try {
        const constraints = {
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: "user"
            },
            audio: false
        };

        localStream = await navigator.mediaDevices.getUserMedia(constraints);

        videoElement = document.getElementById("candidate-video");
        if (videoElement) {
            videoElement.srcObject = localStream;
            videoElement.play();

            const placeholder = document.getElementById("webcam-placeholder");
            if (placeholder) {
                placeholder.style.display = "none";
            }
        }

        console.log("Webcam initialized successfully");
        return true;
    } catch (error) {
        console.error("Error accessing webcam:", error);
        showWebcamError(error);
        return false;
    }
}

// Show error message
function showWebcamError(error) {
    const placeholder = document.getElementById("webcam-placeholder");
    if (placeholder) {
        let errorMessage = "Unable to access camera";

        if (error.name === "NotAllowedError") {
            errorMessage = "Camera access denied. Please allow camera permissions.";
        } else if (error.name === "NotFoundError") {
            errorMessage = "No camera found on this device.";
        } else if (error.name === "NotReadableError") {
            errorMessage = "Camera is already in use by another application.";
        }

        placeholder.innerHTML = "<svg xmlns=\"http://www.w3.org/2000/svg\" fill=\"none\" viewBox=\"0 0 24 24\" stroke=\"currentColor\"><path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z\" /><line x1=\"1\" y1=\"1\" x2=\"23\" y2=\"23\" stroke=\"currentColor\" stroke-width=\"2\"/></svg><p style=\"color: #ea4335; font-weight: 500;\">" + errorMessage + "</p><button onclick=\"initializeWebcam()\" style=\"margin-top: 12px; padding: 8px 16px; background: #8ab4f8; color: white; border: none; border-radius: 6px; cursor: pointer;\">Try Again</button>";
    }
}

// Toggle camera
function toggleCamera() {
    if (localStream) {
        const videoTrack = localStream.getVideoTracks()[0];
        if (videoTrack) {
            videoTrack.enabled = !videoTrack.enabled;

            const button = document.getElementById("camera-toggle");
            if (button) {
                button.classList.toggle("active", videoTrack.enabled);
                button.innerHTML = videoTrack.enabled ? "<span style=\"font-size: 24px;\">📹</span>" : "<span style=\"font-size: 24px;\">📹❌</span>";
            }

            if (videoElement) {
                videoElement.style.opacity = videoTrack.enabled ? "1" : "0";
            }
        }
    }
}

// Stop webcam
function stopWebcam() {
    if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
        localStream = null;

        if (videoElement) {
            videoElement.srcObject = null;
        }

        const placeholder = document.getElementById("webcam-placeholder");
        if (placeholder) {
            placeholder.style.display = "flex";
        }
    }
}

// Simulate speaking animation for AI
function simulateSpeaking(duration) {
    duration = duration || 3000;
    const aiContainer = document.querySelector(".ai-interviewer-container");
    if (aiContainer) {
        aiContainer.classList.add("speaking");
        setTimeout(function () {
            aiContainer.classList.remove("speaking");
        }, duration);
    }
}

// Initialize on page load
document.addEventListener("DOMContentLoaded", function () {
    console.log("Interview room JavaScript loaded");

    setTimeout(function () {
        initializeWebcam();
    }, 1000);
});

// Cleanup on page unload
window.addEventListener("beforeunload", function () {
    stopWebcam();
});
