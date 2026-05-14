import re

def extract_onion_links(html):
    # Case-insensitive और अधिक flexible regex
    return re.findall(r'https?://[a-z0-9\.]{5,}\.onion[^\s"\'<>]*', html, flags=re.IGNORECASE)
