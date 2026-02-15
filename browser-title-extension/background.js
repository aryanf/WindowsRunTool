// Track tab creation timestamps (persisted to survive service worker unloading)
let tabTimestamps = {};
let currentActiveTabId = null;
let previousTabId = null;
let isInitialized = false;

// Track tab groups (for AWS tabs)
let tabGroups = {}; // tabId -> groupId
let groupColors = {}; // groupId -> color
let nextGroupId = 1;
let tabOpeners = {}; // tabId -> openerTabId (for tabs created before URL is available)

// Function to check if a URL is an AWS root page that should start a new group
function isAwsRootPage(url) {
  if (!url || !url.includes('.console.aws.amazon.com')) return false;
  
  const urlObj = new URL(url);
  const pathname = urlObj.pathname;
  const hash = urlObj.hash;
  
  // Main AWS console home
  if (pathname.includes('/console/home') && hash === '#') {
    return true;
  }
  
  // Service home pages (ending with /home without further navigation)
  if (pathname.includes('/home') && (!hash || hash === '#')) {
    return true;
  }
  
  // SQS main queues list
  if (pathname.includes('/sqs/') && hash === '#/queues') {
    return true;
  }
  
  // CloudFormation stacks list (when filteringText or viewNested is present, it's a root list view)
  if (pathname.includes('/cloudformation/') && hash.includes('#/stacks') && 
      (hash.includes('filteringText=') || hash.includes('viewNested=') || hash === '#/stacks')) {
    return true;
  }
  
  // ECS home page
  if (pathname.includes('/ecs/') && pathname.includes('/home')) {
    return true;
  }
  
  return false;
}

// Generate a distinct color for a group
function generateGroupColor(groupId) {
  // Use a predefined set of maximally distinct, easily distinguishable colors
  const colors = [
    '#3498db', // Bright Blue
    '#e74c3c', // Bright Red
    '#2ecc71', // Bright Green
    '#f39c12', // Bright Orange
    '#9b59b6', // Purple
    '#1abc9c', // Cyan
    '#ff6b9d', // Pink
    '#f1c40f', // Yellow
    '#95e1d3', // Mint
    '#ff6348', // Coral
    '#00d2d3', // Turquoise
    '#786fa6', // Lavender
    '#f8b500', // Amber
    '#00b894', // Emerald
    '#fd79a8', // Hot Pink
  ];
  
  return colors[(groupId - 1) % colors.length];
}

// Function to ensure timestamps are loaded
async function ensureInitialized() {
  if (isInitialized) return;
  
  const result = await chrome.storage.session.get(['tabTimestamps', 'tabGroups', 'groupColors', 'nextGroupId']);
  if (result.tabTimestamps) {
    tabTimestamps = result.tabTimestamps;
  }
  if (result.tabGroups) {
    tabGroups = result.tabGroups;
  }
  if (result.groupColors) {
    groupColors = result.groupColors;
  }
  if (result.nextGroupId) {
    nextGroupId = result.nextGroupId;
  }
  
  // Initialize timestamps for existing tabs if not already set
  const tabs = await chrome.tabs.query({});
  const now = Date.now();
  let updated = false;
  tabs.forEach(tab => {
    if (tab.id && !tabTimestamps[tab.id]) {
      // Use tab ID as rough age estimate for existing tabs
      const minId = Math.min(...tabs.map(t => t.id));
      const maxId = Math.max(...tabs.map(t => t.id));
      const idRange = maxId - minId || 1;
      const normalizedAge = (tab.id - minId) / idRange;
      const estimatedAge = (1 - normalizedAge) * 7 * 24 * 60 * 60 * 1000;
      tabTimestamps[tab.id] = now - estimatedAge;
      updated = true;
    }
  });
  if (updated) {
    await chrome.storage.session.set({ tabTimestamps });
  }
  
  // Initialize groups for existing AWS tabs
  tabs.forEach(tab => {
    if (tab.url && tab.url.includes('.console.aws.amazon.com') && !tabGroups[tab.id]) {
      // Assign each existing AWS tab to its own group initially
      const groupId = nextGroupId++;
      tabGroups[tab.id] = groupId;
      groupColors[groupId] = generateGroupColor(groupId);
    }
  });
  await chrome.storage.session.set({ tabGroups, groupColors, nextGroupId });
  
  // Initialize current active tab
  const activeTabs = await chrome.tabs.query({ active: true, currentWindow: true });
  if (activeTabs.length > 0) {
    currentActiveTabId = activeTabs[0].id;
  }
  
  isInitialized = true;
}

// Initialize on startup
ensureInitialized();

// Set default zoom to 90% for new tabs only
chrome.tabs.onCreated.addListener(async (tab) => {
  if (tab.id) {
    chrome.tabs.setZoom(tab.id, 0.9);
    tabTimestamps[tab.id] = Date.now();
    
    // Store opener relationship for later use (URL might not be available yet)
    if (tab.openerTabId) {
      tabOpeners[tab.id] = tab.openerTabId;
    }
    
    // Handle AWS tab grouping (only if URL is available)
    if (tab.url && tab.url.includes('.console.aws.amazon.com')) {
      // Check if this is a root page (starts new group)
      if (isAwsRootPage(tab.url)) {
        // Create new group
        const groupId = nextGroupId++;
        tabGroups[tab.id] = groupId;
        groupColors[groupId] = generateGroupColor(groupId);
      } else if (tab.openerTabId && tabGroups[tab.openerTabId]) {
        // Inherit group from opener tab
        tabGroups[tab.id] = tabGroups[tab.openerTabId];
      } else {
        // New group for orphaned AWS tabs
        const groupId = nextGroupId++;
        tabGroups[tab.id] = groupId;
        groupColors[groupId] = generateGroupColor(groupId);
      }
      await chrome.storage.session.set({ tabGroups, groupColors, nextGroupId });
    }
    
    // Persist to storage
    chrome.storage.session.set({ tabTimestamps });
  }
});

// Track page loads and refreshes
chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete') {
    tabTimestamps[tabId] = Date.now();
    
    // Handle AWS tab group changes on navigation
    if (tab.url && tab.url.includes('.console.aws.amazon.com')) {
      // Check if navigated to a root page (should start new group)
      if (isAwsRootPage(tab.url)) {
        // Create new group for this tab
        const groupId = nextGroupId++;
        tabGroups[tabId] = groupId;
        groupColors[groupId] = generateGroupColor(groupId);
        await chrome.storage.session.set({ tabGroups, groupColors, nextGroupId });
      } else if (!tabGroups[tabId]) {
        // Tab doesn't have a group yet
        // Try multiple strategies to find a group to inherit:
        // 1. Check stored opener relationship
        let openerTabId = tabOpeners[tabId];
        if (openerTabId && tabGroups[openerTabId]) {
          // Inherit group from stored opener
          tabGroups[tabId] = tabGroups[openerTabId];
          delete tabOpeners[tabId]; // Clean up
          await chrome.storage.session.set({ tabGroups, groupColors, nextGroupId });
        } else {
          // 2. Fallback: use the previously active tab (which was likely the opener)
          if (previousTabId && tabGroups[previousTabId]) {
            tabGroups[tabId] = tabGroups[previousTabId];
            delete tabOpeners[tabId]; // Clean up
            await chrome.storage.session.set({ tabGroups, groupColors, nextGroupId });
          } else {
            // 3. Last resort: create new group
            const groupId = nextGroupId++;
            tabGroups[tabId] = groupId;
            groupColors[groupId] = generateGroupColor(groupId);
            await chrome.storage.session.set({ tabGroups, groupColors, nextGroupId });
          }
        }
      }
      // Otherwise, keep existing group assignment
    }
    
    // Persist to storage
    chrome.storage.session.set({ tabTimestamps });
  }
});

// Listen for tab activation to reopen navigator if needed
chrome.tabs.onActivated.addListener(async (activeInfo) => {
  // Store the old active tab as previous before updating
  if (currentActiveTabId && currentActiveTabId !== activeInfo.tabId) {
    previousTabId = currentActiveTabId;
  }
  currentActiveTabId = activeInfo.tabId;
  
  // Check if we should reopen the navigator
  const result = await chrome.storage.session.get(['reopenNavigator']);
  if (result.reopenNavigator) {
    // Clear the flag
    await chrome.storage.session.remove('reopenNavigator');
    
    // Wait a bit for the tab to be ready
    setTimeout(async () => {
      try {
        // Content scripts are always loaded, just send the message
        await chrome.tabs.sendMessage(activeInfo.tabId, { action: 'openNavigator' });
      } catch (error) {
        console.error('Failed to reopen navigator:', error);
      }
    }, 100);
  }
});

// Clean up timestamps and groups when tabs are closed
chrome.tabs.onRemoved.addListener(async (tabId) => {
  delete tabTimestamps[tabId];
  delete tabOpeners[tabId];
  
  // Clean up group assignment
  const groupId = tabGroups[tabId];
  delete tabGroups[tabId];
  
  // Check if this was the last tab in the group, if so clean up the group color
  if (groupId) {
    const groupStillUsed = Object.values(tabGroups).includes(groupId);
    if (!groupStillUsed) {
      delete groupColors[groupId];
    }
  }
  
  // Persist to storage
  chrome.storage.session.set({ tabTimestamps, tabGroups, groupColors });
});

// Listen for the keyboard command
chrome.commands.onCommand.addListener((command) => {
  if (command === "open-tab-navigator") {
    // Get the active tab
    chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
      if (tabs[0]) {
        const tab = tabs[0];
        
        // Check if we can inject into this tab (some pages like chrome:// are restricted)
        if (tab.url && (tab.url.startsWith('chrome://') || tab.url.startsWith('chrome-extension://') || tab.url.startsWith('edge://'))) {
          console.warn('Cannot inject into chrome:// or extension pages');
          return;
        }
        
        try {
          // Content scripts are always loaded, just send the message
          await chrome.tabs.sendMessage(tab.id, { action: 'openNavigator' });
        } catch (error) {
          console.error('Failed to open navigator (content script may not be ready yet):', error);
        }
      }
    });
  }
});

// Listen for messages from content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getTabs') {
    // Ensure we're initialized before responding
    ensureInitialized().then(() => {
      chrome.tabs.query({ currentWindow: true }, (tabs) => {
        sendResponse({ 
          tabs: tabs, 
          timestamps: tabTimestamps, 
          previousTabId: previousTabId,
          tabGroups: tabGroups,
          groupColors: groupColors
        });
      });
    });
    return true; // Keep the message channel open for async response
  } else if (request.action === 'switchTab') {
    chrome.tabs.update(request.tabId, { active: true });
    sendResponse({ success: true });
    return true;
  } else if (request.action === 'closeTab') {
    // Check if we should reopen navigator after closing
    if (request.shouldReopenNavigator) {
      chrome.storage.session.set({ reopenNavigator: true }, () => {
        chrome.tabs.remove(request.tabId, () => {
          sendResponse({ success: true });
        });
      });
    } else {
      chrome.tabs.remove(request.tabId, () => {
        sendResponse({ success: true });
      });
    }
    return true;
  } else if (request.action === 'moveTab') {
    chrome.tabs.move(request.tabId, { index: request.newIndex }, () => {
      sendResponse({ success: true });
    });
    return true;
  }
});
