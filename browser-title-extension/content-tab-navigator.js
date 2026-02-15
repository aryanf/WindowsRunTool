// Function to open the navigator
function openNavigator() {
  // Remove any existing navigator first
  const existing = document.getElementById('custom-tab-navigator-overlay');
  if (existing) {
    existing.remove();
  }

  // Request tabs from background (fresh data each time)
  chrome.runtime.sendMessage({ action: 'getTabs' }, (response) => {
    // Check for errors (e.g., service worker not responding)
    if (chrome.runtime.lastError) {
      console.error('Failed to get tabs:', chrome.runtime.lastError);
      // Retry after a short delay to allow service worker to wake up
      setTimeout(() => {
        chrome.runtime.sendMessage({ action: 'getTabs' }, (retryResponse) => {
          if (chrome.runtime.lastError) {
            console.error('Retry failed:', chrome.runtime.lastError);
            return;
          }
          if (retryResponse && retryResponse.tabs) {
            createNavigatorUI(
              retryResponse.tabs, 
              retryResponse.timestamps || {}, 
              retryResponse.previousTabId,
              retryResponse.tabGroups || {},
              retryResponse.groupColors || {}
            );
          }
        });
      }, 200);
      return;
    }
    
    if (response && response.tabs) {
      createNavigatorUI(
        response.tabs, 
        response.timestamps || {}, 
        response.previousTabId,
        response.tabGroups || {},
        response.groupColors || {}
      );
    }
  });
}

// Listen for messages from background script to open tab navigator
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'openNavigator') {
    openNavigator();
  }
});

// Add keyboard listener to capture Alt+Down at the page level
// This ensures the extension captures it before the page can
// Using both capture and bubble phase for maximum coverage
const keydownHandler = (event) => {
  if (event.altKey && event.key === 'ArrowDown') {
    event.preventDefault();
    event.stopPropagation();
    event.stopImmediatePropagation();
    openNavigator();
    return false;
  }
};

// Add listener in capture phase (runs first)
document.addEventListener('keydown', keydownHandler, true);

// Also add to window for extra coverage
window.addEventListener('keydown', keydownHandler, true);

// Add listener at document level as well
if (document.documentElement) {
  document.documentElement.addEventListener('keydown', keydownHandler, true);
}
