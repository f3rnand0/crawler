import re
import unicodedata
from typing import Optional

def slugify(text: str, separator: str = "-") -> str:
    """
    Convert text to a filesystem-safe slug with umlaut transliteration.
    
    Args:
        text: Input text to slugify
        separator: Word separator (default: "-")
    
    Returns:
        Filesystem-safe slug string
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Transliterate German umlauts and special characters
    text = transliterate_umlauts(text)
    
    # Normalize unicode characters (decompose accents)
    text = unicodedata.normalize('NFKD', text)
    
    # Remove non-ASCII characters (after normalization, accents become separate chars)
    text = ''.join(c for c in text if not unicodedata.combining(c))
    
    # Replace spaces and punctuation with separator
    text = re.sub(r'[^\w\s-]', '', text)  # Remove non-word, non-space, non-hyphen
    text = re.sub(r'[-\s]+', separator, text)  # Convert spaces and hyphens to separator
    
    # Remove leading/trailing separators
    text = text.strip(separator)
    
    # Ensure slug is not empty
    if not text:
        # Fallback: use a hash or simple slug
        text = "untitled"
    
    return text

def transliterate_umlauts(text: str) -> str:
    """
    Transliterate German umlauts and special characters to ASCII equivalents.
    
    Args:
        text: Input text with possible umlauts
    
    Returns:
        Text with umlauts transliterated
    """
    # German umlauts
    replacements = {
        'ä': 'ae',
        'ö': 'oe', 
        'ü': 'ue',
        'ß': 'ss',
        'Ä': 'Ae',
        'Ö': 'Oe',
        'Ü': 'Ue',
        # Additional European characters
        'á': 'a',
        'à': 'a',
        'â': 'a',
        'ã': 'a',
        'å': 'a',
        'ç': 'c',
        'é': 'e',
        'è': 'e',
        'ê': 'e',
        'ë': 'e',
        'í': 'i',
        'ì': 'i',
        'î': 'i',
        'ï': 'i',
        'ñ': 'n',
        'ó': 'o',
        'ò': 'o',
        'ô': 'o',
        'õ': 'o',
        'ø': 'o',
        'ú': 'u',
        'ù': 'u',
        'û': 'u',
        'ý': 'y',
        'ÿ': 'y',
        'ž': 'z',
        'š': 's',
        'č': 'c',
        'ř': 'r',
        'ď': 'd',
        'ť': 't',
        'ň': 'n',
        'ľ': 'l',
        'ě': 'e',
    }
    
    # Perform replacements
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text

def extract_grammar_slug_from_url(url: str) -> str:
    """
    Extract grammar lesson slug from URL.
    
    Args:
        url: Grammar lesson URL (e.g., "/es/cambio-de-vocal-a-ä/gr-49930523")
    
    Returns:
        Grammar slug (e.g., "cambio-de-vocal-a-ae")
    """
    # Remove domain if present
    if "//" in url:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        path = parsed.path
    else:
        path = url
    
    # Remove leading/trailing slashes
    path = path.strip("/")
    
    # Split into parts
    parts = path.split("/")
    
    # Look for grammar segment
    for i, part in enumerate(parts):
        if part.startswith("gr-"):
            # Grammar slug should be the previous part
            if i > 0:
                grammar_slug = parts[i-1]
                # Slugify to handle any remaining special chars
                return slugify(grammar_slug)
            break
    
    # Fallback: extract from URL pattern
    match = re.search(r"/([^/]+)/gr-\d+", path)
    if match:
        return slugify(match.group(1))
    
    # Last resort: use the last non-empty segment before /gr-
    segments = [p for p in parts if p and not p.startswith("gr-")]
    if segments:
        return slugify(segments[-1])
    
    return "unknown-grammar"

def extract_lesson_slug_from_url(url: str) -> str:
    """
    Extract lesson slug from URL.
    
    Args:
        url: Lesson URL (e.g., "/es/hallo/l-49702751")
    
    Returns:
        Lesson slug (e.g., "hallo")
    """
    # Remove domain if present
    if "//" in url:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        path = parsed.path
    else:
        path = url
    
    # Remove leading/trailing slashes
    path = path.strip("/")
    
    # Split into parts
    parts = path.split("/")
    
    # Look for lesson segment
    for i, part in enumerate(parts):
        if part.startswith("l-"):
            # Lesson slug should be the previous part
            if i > 0:
                lesson_slug = parts[i-1]
                return slugify(lesson_slug)
            break
    
    # Fallback: extract from URL pattern
    match = re.search(r"/([^/]+)/l-\d+", path)
    if match:
        return slugify(match.group(1))
    
    # Last resort: use the last non-empty segment before /l-
    segments = [p for p in parts if p and not p.startswith("l-")]
    if segments:
        return slugify(segments[-1])
    
    return "unknown-lesson"

def generate_grammar_filename(category_slug: str, grammar_slug: str) -> str:
    """
    Generate filename for grammar lesson markdown file.
    
    Args:
        category_slug: Category slug (e.g., "verbos")
        grammar_slug: Grammar lesson slug (e.g., "cambio-de-vocal-a-ae")
    
    Returns:
        Filename (e.g., "verbos-cambio-de-vocal-a-ae.md")
    """
    # Ensure both slugs are not empty
    if not category_slug:
        category_slug = "uncategorized"
    if not grammar_slug:
        grammar_slug = "untitled"
    
    # Combine with hyphen
    filename = f"{category_slug}-{grammar_slug}.md"
    
    # Ensure filename is not too long (filesystem limits)
    max_length = 255
    if len(filename) > max_length:
        # Truncate grammar slug if needed
        available_length = max_length - len(category_slug) - len(".md") - 1  # -1 for hyphen
        if available_length > 10:  # Keep at least 10 chars for grammar slug
            grammar_slug = grammar_slug[:available_length]
            filename = f"{category_slug}-{grammar_slug}.md"
        else:
            # Very long category slug, just use hash
            import hashlib
            hash_str = hashlib.md5(grammar_slug.encode()).hexdigest()[:8]
            filename = f"{category_slug}-{hash_str}.md"
    
    return filename

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for filesystem safety.
    
    Args:
        filename: Input filename
    
    Returns:
        Sanitized filename safe for all filesystems
    """
    import os
    
    # Replace problematic characters
    filename = re.sub(r'[<>:"/\\|?*]', '-', filename)
    
    # Remove control characters
    filename = ''.join(c for c in filename if ord(c) >= 32)
    
    # Remove leading/trailing dots and spaces (Windows issue)
    filename = filename.strip('. ')
    
    # Ensure not empty
    if not filename:
        filename = "file"
    
    # Truncate if too long
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        if len(ext) > 20:  # Unlikely but handle weird extension
            ext = ext[:20]
        name = name[:255 - len(ext)]
        filename = name + ext
    
    return filename

if __name__ == "__main__":
    # Test slugify function
    test_cases = [
        ("Formal e informal", "formal-e-informal"),
        ("Cambio de vocal: a - ä", "cambio-de-vocal-a-ae"),
        ("¿Präteritum o Perfekt?", "praeteritum-o-perfekt"),
        ("Dass, ob und wenn", "dass-ob-und-wenn"),
        ("Verbos separables", "verbos-separables"),
    ]
    
    print("Testing slugify function:")
    for input_text, expected in test_cases:
        result = slugify(input_text)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{input_text}' -> '{result}' (expected: '{expected}')")
    
    # Test grammar slug extraction
    print("\nTesting grammar slug extraction:")
    test_urls = [
        "/es/cambio-de-vocal-a-ä/gr-49930523",
        "https://learngerman.dw.com/es/formal-e-informal-1/gr-49710895",
        "/es/dass-ob-und-wenn/gr-50099212",
    ]
    
    for url in test_urls:
        slug = extract_grammar_slug_from_url(url)
        print(f"  '{url}' -> '{slug}'")
    
    # Test filename generation
    print("\nTesting filename generation:")
    test_pairs = [
        ("verbos", "cambio-de-vocal-a-ae", "verbos-cambio-de-vocal-a-ae.md"),
        ("preposiciones", "dativo", "preposiciones-dativo.md"),
        ("conjunciones", "dass-ob-und-wenn", "conjunciones-dass-ob-und-wenn.md"),
    ]
    
    for category, grammar, expected in test_pairs:
        filename = generate_grammar_filename(category, grammar)
        status = "✓" if filename == expected else "✗"
        print(f"  {status} {category} + {grammar} -> {filename} (expected: {expected})")