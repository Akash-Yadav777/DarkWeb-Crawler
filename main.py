import os
import json
import time
from crawler_engine.tor_session_manager import get_tor_session
from crawler_engine.keyword_scanner import scan_for_keywords
from crawler_engine.honeypot_detector import is_honeypot
from crawler_engine.deep_link_extractor import extract_onion_links
from crawler_engine.html_cleaner import clean_html
from crawler_engine.blackhat_signatures import detect_blackhat_signatures

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

# Load seed links from both JSON files
def load_seeds(file_path):
    seeds = []
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                data = json.load(f)
                seeds.extend(data)
            except json.JSONDecodeError:
                for line in f:
                    try:
                        seeds.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        continue
    return seeds

# Load seeds
hidden_wiki_seeds = load_seeds("seeds/hidden_wiki_links.json")
leaked_forum_seeds = load_seeds("seeds/leaked_forum_urls.json")

# Prepare queue
seen_links = set()
queue = []

# Add hidden wiki first
for entry in hidden_wiki_seeds:
    url = entry.get("url")
    depth = entry.get("depth", 0)
    if url and url not in seen_links:
        seen_links.add(url)
        queue.append((url, depth))

# Then leaked forum seeds
for entry in leaked_forum_seeds:
    url = entry.get("url")
    depth = entry.get("depth", 0)
    if url and url not in seen_links:
        seen_links.add(url)
        queue.append((url, depth))

# Setup TOR session
session = get_tor_session(
    proxy_url=config["tor_proxy"],
    timeout=config["timeout"],
    user_agent=config["user_agent"]
)

# Prepare folders
os.makedirs("storage/full_html", exist_ok=True)
os.makedirs("storage/screenshots", exist_ok=True)
os.makedirs("seeds", exist_ok=True)

# Prepare discovered and suspicious files
discovered_file = "seeds/discovered_links.json"
suspicious_file = "seeds/suspicious_links.json"
open(discovered_file, 'a').close()
open(suspicious_file, 'a').close()

# Crawl loop
crawled_count = 0

while queue and crawled_count < config["max_pages"]:
    print(f"[DEBUG] Queue size: {len(queue)} | Crawled count: {crawled_count}")
    url, depth = queue.pop(0)
    print(f"[DEBUG] Crawling URL: {url} at depth {depth}")

    try:
        response = session.get(url)
        print(f"[DEBUG] Response status code for {url}: {response.status_code}")

        if response.status_code == 200:
            content = response.text

            # ✅ Clean HTML
            cleaned_content = clean_html(content)

            # ✅ Save HTML
            if config.get("save_html"):
                safe_name = url.replace("http://", "").replace("/", "_")
                with open(f"storage/full_html/{safe_name}.html", "w", encoding="utf-8") as f:
                    f.write(cleaned_content)

            # ✅ Scan for keywords
            if config.get("scan_keywords"):
                found_keywords = scan_for_keywords(cleaned_content)
                if found_keywords:
                    print(f"[!] Keywords found in {url}: {found_keywords}")

            # ✅ Honeypot detection
            if config.get("detect_honeypots"):
                if is_honeypot(cleaned_content):
                    print(f"[⚠] Potential Honeypot detected at: {url}")

            # ✅ Detect blackhat signatures
            suspicious_patterns = detect_blackhat_signatures(cleaned_content)
            if suspicious_patterns:
                print(f"[⚠] Blackhat signatures in {url}: {suspicious_patterns}")
                # Save suspicious link
                suspicious_entry = {"url": url, "depth": depth, "signatures": suspicious_patterns}
                with open(suspicious_file, "a") as f:
                    f.write(json.dumps(suspicious_entry) + "\n")

            # ✅ Extract new links
            if config.get("extract_links") and depth < config.get("depth_limit", 1):
                new_links = extract_onion_links(cleaned_content)
                print(f"[DEBUG] Found {len(new_links)} new links at depth {depth}")

                for link in new_links:
                    if link not in seen_links:
                        print(f"[DEBUG] Adding new link to queue: {link}")
                        seen_links.add(link)
                        queue.append((link, depth + 1))

                        try:
                            link_response = session.get(link)
                            if link_response.status_code == 200:
                                link_content = clean_html(link_response.text)
                                blackhat_found = detect_blackhat_signatures(link_content)

                                new_entry = {
                                    "url": link,
                                    "depth": depth + 1,
                                    "suspicious": bool(blackhat_found)
                                }

                                # Save to discovered files
                                with open(discovered_file, "a") as f:
                                    f.write(json.dumps(new_entry) + "\n")
                                with open("seeds/hidden_wiki_links.json", "a") as f:
                                    f.write(json.dumps(new_entry) + "\n")

                                if blackhat_found:
                                    with open(suspicious_file, "a") as f:
                                        new_entry["signatures"] = blackhat_found
                                        f.write(json.dumps(new_entry) + "\n")

                                print(f"[+] New .onion link discovered (depth {depth + 1}): {link}")

                        except Exception as link_ex:
                            print(f"[ERROR] Couldn't fetch discovered link: {link} => {link_ex}")

            crawled_count += 1

        else:
            print(f"[-] Failed ({response.status_code}) for {url}")

    except Exception as e:
        print(f"[ERROR] {url}: {e}")

    time.sleep(3)  # Polite delay
