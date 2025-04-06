import re

# List of known phishing indicators
PHISHING_INDICATORS = [
    "login", "secure", "account", "verify", "bank", "paypal", "ebay", 
    "password", "update", "confirm", "click", "phish", "scam", "fraud"
]

# List of trusted domains (root domains only)
TRUSTED_DOMAINS = [
    "amazon.com", "paypal.com", "ebay.com", "google.com", "facebook.com", 
    "microsoft.com", "apple.com", "netflix.com"
]

def extract_domain(url):
    """Extract the domain starting with 'www' or fallback to netloc."""
    domain_match = re.search(r'(www\.[^/]+)', url)
    if domain_match:
        return domain_match.group(1)  # Return the domain with www.
    return url  # Fallback to the raw input

def get_root_domain(domain):
    """Extract the root domain (e.g., 'amazon.com' from 'www.amazon.com')."""
    if domain.startswith("www."):
        domain = domain[4:]  # Remove 'www.'
    parts = domain.split('.')
    if len(parts) > 2:
        return '.'.join(parts[-2:])  # Extract the last two parts
    return domain

def is_suspicious_domain(domain):
    """Check if the domain contains phishing indicators."""
    for indicator in PHISHING_INDICATORS:
        if indicator in domain:
            return True
    return False

def is_trusted_domain(domain):
    """Check if the domain is in the list of trusted domains."""
    root_domain = get_root_domain(domain)
    return root_domain in TRUSTED_DOMAINS

def check_url(url):
    """Analyze the URL for phishing indicators."""
    domain = extract_domain(url)
    root_domain = get_root_domain(domain)

    print(f"\nAnalyzing URL: {url}")
    print(f"Extracted Domain: {domain}")
    print(f"Root Domain: {root_domain}")

    # Check if the domain is trusted
    if is_trusted_domain(domain):
        print(f"[+] Trusted domain detected: {domain}")
        return  # Exit early for trusted domains

    # Check if the domain is suspicious
    if is_suspicious_domain(domain):
        print(f"[!] Warning: Suspicious domain detected: {domain}")

    print(f"[!] Phishing indicators detected for: {url}")

def main():
    # Get user input for URLs to check
    while True:
        url = input("Enter the URL to check (or type 'exit' to quit): ").strip()
        if url.lower() == "exit":
            print("Exiting the program.")
            break
        check_url(url)

if __name__ == "__main__":
    main()
