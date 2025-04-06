document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const url = params.get('url');
    const source = params.get('source');
    const details = JSON.parse(params.get('details'));
  
    document.getElementById('warning-url').textContent = url;
  
    // Display threat details
    const detailsContainer = document.getElementById('threat-details');
    detailsContainer.innerHTML = `
      <p><strong>Source:</strong> ${source}</p>
      <p><strong>Threat Type:</strong> ${details.threat}</p>
      ${details.tags?.length ? `<p><strong>Tags:</strong> ${details.tags.join(', ')}</p>` : ''}
      ${details.reference ? `<p><a href="${details.reference}" target="_blank">More Info</a></p>` : ''}
    `;
  
    // Button handlers
    document.getElementById('continue').addEventListener('click', () => {
      chrome.runtime.sendMessage({
        action: "phishDecision",
        url: url,
        decision: "continue"
      }, () => {
        window.location.href = url;
      });
    });
  
    document.getElementById('block').addEventListener('click', () => {
      chrome.runtime.sendMessage({
        action: "phishDecision",
        url: url,
        decision: "block"
      }, () => {
        window.location.href = chrome.runtime.getURL("blocked.html") + `?url=${encodeURIComponent(url)}`;
      });
    });
  });