import re
import string

# Define a basic list of stopwords to avoid heavy NLTK dependency if not needed, 
# or we can keep it simple. Let's use a standard list.
STOPWORDS = set([
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", 
    "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", 
    "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", 
    "theirs", "themselves", "what", "which", "who", "whom", "this", "that", 
    "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", 
    "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", 
    "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", 
    "at", "by", "for", "with", "about", "against", "between", "into", "through", 
    "during", "before", "after", "above", "below", "to", "from", "up", "down", 
    "in", "out", "on", "off", "over", "under", "again", "further", "then", 
    "once", "here", "there", "when", "where", "why", "how", "all", "any", 
    "both", "each", "few", "more", "most", "other", "some", "such", "no", 
    "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", 
    "t", "can", "will", "just", "don", "should", "now"
])

def remove_urls(text: str) -> str:
    """Remove URLs from text."""
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    return url_pattern.sub(r'', text)

def remove_emojis(text: str) -> str:
    """Remove emojis from text. (Simple approach for emojis and non-ascii)"""
    return text.encode('ascii', 'ignore').decode('ascii')

def lowercase_text(text: str) -> str:
    """Convert text to lowercase."""
    return text.lower()

def remove_special_characters(text: str) -> str:
    """Remove punctuation and special characters, keeping alphanumeric and spaces."""
    return text.translate(str.maketrans('', '', string.punctuation))

def remove_stopwords(text: str) -> str:
    """Remove common English stopwords."""
    words = text.split()
    filtered_words = [word for word in words if word not in STOPWORDS]
    return ' '.join(filtered_words)

def clean_reddit_text(text: str) -> str:
    """
    Main function to run the full text cleaning pipeline.
    """
    if not text:
        return ""
    
    # Order matters
    text = lowercase_text(text)
    text = remove_urls(text)
    text = remove_emojis(text)
    text = remove_special_characters(text)
    text = remove_stopwords(text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text
