chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
  const url = tabs[0].url; 
  const boxElement = document.getElementById("output");
  
  // Inject HTML tags and text together
  boxElement.innerHTML = url;

});
