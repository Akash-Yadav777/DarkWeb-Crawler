# crawler_engine/tor_session_manager.py

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def get_tor_session(proxy_url="socks5h://127.0.0.1:9050", timeout=30, user_agent=None):
    session = requests.Session()

    # Set SOCKS5 proxy (ensure 'requests[socks]' is installed)
    session.proxies = {
        'http': proxy_url,
        'https': proxy_url
    }

    # Optional: set headers like User-Agent
    if user_agent:
        session.headers.update({'User-Agent': user_agent})

    # Retry mechanism
    retries = Retry(total=3, backoff_factor=1)
    session.mount("http://", HTTPAdapter(max_retries=retries))
    session.mount("https://", HTTPAdapter(max_retries=retries))

    session.timeout = timeout
    return session
