document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const url = params.get('url');
    document.getElementById('blocked-url').textContent = url;
  
    document.getElementById('back').addEventListener('click', () => {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0]?.id) {
          chrome.tabs.update(tabs[0].id, { url: "chrome://newtab" });
        }
      });
    });

    document.getElementById('unblock').addEventListener('click', () => {
      chrome.runtime.sendMessage({
        action: "unblockSite",
        url: url
      }, (response) => {
        if (response.success) {
          // Redirect to the unblocked site
          chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (tabs[0]?.id) {
              chrome.tabs.update(tabs[0].id, { url: url });
            }
          });
        } else {
          alert("Failed to unblock the site. Please try again.");
        }
      });
    });
});