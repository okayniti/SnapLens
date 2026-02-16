/**
 * SnapLens — Chrome Extension Popup Logic
 *
 * Flow:
 * 1. User clicks "Capture Screenshot"
 * 2. chrome.tabs.captureVisibleTab() grabs the visible tab as a PNG data URL
 * 3. Convert data URL → Blob → File, send to FastAPI /upload
 * 4. Display AI analysis (category, title, summary, suggested action)
 * 5. User clicks "Save as Task/Note/Reminder/Expense" → POST /items
 *
 * Important Chrome Extension rules:
 * - No inline event handlers (CSP blocks them) → use addEventListener
 * - No inline scripts → all logic in this separate .js file
 * - activeTab permission → can only capture the tab the user is viewing
 */

const API_URL = "http://127.0.0.1:8000";
let lastResult = null;

// ── DOM References ────────────────────────────────────
const captureBtn = document.getElementById("capture-btn");
const captureSection = document.getElementById("capture-section");
const loadingSection = document.getElementById("loading-section");
const resultSection = document.getElementById("result-section");
const errorSection = document.getElementById("error-section");
const resetBtn = document.getElementById("reset-btn");
const errorResetBtn = document.getElementById("error-reset-btn");

// ── Event Listeners ───────────────────────────────────
// Chrome extensions don't allow onclick="..." in HTML (Content Security Policy)
// So we attach all events here in JavaScript

captureBtn.addEventListener("click", captureAndAnalyze);
resetBtn.addEventListener("click", resetView);
errorResetBtn.addEventListener("click", resetView);

// Save buttons — using data-category attribute
document.querySelectorAll(".btn-save").forEach(btn => {
    btn.addEventListener("click", () => {
        saveAs(btn.dataset.category);
    });
});


// ── Main Capture Flow ─────────────────────────────────
async function captureAndAnalyze() {
    showSection("loading");

    try {
        // Step 1: Capture the visible tab as a PNG image
        // This uses the activeTab permission — only works on the current tab
        const dataUrl = await chrome.tabs.captureVisibleTab(null, {
            format: "png",
            quality: 90
        });

        // Step 2: Convert data URL to a File object
        // The backend expects a file upload, not a base64 string
        const file = dataUrlToFile(dataUrl, "screenshot.png");

        // Step 3: Send to FastAPI /upload endpoint
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch(API_URL + "/upload", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || "Upload failed");
        }

        // Step 4: Display the AI analysis
        const data = await response.json();
        lastResult = data;
        displayResults(data);

    } catch (error) {
        showError(error.message);
    }
}


// ── Display AI Results ────────────────────────────────
function displayResults(data) {
    const intent = data.intent;

    // Set badge
    const badge = document.getElementById("result-badge");
    badge.textContent = intent.category;
    badge.className = "badge badge-" + intent.category;

    // Set content
    document.getElementById("result-title").textContent = intent.title;
    document.getElementById("result-summary").textContent = intent.summary;
    document.getElementById("result-action").textContent = "💡 " + intent.suggested_action;

    // Show key detail if available
    const detailRow = document.getElementById("result-detail-row");
    if (intent.key_detail) {
        document.getElementById("result-detail").textContent = intent.key_detail;
        detailRow.classList.remove("hidden");
    } else {
        detailRow.classList.add("hidden");
    }

    showSection("result");
}


// ── Save Item ─────────────────────────────────────────
async function saveAs(category) {
    if (!lastResult) return;

    const intent = lastResult.intent;
    try {
        const response = await fetch(API_URL + "/items", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                category: category,
                title: intent.title,
                summary: intent.summary,
                key_detail: intent.key_detail,
                extracted_text: lastResult.extracted_text,
                suggested_action: intent.suggested_action
            })
        });

        if (!response.ok) throw new Error("Save failed");

        showToast("✅ Saved as " + category + "!");
    } catch (error) {
        showToast("❌ " + error.message);
    }
}


// ── Helper: Data URL → File ───────────────────────────
// Chrome's captureVisibleTab returns a base64 data URL like:
// "data:image/png;base64,iVBORw0KGgo..."
// But our backend expects a file upload, so we convert it.
function dataUrlToFile(dataUrl, filename) {
    const [header, base64Data] = dataUrl.split(",");
    const mimeType = header.match(/:(.*?);/)[1];
    const binaryString = atob(base64Data);
    const bytes = new Uint8Array(binaryString.length);

    for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }

    const blob = new Blob([bytes], { type: mimeType });
    return new File([blob], filename, { type: mimeType });
}


// ── UI Helpers ────────────────────────────────────────
function showSection(name) {
    captureSection.classList.add("hidden");
    loadingSection.classList.add("hidden");
    resultSection.classList.add("hidden");
    errorSection.classList.add("hidden");

    if (name === "capture") captureSection.classList.remove("hidden");
    if (name === "loading") loadingSection.classList.remove("hidden");
    if (name === "result") resultSection.classList.remove("hidden");
    if (name === "error") errorSection.classList.remove("hidden");
}

function showError(message) {
    document.getElementById("error-text").textContent = message;
    showSection("error");
}

function showToast(message) {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.classList.remove("hidden");
    setTimeout(() => toast.classList.add("hidden"), 2000);
}

function resetView() {
    lastResult = null;
    showSection("capture");
}
