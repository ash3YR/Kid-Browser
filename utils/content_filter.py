import re
from better_profanity import profanity

# Load custom profanity filter
profanity.load_censor_words()

# Blocked and allowed websites
blocked_websites = []
allowed_websites = []

# Blocked patterns
blocked_patterns = [
    r'\b(drugs?|alcohol|gambling|violence)\b',
    r'\b(xxx|porn|adult|crime|boobs|melons|whiskers|cannons)\b',
]

def is_safe_url(url):
    """Check if a URL is safe for children."""
    # Check blocked/allowed lists
    if url in blocked_websites:
        return False
    if allowed_websites and url not in allowed_websites:
        return False
    
    # Check for unsafe keywords
    unsafe_keywords = ['adult', 'xxx', 'porn', 'gambling', 'violence']
    return not any(keyword in url.lower() for keyword in unsafe_keywords)