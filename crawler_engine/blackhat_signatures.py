# crawler_engine/blackhat_signatures.py

import re

# Simple list of suspicious patterns for blackhat activity
BLACKHAT_PATTERNS = [
    r"carding",  # Credit card fraud
    r"cvv dumps?",
    r"paypal\s+accounts?",
    r"fake\s+passports?",
    r"hack\s+tools?",
    r"keyloggers?",
    r"exploit\s+kits?",
    r"zero\s+day",
    r"buy\s+drugs?",
    r"bitcoin\s+mixers?",
    r"ransomware",
    r"botnet\s+rentals?",
    r"ssh\s+brute\s+force",
    r"ddos\s+services?",
]

def detect_blackhat_signatures(html_content):
    found = []
    for pattern in BLACKHAT_PATTERNS:
        if re.search(pattern, html_content, re.IGNORECASE):
            found.append(pattern)
    return found
