document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('blocked-sites-container');
  const list = document.getElementById('blocked-sites-list');
  let blockedSitesPort = null; // Connection for blocked sites list
  let unblockPort = null;      // Connection for unblock operations

  // Enhanced error display function
  function showError(message) {
      list.innerHTML = `
          <li class="error-message">
              <div>⚠️ ${message}</div>
              <button id="retry-btn">Try Again</button>
          </li>
      `;
      document.getElementById('retry-btn').addEventListener('click', loadBlockedSites);
  }

  // Main loading function
  function loadBlockedSites() {
      // Clean up any existing connection
      if (blockedSitesPort) {
          blockedSitesPort.disconnect();
      }

      list.innerHTML = '<li class="loading-message">Loading blocked sites...</li>';
      container.classList.remove('hidden');

      // Create persistent connection
      blockedSitesPort = chrome.runtime.connect({ name: "blockedSitesQuery" });

      // Handle incoming messages
      blockedSitesPort.onMessage.addListener((response) => {
          console.log('[Popup] Received response:', response);
          
          if (response.error) {
              showError(response.error);
              return;
          }

          if (response.blockedSites && response.blockedSites.length > 0) {
              renderBlockedSites(response.blockedSites);
          } else {
              showEmptyState();
          }
      });

      // Handle disconnection
      blockedSitesPort.onDisconnect.addListener(() => {
          if (chrome.runtime.lastError) {
              console.error('[Popup] Port disconnected:', chrome.runtime.lastError);
              showError('Connection to extension lost');
          }
          blockedSitesPort = null;
      });

      // Send the request
      blockedSitesPort.postMessage({ action: "getBlockedSites" });
  }

  function renderBlockedSites(sites) {
      console.log(`[Popup] Rendering ${sites.length} blocked sites`);
      list.innerHTML = '';
      
      sites.forEach(site => {
          const li = document.createElement('li');
          li.innerHTML = `
              <span class="blocked-url" title="${site.url}">${truncateUrl(site.url)}</span>
              <button class="unblock-btn" data-url="${site.url}">Unblock</button>
              <span class="status-message"></span>
          `;
          list.appendChild(li);
      });

      // Add click handlers for unblock buttons
      document.querySelectorAll('.unblock-btn').forEach(btn => {
          btn.addEventListener('click', handleUnblockClick);
      });
  }

  async function handleUnblockClick(e) {
      const btn = e.target;
      const url = btn.getAttribute('data-url');
      const statusElement = btn.nextElementSibling;
      
      btn.disabled = true;
      btn.textContent = 'Unblocking...';
      statusElement.textContent = '';
      statusElement.style.color = '';

      try {
          console.log(`[Popup] Unblocking: ${url}`);
          
          // Clean up any existing unblock connection
          if (unblockPort) {
              unblockPort.disconnect();
          }

          // Create new connection for this unblock operation
          unblockPort = chrome.runtime.connect({ name: "unblockSite" });
          
          const result = await new Promise((resolve, reject) => {
              unblockPort.onMessage.addListener((response) => {
                  unblockPort.disconnect();
                  unblockPort = null;
                  
                  if (response.error) {
                      reject(new Error(response.error));
                  } else {
                      resolve(response);
                  }
              });
              
              unblockPort.postMessage({ 
                  action: "unblockSite", 
                  url: url 
              });
          });

          if (result?.success) {
              console.log('[Popup] Unblock successful');
              // Visual feedback before removing
              const item = btn.closest('li');
              item.style.opacity = '0.5';
              item.style.transition = 'opacity 0.3s ease';
              
              statusElement.textContent = '✓ Unblocked';
              statusElement.style.color = '#2ecc71';
              
              setTimeout(() => {
                  item.remove();
                  if (list.children.length === 0) {
                      showEmptyState();
                  }
              }, 500);
          } else {
              throw new Error(result?.error || 'Unblock failed');
          }
      } catch (error) {
          console.error('[Popup] Unblock error:', error);
          btn.textContent = 'Unblock';
          btn.disabled = false;
          
          statusElement.textContent = '✗ Failed - ' + error.message;
          statusElement.style.color = '#e74c3c';
          
          // Clear error message after delay
          setTimeout(() => {
              statusElement.textContent = '';
          }, 3000);
      }
  }

  function showEmptyState() {
      list.innerHTML = '<li class="empty-message">No websites currently blocked</li>';
  }

  function truncateUrl(url, maxLength = 40) {
      return url.length > maxLength ? 
          url.substring(0, maxLength) + '...' : 
          url;
  }

  // Clean up connections when popup closes
  window.addEventListener('beforeunload', () => {
      if (blockedSitesPort) {
          blockedSitesPort.disconnect();
      }
      if (unblockPort) {
          unblockPort.disconnect();
      }
  });

  // Dynamic styles
  const style = document.createElement('style');
  style.textContent = `
      .blocked-url {
          flex: 1;
          word-break: break-all;
          margin-right: 10px;
          font-size: 13px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
      }
      .unblock-btn {
          background-color: #e74c3c;
          color: white;
          border: none;
          padding: 4px 8px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 12px;
          white-space: nowrap;
          transition: all 0.2s;
          margin-right: 5px;
      }
      .unblock-btn:hover {
          background-color: #c0392b;
      }
      .unblock-btn:disabled {
          opacity: 0.7;
          cursor: not-allowed;
      }
      #blocked-sites-list {
          list-style: none;
          padding: 0;
          margin: 0;
          max-height: 300px;
          overflow-y: auto;
      }
      #blocked-sites-list li {
          display: flex;
          align-items: center;
          padding: 8px 12px;
          border-bottom: 1px solid #eee;
          transition: opacity 0.3s ease;
      }
      .empty-message {
          color: #95a5a6;
          font-style: italic;
          text-align: center;
          padding: 16px 0;
      }
      .error-message {
          color: #e74c3c;
          text-align: center;
          padding: 12px;
      }
      .error-message div {
          margin-bottom: 8px;
      }
      #retry-btn {
          background-color: #3498db;
          color: white;
          border: none;
          padding: 6px 12px;
          border-radius: 4px;
          cursor: pointer;
      }
      .loading-message {
          color: #7f8c8d;
          text-align: center;
          padding: 16px 0;
          font-style: italic;
      }
      .status-message {
          font-size: 11px;
          margin-left: 5px;
          transition: all 0.3s ease;
      }
  `;
  document.head.appendChild(style);

  // Initial load
  loadBlockedSites();
});