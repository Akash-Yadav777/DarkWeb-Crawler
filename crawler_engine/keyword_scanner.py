def scan_for_keywords(text, keywords=None):
    if keywords is None:
        keywords = ['hack', 'exploit', 'carding', 'malware', 'ransomware', 'leak', 'zero-day']
    found = []
    for word in keywords:
        if word.lower() in text.lower():
            found.append(word)
    return found
