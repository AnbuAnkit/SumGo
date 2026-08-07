chrome.action.onClicked.addListener(async (tab) => {
  // 1. Get the active tab data safely
  if (tab.url) {
    console.log("Captured URL:", tab.url);

    try {
      // 2. Send the URL to your local AI agent server or API
      const response = await fetch("http://localhost:5000/agent/endpoint", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ currentUrl: tab.url, title: tab.title })
      });
      
      console.log("Successfully sent to agent:", await response.text());
    } catch (error) {
      console.error("Could not connect to agent server:", error);
    }
  }
});
