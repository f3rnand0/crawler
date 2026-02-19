import re
from typing import Tuple, Optional
from urllib.parse import urlparse

class URLParserError(Exception):
    """Exception raised for URL parsing errors."""
    pass

def parse_course_url(url: str) -> Tuple[int, str, str]:
    """
    Parse a DW Learn German course URL to extract course ID, language code, and GraphQL language enum.
    
    Args:
        url: Course page URL (e.g., "https://learngerman.dw.com/es/nicos-weg/c-47994059")
    
    Returns:
        Tuple of (course_id, language_code, language_enum)
    
    Raises:
        URLParserError: If URL format is invalid or unsupported
    """
    # Parse URL
    parsed = urlparse(url)
    
    # Validate domain
    if "learngerman.dw.com" not in parsed.netloc:
        raise URLParserError(f"Invalid domain: {parsed.netloc}. Expected learngerman.dw.com")
    
    # Extract path components
    path = parsed.path.strip("/")
    parts = path.split("/")
    
    if len(parts) < 3:
        raise URLParserError(f"Invalid URL path format: {path}. Expected /{{lang}}/{{slug}}/c-{{id}}")
    
    # Extract language code (first segment)
    lang_code = parts[0].lower()
    
    # Find course ID segment (ends with /c-{id})
    course_segment = None
    course_id = None
    
    for i, segment in enumerate(parts):
        if segment.startswith("c-"):
            course_segment = segment
            # Validate there's a slug before the course segment
            if i < 1:
                raise URLParserError(f"Missing slug before course ID in: {path}")
            break
    
    if not course_segment:
        # Alternative pattern: look for course ID in any segment
        for segment in parts:
            if segment.startswith("c-"):
                course_segment = segment
                break
    
    if not course_segment:
        raise URLParserError(f"No course ID found in URL path: {path}")
    
    # Extract course ID
    match = re.match(r"c-(\d+)$", course_segment)
    if not match:
        raise URLParserError(f"Invalid course ID format: {course_segment}. Expected c-{{number}}")
    
    course_id = int(match.group(1))
    
    # Map language code to GraphQL enum
    language_enum = map_language_code_to_enum(lang_code)
    
    return course_id, lang_code, language_enum

def map_language_code_to_enum(lang_code: str) -> str:
    """
    Map URL language code to GraphQL Language enum value.
    
    Args:
        lang_code: Language code from URL (e.g., "es", "en", "de")
    
    Returns:
        GraphQL Language enum value
    
    Raises:
        URLParserError: If language code is not supported
    """
    language_map = {
        # Common languages
        "es": "SPANISH",
        "en": "ENGLISH", 
        "de": "GERMAN",
        "fr": "FRENCH",
        "pt": "PORTUGUESE_BRAZIL",
        "ru": "RUSSIAN",
        "ar": "ARABIC",
        "zh": "CHINESE",
        "zh-tw": "CHINESE_TRADITIONAL",
        # Additional languages from GraphQL schema
        "sq": "ALBANIAN",
        "am": "AMHARIC",
        "bn": "BENGALI",
        "bs": "BOSNIAN",
        "bg": "BULGARIAN",
        "prs": "DARI",  # Dari (Afghan Persian)
        "el": "GREEK",
        "ha": "HAUSA",
        "hi": "HINDI",
        "id": "INDONESIAN",
        "sw": "KISWAHILI",
        "hr": "CROATIAN",
        "mk": "MACEDONIAN",
        "ps": "PASHTO",
        "fa": "PERSIAN",
        "pl": "POLISH",
        "pt-ao": "PORTUGUESE_AFRICA",  # Portuguese (Africa)
        "ro": "ROMANIAN",
        "sr": "SERBIAN",
        "tr": "TURKISH",
        "uk": "UKRANIAN",
        "ur": "URDU",
        "hu": "HUNGARIAN",
    }
    
    # Try exact match first
    if lang_code in language_map:
        return language_map[lang_code]
    
    # Try language-region codes (e.g., pt-br -> pt)
    if "-" in lang_code:
        base_lang = lang_code.split("-")[0]
        if base_lang in language_map:
            return language_map[base_lang]
    
    # Fallback to common mappings or raise error
    common_fallbacks = {
        "it": "SPANISH",  # Italian not in schema, fallback to Spanish
        "nl": "ENGLISH",  # Dutch not in schema, fallback to English
        "ja": "ENGLISH",  # Japanese not in schema
        "ko": "ENGLISH",  # Korean not in schema
    }
    
    if lang_code in common_fallbacks:
        return common_fallbacks[lang_code]
    
    # Default to SPANISH for unknown languages (most courses are in Spanish)
    return "SPANISH"

def extract_slug_from_url(url: str, slug_type: str = "course") -> str:
    """
    Extract slug from URL path.
    
    Args:
        url: The URL to parse
        slug_type: Type of slug to extract ("course", "lesson", "grammar")
    
    Returns:
        The slug string
    
    Raises:
        URLParserError: If slug cannot be extracted
    """
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    parts = path.split("/")
    
    if slug_type == "course":
        # Course slug is before /c-{id}
        for i, segment in enumerate(parts):
            if segment.startswith("c-"):
                if i > 0:
                    return parts[i-1]
                break
    
    elif slug_type == "lesson":
        # Lesson slug is before /l-{id}
        for i, segment in enumerate(parts):
            if segment.startswith("l-"):
                if i > 0:
                    return parts[i-1]
                break
    
    elif slug_type == "grammar":
        # Grammar slug is before /gr-{id}
        for i, segment in enumerate(parts):
            if segment.startswith("gr-"):
                if i > 0:
                    return parts[i-1]
                break
    
    raise URLParserError(f"Cannot extract {slug_type} slug from URL: {url}")

def validate_url_format(url: str) -> bool:
    """
    Validate that URL has correct format for DW Learn German course.
    
    Args:
        url: URL to validate
    
    Returns:
        True if URL format is valid
    """
    try:
        parse_course_url(url)
        return True
    except URLParserError:
        return False

if __name__ == "__main__":
    # Test with example URLs
    test_urls = [
        "https://learngerman.dw.com/es/nicos-weg/c-47994059",
        "https://learngerman.dw.com/en/nicos-weg/c-47994059",
        "https://learngerman.dw.com/de/nicos-weg/c-47994059",
        "https://learngerman.dw.com/pt/nicos-weg/c-47994059",
        "https://learngerman.dw.com/fr/nicos-weg/c-47994059",
    ]
    
    for test_url in test_urls:
        try:
            course_id, lang_code, lang_enum = parse_course_url(test_url)
            print(f"URL: {test_url}")
            print(f"  Course ID: {course_id}")
            print(f"  Language code: {lang_code}")
            print(f"  Language enum: {lang_enum}")
            print(f"  Course slug: {extract_slug_from_url(test_url, 'course')}")
            print()
        except URLParserError as e:
            print(f"Error parsing {test_url}: {e}")
            print()