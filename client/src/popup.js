// Runs every time the extension popup opens:
// read the active tab's URL, save it locally, then hand it to the backend.

const BACKEND_URL = "http://localhost:8000";

function showStatus(text) {
  const output = document.getElementById("output");
  if (output) output.textContent = text;
}

function getActiveTabUrl() {
  return chrome.tabs
    .query({ active: true, currentWindow: true })
    .then((tabs) => (tabs[0] ? tabs[0].url : undefined));
}

async function reportToBackend(url) {
  try {
    const response = await fetch(`${BACKEND_URL}/api/context`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });

    if (!response.ok) {
      const body = await response.json().catch(() => null);
      console.warn("Backend rejected the URL:", response.status, body?.detail ?? "");
    }
  } catch (error) {
    // Backend not running is not fatal: the URL is still saved locally.
    console.warn("Backend not reachable, URL saved locally only:", error);
  }
}

async function saveCurrentUrl() {
  try {
    const url = await getActiveTabUrl();

    if (!url) {
      showStatus("Could not read this tab's URL");
      return;
    }

    // "lastUrl" is the storage key you read back later.
    await chrome.storage.local.set({ lastUrl: url });

    showStatus(url);
    console.log("Saved URL:", url);

    await reportToBackend(url);
  } catch (error) {
    console.error("Failed to read or save the active tab URL:", error);
    showStatus("Could not read this tab's URL");
  }
}

document.addEventListener("DOMContentLoaded", saveCurrentUrl);
