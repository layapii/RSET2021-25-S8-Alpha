document.addEventListener('DOMContentLoaded', function() {
    // Configuration
    const GOOGLE_API_KEY = 'AIzaSyBRgXxGFIxWy5MEtp4Xg9lF6ujJ6X70EHY'; // Replace with your actual key
    const CACHE_DURATION = 30 * 60 * 1000; // 30 minutes cache

    // DOM elements
    const result = document.getElementById('result');
    const phishingType = document.getElementById('phishingType');
    const details = document.getElementById('details');

    // Main check function
    async function checkUrl(url) {
        if (!url) {
            showResult('warning', 'No URL Found', 'No active tab URL was found.');
            return;
        }

        // 1. Check cache first
        const cached = await checkCache(url);
        if (cached) {
            showResult(cached.type, cached.title, cached.message);
            return;
        }

        // 2. Verify with Google Safe Browsing (most reliable)
        const gsbResult = await checkGoogleSafeBrowsing(url);
        if (gsbResult?.isThreat) {
            const threatInfo = gsbResult.threats.map(t => `${t.threatType}/${t.platformType}`).join(', ');
            await cacheResult(url, 'danger', 'Google Safe Browsing Alert', 
                `Google identifies this as: ${threatInfo}`);
            return;
        }

        // 3. Check URLhaus as secondary source
        const urlhausResult = await checkURLhaus(url);
        if (urlhausResult?.threat) {
            await cacheResult(url, 'danger', 'URLhaus Alert', 
                `URLhaus reports: ${urlhausResult.threat} (${urlhausResult.tags?.join(', ')})`);
            return;
        }

        // 4. Run local heuristic checks
        const localResult = runLocalChecks(url);
        if (localResult) {
            await cacheResult(url, localResult.type, localResult.title, localResult.message);
            return;
        }

        // 5. Final fallback
        const isHTTPS = url.startsWith('https://');
        await cacheResult(url, 'safe', 'No Threats Detected', 
            `No known threats found. ${isHTTPS ? 'HTTPS secured.' : 'Warning: No HTTPS.'}`);
    }

    // Google Safe Browsing API v4
    async function checkGoogleSafeBrowsing(url) {
        try {
            const apiUrl = `https://safebrowsing.googleapis.com/v4/threatMatches:find?key=${GOOGLE_API_KEY}`;
            const body = {
                client: {
                    clientId: "your-extension-name",
                    clientVersion: "1.0"
                },
                threatInfo: {
                    threatTypes: ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE"],
                    platformTypes: ["ANY_PLATFORM"],
                    threatEntryTypes: ["URL"],
                    threatEntries: [{url}]
                }
            };

            const response = await fetch(apiUrl, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(body)
            });

            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            return {
                isThreat: data.matches?.length > 0,
                threats: data.matches || []
            };
        } catch (error) {
            console.error("Google Safe Browsing check failed:", error);
            return null;
        }
    }

    // URLhaus check (unchanged from previous)
    async function checkURLhaus(url) { /* ... */ }

    // Local pattern checks (unchanged from previous)
    function runLocalChecks(url) { /* ... */ }

    // Cache management
    async function checkCache(url) {
        const cache = await chrome.storage.local.get('urlCache');
        const entry = cache.urlCache?.[url];
        if (entry && (Date.now() - entry.timestamp < CACHE_DURATION)) {
            return entry.result;
        }
        return null;
    }

    async function cacheResult(url, type, title, message) {
        const cache = await chrome.storage.local.get('urlCache');
        const newCache = {
            ...cache.urlCache,
            [url]: {
                result: {type, title, message},
                timestamp: Date.now()
            }
        };
        await chrome.storage.local.set({urlCache: newCache});
        showResult(type, title, message);
    }

    // Get current tab URL
    chrome.tabs.query({active: true, currentWindow: true}, tabs => {
        checkUrl(tabs[0]?.url);
    });
});