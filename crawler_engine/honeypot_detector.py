def is_honeypot(html):
    triggers = ['this site is under surveillance', 'law enforcement', 'report abuse']
    for trigger in triggers:
        if trigger.lower() in html.lower():
            return True
    return False
