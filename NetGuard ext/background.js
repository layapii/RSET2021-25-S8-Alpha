const CONFIG = {
  debug: true,                  // Enable debug logging
  checkTimeout: 5000,           // 5 seconds max per URL check
  decisionExpiry: 24 * 60 * 60 * 1000, // 24 hour block duration
  maxBlockedSites: 100,         // Maximum sites to block
  warningCooldown: 10 * 1000 // 30 minutes between warnings
};

// Safe Domains Whitelist
const SAFE_DOMAINS = [
  'google.com',
  'microsoft.com',
  'apple.com',
  'rajagiritech.ac.in',
  'localhost',
  '.org',
  '.in',
  '.ac.in'
];

// Threat Detection Patterns
const THREAT_PATTERNS = [
  /phishing|fake|scam|login\.php/i,
  /([a-z0-9]+\.){3,}[a-z]{2,}/,      // Excessive subdomains
  /https?:\/\/(?!www\.)\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/, // IP addresses
  /\.exe(\?|$)/i,                    // Executable files
  /\.zip(\?|$)/i,                    // Archive files
  /[^\w\-.]\d{10,}[^\w\-.]/,      // Long number sequences
  /https?:\/\/[^\/]+\/login[^\/]*$/i // Login pages
];

// Storage for user decisions
const userDecisions = new Map();

// Debug logging function
function debug(message, data = null) {
  if (CONFIG.debug) {
      const timestamp = new Date().toISOString();
      console.log(`[${timestamp}] NetGuard: ${message}`, data || '');
      chrome.action.setBadgeText({ text: '!' });
      chrome.action.setBadgeBackgroundColor({ color: '#EA4335' });
  }
}

// Enhanced URL validation
function isValidUrl(url) {
  try {
      const parsed = new URL(url);
      const allowedProtocols = ['http:', 'https:'];
      if (!allowedProtocols.includes(parsed.protocol)) return false;
      
      // Block common dangerous file extensions
      const dangerousExtensions = ['.exe', '.zip', '.rar', '.js', '.jar'];
      const pathname = parsed.pathname.toLowerCase();
      if (dangerousExtensions.some(ext => pathname.endsWith(ext))) {
          return false;
      }
      
      return true;
  } catch (e) {
      return false;
  }
}

// Check URL against threat databases
async function checkUrl(url) {
  if (!isValidUrl(url)) {
      debug("Invalid URL format", url);
      return { isMalicious: false };
  }

  const domain = new URL(url).hostname;

  // Check against whitelist
  if (SAFE_DOMAINS.some(safeDomain => domain.endsWith(safeDomain))) {
      debug("Domain is whitelisted", domain);
      return { isMalicious: false };
  }

  // Check local threat patterns
  for (const pattern of THREAT_PATTERNS) {
      if (pattern.test(url)) {
          debug("Local threat pattern matched", {
              url: url,
              pattern: pattern.toString()
          });
          return {
              isMalicious: true,
              source: "Local Pattern Detection",
              details: {
                  threat: "Matches known threat pattern",
                  pattern: pattern.toString(),
                  confidence: "high"
              }
          };
      }
  }

  // Check URLhaus API
  try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), CONFIG.checkTimeout);

      const response = await fetch("https://urlhaus-api.abuse.ch/v1/url/", {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: `url=${encodeURIComponent(url)}`,
          signal: controller.signal
      });

      clearTimeout(timeout);

      if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      if (data.query_status === "ok" && data.threat) {
          debug("URLhaus detected", data);
          return {
              isMalicious: true,
              source: "URLhaus Database",
              details: {
                  threat: data.threat,
                  tags: data.tags || [],
                  urlhaus_reference: data.urlhaus_reference,
                  date_added: data.date_added,
                  confidence: data.threat === "malware_download" ? "critical" : "high"
              }
          };
      }
  } catch (error) {
      debug("URLhaus API check failed", error.message);
  }
  return { isMalicious: false };
}

// Session management functions
async function getSessionData(tabId) {
  const result = await chrome.storage.session.get(`phish_${tabId}`);
  return result[`phish_${tabId}`] || null;
}

async function setSessionData(tabId, data) {
  await chrome.storage.session.set({
      [`phish_${tabId}`]: {
          ...data,
          timestamp: Date.now()
      }
  });
}

async function clearSessionData(tabId) {
  await chrome.storage.session.remove(`phish_${tabId}`);
}

// Warning history functions
async function getWarningHistory(url) {
  const result = await chrome.storage.session.get(`warning_${url}`);
  return result[`warning_${url}`] || null;
}

async function setWarningHistory(url) {
  await chrome.storage.session.set({
      [`warning_${url}`]: { 
          timestamp: Date.now(),
          count: ((await getWarningHistory(url))?.count || 0) + 1
      }
  });
}

async function clearWarningHistory(url) {
  await chrome.storage.session.remove(`warning_${url}`);
}

// Handle navigation events
async function handleNavigation(details) {
  const { url, tabId } = details;
  debug("Handling navigation", { url, tabId, frameId: details.frameId });
  
  const dangerousExtensions = ['.exe', '.zip', '.rar', '.js', '.jar'];
    const pathname = new URL(url).pathname.toLowerCase();
    if (dangerousExtensions.some(ext => pathname.endsWith(ext))) {
        console.log("Blocking dangerous file:", url); // Debug log
        await chrome.tabs.update(tabId, {
            url: chrome.runtime.getURL(`blocked.html?url=${encodeURIComponent(url)}`)
        });
        return; // Stop further execution
    }

  if (details.frameId !== 0 || !isValidUrl(url)) {
      return;
  }

  const blockDecision = userDecisions.get(url);
  if (blockDecision?.action === 'block' && 
      Date.now() - blockDecision.timestamp < CONFIG.decisionExpiry) {
      debug("URL is blocked", url);
      await chrome.tabs.update(tabId, {
          url: chrome.runtime.getURL(`blocked.html?url=${encodeURIComponent(url)}`)
      });
      return;
  }

  const isContinuing = await chrome.storage.session.get(`continuing_${tabId}`);
  if (isContinuing[`continuing_${tabId}`]) {
      await chrome.storage.session.remove(`continuing_${tabId}`);
      debug("Skipping recently continued URL", url);
      return;
  }

  const warningHistory = await getWarningHistory(url);
  if (warningHistory && (Date.now() - warningHistory.timestamp < CONFIG.warningCooldown)) {
      debug("Within warning cooldown period", { url, lastWarning: warningHistory.timestamp });
      return;
  }

  try {
      const result = await checkUrl(url);
      
      if (result.isMalicious) {
          debug("Showing warning for malicious URL", {
              url,
              source: result.source,
              details: result.details
          });

          await setSessionData(tabId, {
              url,
              source: result.source,
              details: result.details
          });

          await setWarningHistory(url);

          await chrome.tabs.update(tabId, {
              url: chrome.runtime.getURL(
                  `warning.html?url=${encodeURIComponent(url)}` +
                  `&tabId=${tabId}` +
                  `&source=${encodeURIComponent(result.source)}` +
                  `&details=${encodeURIComponent(JSON.stringify(result.details))}`
              )
          });
      }
  } catch (error) {
      debug("Navigation handling error", error);
  }
}

// Connection handler for blocked sites list
chrome.runtime.onConnect.addListener((port) => {
  if (port.name === "blockedSitesQuery") {
      debug("Popup connected for blocked sites query");
      
      port.onMessage.addListener(async (request) => {
          if (request.action === "getBlockedSites") {
              try {
                  const allItems = await chrome.storage.local.get(null);
                  const blockedSites = [];
                  
                  for (const [key, value] of Object.entries(allItems)) {
                      if (key.startsWith('blocked_')) {
                          const url = value.normalizedUrl || key.replace('blocked_', '');
                          blockedSites.push({
                              url: url,
                              timestamp: value.timestamp,
                              source: value.source,
                              details: value.details
                          });
                      }
                  }
                  
                  blockedSites.sort((a, b) => b.timestamp - a.timestamp);
                  port.postMessage({ blockedSites });
                  debug("Sent blocked sites to popup", { count: blockedSites.length });
              } catch (error) {
                  debug("Error getting blocked sites", error);
                  port.postMessage({ error: error.message });
              }
          }
      });

      port.onDisconnect.addListener(() => {
          debug("Popup disconnected");
      });
  }

  // New connection handler for unblock operations
  if (port.name === "unblockSite") {
      debug("Unblock operation connection established");
      
      port.onMessage.addListener(async (request) => {
          if (request.action === "unblockSite") {
              try {
                  const url = request.url;
                  debug("Processing unblock request", { url });

                  // Normalize URL
                  let normalizedUrl = url;
                  try {
                      const urlObj = new URL(url);
                      normalizedUrl = urlObj.href.toLowerCase();
                  } catch (e) {
                      debug("URL normalization failed for unblock", url);
                  }

                  debug("Removing blocked entries for:", {
                      original: `blocked_${url}`,
                      normalized: `blocked_${normalizedUrl}`
                  });

                  // Remove from both possible storage keys
                  userDecisions.delete(url);
                  await chrome.storage.local.remove(`blocked_${url}`);
                  await chrome.storage.local.remove(`blocked_${normalizedUrl}`);
                  
                  debug("Unblock successful", { url });
                  port.postMessage({ success: true });
              } catch (error) {
                  debug("Unblock error", error);
                  port.postMessage({ 
                      success: false, 
                      error: error.message 
                  });
              } finally {
                  port.disconnect();
              }
          }
      });

      port.onDisconnect.addListener(() => {
          debug("Unblock operation connection closed");
      });
  }
});

// Handle user decisions (original message-based handler remains for other operations)
async function handleUserDecision(request, sender, sendResponse) {
  try {
      if (request.action === "phishDecision") {
          debug("Processing user decision", {
              decision: request.decision,
              url: request.url,
              tabId: sender.tab?.id
          });

          userDecisions.set(request.url, {
              action: request.decision,
              timestamp: Date.now(),
              source: request.source || 'user'
          });

          if (request.decision === "block") {
              // Normalize URL before storage
              let normalizedUrl = request.url;
              try {
                  const urlObj = new URL(request.url);
                  normalizedUrl = urlObj.href.toLowerCase();
              } catch (e) {
                  debug("URL normalization failed, using original", request.url);
              }

              const storageKey = `blocked_${normalizedUrl}`;
              
              await chrome.storage.local.set({
                  [storageKey]: {
                      action: 'block',
                      timestamp: Date.now(),
                      source: request.source || 'user',
                      details: request.details,
                      normalizedUrl: normalizedUrl
                  }
              });

              await clearWarningHistory(request.url);

              if (sender.tab?.id) {
                  await chrome.tabs.update(sender.tab.id, {
                      url: chrome.runtime.getURL(`blocked.html?url=${encodeURIComponent(request.url)}`)
                  });
              }

              await enforceBlockedSitesLimit();
          } 
          else if (request.decision === "continue") {
              if (sender.tab?.id) {
                  await chrome.storage.session.set({
                      [`continuing_${sender.tab.id}`]: true
                  });
                  await chrome.tabs.update(sender.tab.id, { url: request.url });
              }
          }

          sendResponse({ success: true });
          return true;
      }

      // Keep this for backward compatibility
      if (request.action === "unblockSite") {
          debug("Processing legacy unblock request", request.url);
          
          let normalizedUrl = request.url;
          try {
              const urlObj = new URL(request.url);
              normalizedUrl = urlObj.href.toLowerCase();
          } catch (e) {
              debug("URL normalization failed for unblock", request.url);
          }

          userDecisions.delete(request.url);
          await chrome.storage.local.remove(`blocked_${request.url}`);
          await chrome.storage.local.remove(`blocked_${normalizedUrl}`);
          
          if (sender.tab?.id) {
              await chrome.tabs.update(sender.tab.id, { url: request.url });
          }

          sendResponse({ success: true });
          return true;
      }

      if (request.action === "getBlockedSites") {
          const allItems = await chrome.storage.local.get(null);
          const blockedSites = [];
          
          for (const [key, value] of Object.entries(allItems)) {
              if (key.startsWith('blocked_')) {
                  const url = value.normalizedUrl || key.replace('blocked_', '');
                  blockedSites.push({
                      url: url,
                      timestamp: value.timestamp,
                      source: value.source,
                      details: value.details
                  });
              }
          }
          
          blockedSites.sort((a, b) => b.timestamp - a.timestamp);
          sendResponse({ blockedSites });
          return true;
      }
  } catch (error) {
      debug("Error handling message", { error, request });
      sendResponse({ success: false, error: error.message });
      return false;
  }
}

// Enforce maximum blocked sites limit
async function enforceBlockedSitesLimit() {
  try {
      const allItems = await chrome.storage.local.get(null);
      const blockedEntries = Object.entries(allItems)
          .filter(([key]) => key.startsWith('blocked_'))
          .sort((a, b) => b[1].timestamp - a[1].timestamp);

      if (blockedEntries.length > CONFIG.maxBlockedSites) {
          const toRemove = blockedEntries.slice(CONFIG.maxBlockedSites);
          for (const [key] of toRemove) {
              const url = key.replace('blocked_', '');
              userDecisions.delete(url);
              await chrome.storage.local.remove(key);
              debug("Removed old blocked site", url);
          }
      }
  } catch (error) {
      debug("Error enforcing block limit", error);
  }
}

// Clean up expired decisions
async function cleanExpiredDecisions() {
  try {
      const now = Date.now();
      const allItems = await chrome.storage.local.get(null);

      for (const [url, decision] of userDecisions.entries()) {
          if (now - decision.timestamp > CONFIG.decisionExpiry) {
              userDecisions.delete(url);
          }
      }

      for (const [key, value] of Object.entries(allItems)) {
          if (key.startsWith('blocked_') && now - value.timestamp > CONFIG.decisionExpiry) {
              const url = key.replace('blocked_', '');
              userDecisions.delete(url);
              await chrome.storage.local.remove(key);
              debug("Cleaned expired block", url);
          }
      }
  } catch (error) {
      debug("Error cleaning expired decisions", error);
  }
}

// Initialize extension
async function initialize() {
  try {
      debug("Initializing extension");

      const allItems = await chrome.storage.local.get(null);
      for (const [key, value] of Object.entries(allItems)) {
          if (key.startsWith('blocked_')) {
              const url = value.normalizedUrl || key.replace('blocked_', '');
              userDecisions.set(url, {
                  action: 'block',
                  timestamp: value.timestamp || Date.now(),
                  source: value.source || 'storage'
              });
          }
      }

      chrome.webNavigation.onBeforeNavigate.addListener(
          handleNavigation,
          { url: [{ schemes: ['http', 'https'] }] }
      );

      chrome.runtime.onMessage.addListener(handleUserDecision);

      chrome.alarms.create('cleanup', { periodInMinutes: 60 });
      chrome.alarms.onAlarm.addListener(cleanExpiredDecisions);

      debug("Initialization complete");
  } catch (error) {
      debug("Initialization failed", error);
      setTimeout(initialize, 10000);
  }
}

// Start the extension
initialize();

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
      isValidUrl,
      checkUrl,
      handleNavigation,
      handleUserDecision,
      cleanExpiredDecisions
  };
}