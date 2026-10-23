async function getActiveTab() {
  try {
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tabs && tabs[0]) {
      console.log("Current tab:", tabs[0].url);
    }
  } catch (error) {
    console.error("Failed to query tabs:", error);
  }
}

// Call the function safely
getActiveTab();