// Bold patterns loaded from config for rendering in navigator
let _boldPatterns = null;

async function loadBoldPatterns() {
  if (_boldPatterns !== null) return _boldPatterns;
  try {
    const response = await fetch(chrome.runtime.getURL('bold-patterns.json'));
    const config = await response.json();
    _boldPatterns = config.boldPatterns || [];
  } catch (e) {
    console.error('Failed to load bold patterns:', e);
    _boldPatterns = [];
  }
  return _boldPatterns;
}

// Apply bold formatting to a title string based on configured patterns
// Returns an array of DOM nodes (text nodes and bold spans)
function applyBoldPatterns(titleText, patterns) {
  if (!titleText || !patterns || patterns.length === 0) {
    return [document.createTextNode(titleText || '')];
  }

  // Find the longest matching pattern
  let bestMatch = null;
  let bestMatchIndex = -1;

  for (const pattern of patterns) {
    const index = titleText.indexOf(pattern);
    if (index !== -1) {
      if (!bestMatch || pattern.length > bestMatch.length) {
        bestMatch = pattern;
        bestMatchIndex = index;
      }
    }
  }

  if (!bestMatch) {
    return [document.createTextNode(titleText)];
  }

  const fragments = [];
  if (bestMatchIndex > 0) {
    fragments.push(document.createTextNode(titleText.substring(0, bestMatchIndex)));
  }
  const boldSpan = document.createElement('span');
  boldSpan.style.fontWeight = '700';
  boldSpan.textContent = bestMatch;
  fragments.push(boldSpan);
  const afterIndex = bestMatchIndex + bestMatch.length;
  if (afterIndex < titleText.length) {
    fragments.push(document.createTextNode(titleText.substring(afterIndex)));
  }
  return fragments;
}

// Create and inject the tab navigator UI
async function createNavigatorUI(tabs, timestamps = {}, previousTabId = null, tabGroups = {}, groupColors = {}) {
  // Load bold patterns
  const boldPatterns = await loadBoldPatterns();
  // Check if navigator already exists and remove it
  const existingOverlay = document.getElementById('custom-tab-navigator-overlay');
  if (existingOverlay) {
    existingOverlay.remove();
  }
  
  // Create overlay
  const overlay = document.createElement('div');
  overlay.id = 'custom-tab-navigator-overlay';
  overlay.innerHTML = `
    <div class="tab-navigator-container">
      <div class="tab-navigator-header">
        <input type="text" id="tab-search-input" placeholder="Search tabs..." autofocus>
        <button id="close-navigator">✕</button>
      </div>
      <div class="tab-navigator-list" id="tab-list"></div>
      <div class="tab-navigator-footer">
        <span id="tab-count"></span>
        <span>↑↓ navigate • Shift+↑↓ reorder • → switch • ← close • Esc exit</span>
      </div>
    </div>
  `;

  // Add styles
  const style = document.createElement('style');
  style.textContent = `
    #custom-tab-navigator-overlay {
      all: initial;
      position: fixed !important;
      top: 0 !important;
      left: 0 !important;
      width: 100% !important;
      height: 100% !important;
      background: rgba(0, 0, 0, 0.7) !important;
      z-index: 2147483647 !important;
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
      margin: 0 !important;
      padding: 0 !important;
      box-sizing: border-box !important;
    }

    #custom-tab-navigator-overlay * {
      box-sizing: border-box !important;
      margin: 0 !important;
      padding: 0 !important;
    }

    .tab-navigator-container {
      background: #1e1e1e !important;
      border-radius: 8px !important;
      width: 1000px !important;
      max-width: calc(100vw - 80px) !important;
      max-height: calc(100vh - 80px) !important;
      display: flex !important;
      flex-direction: column !important;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
      margin: 0 auto !important;
      padding: 0 !important;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
      line-height: normal !important;
    }

    .tab-navigator-header {
      padding: 20px 24px !important;
      border-bottom: 1px solid #333333 !important;
      display: flex !important;
      gap: 12px !important;
      flex-shrink: 0 !important;
    }

    #tab-search-input {
      flex: 1 !important;
      padding: 12px 16px !important;
      border: 2px solid #333333 !important;
      border-radius: 6px !important;
      font-size: 15px !important;
      outline: none !important;
      transition: border-color 0.2s !important;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
      line-height: normal !important;
      background: #1e1e1e !important;
      color: #ffffff !important;
    }

    #tab-search-input:focus {
      border-color: #4285f4 !important;
    }

    #close-navigator {
      background: #2a2a2a !important;
      border: none !important;
      border-radius: 6px !important;
      width: 44px !important;
      height: 44px !important;
      font-size: 20px !important;
      cursor: pointer !important;
      color: #ffffff !important;
      transition: background 0.2s !important;
      flex-shrink: 0 !important;
      line-height: normal !important;
    }

    #close-navigator:hover {
      background: #3a3a3a !important;
    }

    .tab-navigator-list {
      overflow-y: auto !important;
      max-height: 700px !important;
      padding: 12px 16px !important;
      flex: 1 !important;
    }

    .tab-item {
      padding: 8px 16px !important;
      border-radius: 4px !important;
      cursor: pointer !important;
      display: flex !important;
      align-items: center !important;
      gap: 10px !important;
      margin-bottom: 2px !important;
      transition: background 0.15s !important;
      border: 2px solid transparent !important;
      list-style: none !important;
      line-height: normal !important;
      background: transparent !important;
    }

    .tab-item:hover {
      background: #2a2a2a !important;
    }

    .tab-item.selected {
      background: #1a3a5c !important;
      border-color: #4285f4 !important;
    }

    .tab-item.active-tab {
      background: #1a3a1a !important;
    }

    .tab-item.selected.active-tab {
      background: #2a5a2a !important;
      border-color: #4285f4 !important;
    }

    .tab-favicon {
      width: 20px !important;
      height: 20px !important;
      min-width: 20px !important;
      min-height: 20px !important;
      flex-shrink: 0 !important;
      display: block !important;
      object-fit: contain !important;
    }

    .tab-info {
      flex: 1 !important;
      overflow: hidden !important;
      line-height: normal !important;
    }

    .tab-title {
      font-size: 14px !important;
      font-weight: 500 !important;
      white-space: nowrap !important;
      overflow: hidden !important;
      text-overflow: ellipsis !important;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
      line-height: 1.4 !important;
    }

    .tab-item.active-tab .tab-title {
      /* Keep normal font-weight, only bold markers get 700 */
      font-weight: 400 !important;
    }

    .tab-url {
      display: none !important;
    }

    .tab-age-indicator {
      width: 12px !important;
      height: 12px !important;
      min-width: 12px !important;
      min-height: 12px !important;
      border-radius: 50% !important;
      flex-shrink: 0 !important;
      margin-left: 8px !important;
    }

    .tab-group-indicator {
      width: 12px !important;
      height: 12px !important;
      min-width: 12px !important;
      min-height: 12px !important;
      flex-shrink: 0 !important;
      margin-left: 8px !important;
    }

    .tab-navigator-footer {
      padding: 16px 24px !important;
      border-top: 1px solid #333333 !important;
      display: flex !important;
      justify-content: space-between !important;
      align-items: center !important;
      gap: 16px !important;
      font-size: 12px !important;
      color: #cccccc !important;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
      line-height: normal !important;
      flex-shrink: 0 !important;
    }

    #tab-count {
      font-weight: 500 !important;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
      padding: 4px 8px !important;
      background: #1e1e1e !important;
      border-radius: 4px !important;
      color: #cccccc !important;
    }
  `;

  document.head.appendChild(style);
  document.body.appendChild(overlay);

  // Populate tab list
  const tabList = document.getElementById('tab-list');
  const tabCount = document.getElementById('tab-count');
  // Start with previous tab selected (for quick switching), fallback to active tab
  let selectedIndex = previousTabId ? tabs.findIndex(tab => tab.id === previousTabId) : -1;
  if (selectedIndex === -1) {
    selectedIndex = tabs.findIndex(tab => tab.active);
  }
  let filteredTabs = [...tabs];
  let isClosed = false;
  
  // Calculate age indicator color based on actual time elapsed since creation/refresh
  // Returns RGB color: light green (fresh) -> light red (1 day) -> dark red (1 week)
  function getAgeColor(tabId) {
    const now = Date.now();
    const loadTime = timestamps[tabId] || now; // Default to now if no timestamp
    const ageInMs = now - loadTime;
    
    const oneDayMs = 24 * 60 * 60 * 1000; // 1 day in milliseconds
    const oneWeekMs = 7 * 24 * 60 * 60 * 1000; // 7 days in milliseconds
    
    if (ageInMs < oneDayMs) {
      // 0 to 1 day: gradient from light green to light red
      const dayRatio = ageInMs / oneDayMs;
      
      // Light green RGB: (144, 238, 144)
      // Light red RGB: (255, 204, 204)
      const r = Math.round(144 + (255 - 144) * dayRatio);
      const g = Math.round(238 + (204 - 238) * dayRatio);
      const b = Math.round(144 + (204 - 144) * dayRatio);
      
      return `rgb(${r}, ${g}, ${b})`;
    } else if (ageInMs < oneWeekMs) {
      // 1 day to 1 week: gradient from light red to dark red
      const daysSinceOneDay = (ageInMs - oneDayMs) / (oneWeekMs - oneDayMs);
      const ageRatio = Math.min(daysSinceOneDay, 1);
      
      // Color gradient: light red (#ffcccc) to dark red (#8b0000)
      const r = Math.round(255 - (255 - 139) * ageRatio);
      const g = Math.round(204 - 204 * ageRatio);
      const b = Math.round(204 - 204 * ageRatio);
      
      return `rgb(${r}, ${g}, ${b})`;
    } else {
      // 1 week or older: dark red
      return '#8b0000'; // Dark red
    }
  }
  
  // Format age for tooltip in day-hh:mm format
  function formatAge(tabId) {
    const now = Date.now();
    const loadTime = timestamps[tabId];
    if (!loadTime) return 'Age unknown';
    
    const ageInMs = now - loadTime;
    
    // Calculate days, hours, minutes
    const days = Math.floor(ageInMs / (24 * 60 * 60 * 1000));
    const hours = Math.floor((ageInMs % (24 * 60 * 60 * 1000)) / (60 * 60 * 1000));
    const minutes = Math.floor((ageInMs % (60 * 60 * 1000)) / (60 * 1000));
    const seconds = Math.floor((ageInMs % (60 * 1000)) / 1000);
    
    // Format as day-hh:mm:ss (added seconds to see updates)
    const hh = String(hours).padStart(2, '0');
    const mm = String(minutes).padStart(2, '0');
    const ss = String(seconds).padStart(2, '0');
    
    return `${days}-${hh}:${mm}:${ss}`;
  }

  function renderTabs() {
    if (isClosed || !tabList || !document.body.contains(overlay)) {
      return;
    }
    tabList.innerHTML = '';
    filteredTabs.forEach((tab, index) => {
      const tabItem = document.createElement('div');
      tabItem.className = 'tab-item';
      if (index === selectedIndex) tabItem.classList.add('selected');
      if (tab.active) tabItem.classList.add('active-tab');
      
      // Create favicon element with better error handling
      const favicon = document.createElement('img');
      favicon.className = 'tab-favicon';
      
      // Check if this is an AWS sign-in page and use local AWS icon
      const isAwsSignInPage = tab.url && (tab.url.includes('signin.aws.amazon.com') || 
                                           tab.url.includes('/oauth') ||
                                           tab.url.includes('oauth-flow-id'));
      
      // Check if this is a Jenkins page and use local icon
      const isJenkinsPage = tab.url && (tab.url.includes('jenkins') || tab.title.includes('[Jenkins]'));
      
      if (isAwsSignInPage) {
        // Use local AWS icon for sign-in pages
        favicon.src = chrome.runtime.getURL('icons/aws/aws.ico');
      } else if (isJenkinsPage) {
        // Use local Jenkins icon
        favicon.src = chrome.runtime.getURL('icons/jenkins/jenkins.png');
      } else if (tab.favIconUrl && tab.favIconUrl !== '') {
        favicon.src = 'data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 24 24%22><text y=%2220%22 font-size=%2220%22>.</text></svg>';
        // Use favIconUrl if available
        favicon.src = tab.favIconUrl;
        // Add error handler that sets default icon if loading fails
        favicon.onerror = function() {
          favicon.src = 'data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 24 24%22><text y=%2220%22 font-size=%2220%22>.</text></svg>';
        };
      } else {
        // No favicon URL, use default immediately
        favicon.src = 'data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 24 24%22><text y=%2220%22 font-size=%2220%22>.</text></svg>';
      }
      
      const tabInfo = document.createElement('div');
      tabInfo.className = 'tab-info';
      
      const tabTitle = document.createElement('div');
      tabTitle.className = 'tab-title';
      
      // Apply bold formatting from config patterns
      const titleText = tab.title || '';
      const fragments = applyBoldPatterns(titleText, boldPatterns);
      fragments.forEach(fragment => tabTitle.appendChild(fragment));
      // Apply age color to font
      tabTitle.style.color = getAgeColor(tab.id);
      
      tabInfo.appendChild(tabTitle);
      
      // Create age indicator
      const ageIndicator = document.createElement('div');
      ageIndicator.className = 'tab-age-indicator';
      ageIndicator.style.backgroundColor = getAgeColor(tab.id);
      ageIndicator.title = `Last loaded: ${formatAge(tab.id)}`;
      
      tabItem.appendChild(favicon);
      tabItem.appendChild(tabInfo);
      
      // Add group indicator if tab is in a group
      if (tabGroups[tab.id] && groupColors[tabGroups[tab.id]]) {
        const groupIndicator = document.createElement('div');
        groupIndicator.className = 'tab-group-indicator';
        groupIndicator.style.backgroundColor = groupColors[tabGroups[tab.id]];
        groupIndicator.title = `Group ${tabGroups[tab.id]}`;
        tabItem.appendChild(groupIndicator);
      }
      
      tabItem.appendChild(ageIndicator);

      tabItem.addEventListener('click', () => {
        switchToTab(tab.id);
      });

      tabList.appendChild(tabItem);
    });

    tabCount.textContent = `${filteredTabs.length} tab${filteredTabs.length !== 1 ? 's' : ''}`;
  }

  function switchToTab(tabId) {
    chrome.runtime.sendMessage({ action: 'switchTab', tabId: tabId }, () => {
      closeNavigator();
    });
  }

  function handleVisibilityChange() {
    if (document.hidden) {
      closeNavigator();
    }
  }

  function closeNavigator() {
    if (isClosed) {
      return;
    }
    isClosed = true;
    overlay.remove();
    style.remove();
    // Remove event listeners
    window.removeEventListener('blur', closeNavigator);
    document.removeEventListener('visibilitychange', handleVisibilityChange);
  }

  function updateSelection(newIndex) {
    if (filteredTabs.length === 0) {
      return;
    }
    
    // Wrap around: if going past last, go to first; if going before first, go to last
    if (newIndex >= filteredTabs.length) {
      newIndex = 0;
    } else if (newIndex < 0) {
      newIndex = filteredTabs.length - 1;
    }
    
    selectedIndex = newIndex;
    renderTabs();
    
    // Scroll selected item into view
    const items = tabList.querySelectorAll('.tab-item');
    if (items[selectedIndex]) {
      items[selectedIndex].scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }
  }

  // Search functionality
  const searchInput = document.getElementById('tab-search-input');
  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase().trim();
    if (!query) {
      filteredTabs = [...tabs];
    } else {
      // Split by spaces to create multiple search terms (AND operation)
      const searchTerms = query.split(/\s+/).filter(term => term.length > 0);
      filteredTabs = tabs.filter(tab => {
        const tabText = (tab.title + ' ' + tab.url).toLowerCase();
        // All search terms must be present (AND operation)
        return searchTerms.every(term => tabText.includes(term));
      });
    }
    selectedIndex = 0;
    renderTabs();
  });

  // Ensure search input is focused
  searchInput.focus();

  // Keyboard navigation
  document.addEventListener('keydown', function keyHandler(e) {
    // Navigation keys should work even when input is focused
    const isNavigationKey = ['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'Enter', 'Escape'].includes(e.key);
    
    if (isNavigationKey) {
      // For navigation keys, prevent default and handle navigation
      e.preventDefault();
      e.stopPropagation();
      
      if (e.key === 'Escape') {
        closeNavigator();
        document.removeEventListener('keydown', keyHandler);
      } else if (e.key === 'ArrowDown') {
        // Shift+ArrowDown: Move tab down in order
        if (e.shiftKey && filteredTabs.length > 0 && selectedIndex < filteredTabs.length - 1) {
          const currentTab = filteredTabs[selectedIndex];
          const currentTabOriginalIndex = tabs.findIndex(t => t.id === currentTab.id);
          const nextTab = filteredTabs[selectedIndex + 1];
          const nextTabOriginalIndex = tabs.findIndex(t => t.id === nextTab.id);
          
          // Move the tab in Chrome
          chrome.runtime.sendMessage({ 
            action: 'moveTab', 
            tabId: currentTab.id, 
            newIndex: nextTabOriginalIndex 
          }, () => {
            // Swap in both arrays
            [filteredTabs[selectedIndex], filteredTabs[selectedIndex + 1]] = [filteredTabs[selectedIndex + 1], filteredTabs[selectedIndex]];
            [tabs[currentTabOriginalIndex], tabs[nextTabOriginalIndex]] = [tabs[nextTabOriginalIndex], tabs[currentTabOriginalIndex]];
            
            // Move selection down with the tab
            selectedIndex++;
            renderTabs();
            
            // Scroll selected item into view
            const items = tabList.querySelectorAll('.tab-item');
            if (items[selectedIndex]) {
              items[selectedIndex].scrollIntoView({ block: 'nearest', behavior: 'smooth' });
            }
          });
        } else {
          // Normal navigation
          updateSelection(selectedIndex + 1);
        }
      } else if (e.key === 'ArrowUp') {
        // Shift+ArrowUp: Move tab up in order
        if (e.shiftKey && filteredTabs.length > 0 && selectedIndex > 0) {
          const currentTab = filteredTabs[selectedIndex];
          const currentTabOriginalIndex = tabs.findIndex(t => t.id === currentTab.id);
          const prevTab = filteredTabs[selectedIndex - 1];
          const prevTabOriginalIndex = tabs.findIndex(t => t.id === prevTab.id);
          
          // Move the tab in Chrome
          chrome.runtime.sendMessage({ 
            action: 'moveTab', 
            tabId: currentTab.id, 
            newIndex: prevTabOriginalIndex 
          }, () => {
            // Swap in both arrays
            [filteredTabs[selectedIndex - 1], filteredTabs[selectedIndex]] = [filteredTabs[selectedIndex], filteredTabs[selectedIndex - 1]];
            [tabs[prevTabOriginalIndex], tabs[currentTabOriginalIndex]] = [tabs[currentTabOriginalIndex], tabs[prevTabOriginalIndex]];
            
            // Move selection up with the tab
            selectedIndex--;
            renderTabs();
            
            // Scroll selected item into view
            const items = tabList.querySelectorAll('.tab-item');
            if (items[selectedIndex]) {
              items[selectedIndex].scrollIntoView({ block: 'nearest', behavior: 'smooth' });
            }
          });
        } else {
          // Normal navigation
          updateSelection(selectedIndex - 1);
        }
      } else if (e.key === 'ArrowRight' || e.key === 'Enter') {
        if (filteredTabs[selectedIndex]) {
          switchToTab(filteredTabs[selectedIndex].id);
        }
        document.removeEventListener('keydown', keyHandler);
      } else if (e.key === 'ArrowLeft') {
        if (filteredTabs[selectedIndex]) {
          const tabToClose = filteredTabs[selectedIndex];
          const wasActiveTab = tabToClose.active; // Check if closing the current active tab
          
          // Send to background to handle the close operation
          chrome.runtime.sendMessage({ 
            action: 'closeTab', 
            tabId: tabToClose.id,
            shouldReopenNavigator: wasActiveTab 
          }, () => {
            // Remove from both arrays
            const originalIndex = tabs.findIndex(t => t.id === tabToClose.id);
            if (originalIndex !== -1) {
              tabs.splice(originalIndex, 1);
            }
            filteredTabs.splice(selectedIndex, 1);
            
            // Adjust selection
            if (filteredTabs.length === 0) {
              closeNavigator();
              document.removeEventListener('keydown', keyHandler);
            } else {
              if (selectedIndex >= filteredTabs.length) {
                selectedIndex = filteredTabs.length - 1;
              }
              renderTabs();
            }
          });
        }
      }
    } else {
      // For typing keys, ensure the search input is focused
      if (document.activeElement !== searchInput) {
        searchInput.focus();
      }
    }
  }, true);

  // Close button
  document.getElementById('close-navigator').addEventListener('click', closeNavigator);

  // Close when clicking overlay
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) {
      closeNavigator();
    }
  });

  // Close navigator when window loses focus or tab is switched
  window.addEventListener('blur', closeNavigator);
  document.addEventListener('visibilitychange', handleVisibilityChange);

  // Initial render
  renderTabs();
}

// Expose function globally so background script can call it
window.createNavigatorUI = createNavigatorUI;
