import re

# Technical terms that should be protected before general punctuation stripping
TECH_PROTECTED_TERMS = {
    "c++": "cpp_token",
    "c#": "csharp_token",
    ".net": "dotnet_token",
    "node.js": "nodejs_token",
    "react.js": "reactjs_token",
    "vue.js": "vuejs_token",
    "angular.js": "angularjs_token",
    "next.js": "nextjs_token",
    "nest.js": "nestjs_token",
    "ci/cd": "cicd_token",
    "tcp/ip": "tcpip_token",
    "rest api": "restapi_token",
    "restful api": "restfulapi_token",
}

# Inverted mapping to restore protected tokens
TOKEN_RESTORE_MAP = {v: k for k, v in TECH_PROTECTED_TERMS.items()}

# Standard common English stopwords (excluding technical tokens or short query words)
STANDARD_STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", 
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", 
    "by", "could", "did", "do", "does", "doing", "down", "during", "each", "few", "for", "from", 
    "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself", "him", 
    "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "me", "more", 
    "most", "my", "myself", "nor", "of", "off", "on", "once", "only", "or", "other", "ought", 
    "our", "ours", "ourselves", "out", "over", "own", "same", "she", "should", "so", "some", 
    "such", "than", "that", "the", "their", "theirs", "them", "themselves", "then", "there", 
    "these", "they", "this", "those", "through", "to", "too", "under", "until", "up", "very", 
    "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom", "why", 
    "with", "would", "you", "your", "yours", "yourself", "yourselves"
}

def clean_text(text: str, remove_stopwords: bool = False) -> str:
    """
    Cleans raw text while preserving essential technical tokens (C++, C#, Node.js, etc.).
    
    Steps:
    1. Lowercase conversion
    2. Token protection for special programming languages/tools
    3. Punctuation filtering (preserving hyphens and alphanumeric characters)
    4. Token restoration
    5. Whitespace normalization
    """
    if not text or not isinstance(text, str):
        return ""

    lowered = text.lower()

    # Protect technical keywords like C++, C#, .NET
    for term, token in TECH_PROTECTED_TERMS.items():
        pattern = re.escape(term)
        lowered = re.sub(pattern, f" {token} ", lowered)

    # Remove email addresses and URLs for clean NLP processing
    lowered = re.sub(r"\S+@\S+", " ", lowered)
    lowered = re.sub(r"https?://\S+|www\.\S+", " ", lowered)

    # Replace punctuation that is not part of protected tokens with spaces
    # Allow alphanumeric characters and underscore
    cleaned = re.sub(r"[^\w\s]", " ", lowered)

    # Restore protected tokens
    for token, original in TOKEN_RESTORE_MAP.items():
        cleaned = re.sub(rf"\b{token}\b", original, cleaned)

    tokens = cleaned.split()

    if remove_stopwords:
        tokens = [t for t in tokens if t not in STANDARD_STOPWORDS and len(t) > 1]

    return " ".join(tokens)
