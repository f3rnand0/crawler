# DW Learn German Grammar Extractor

A command-line tool to extract grammar lessons from DW Learn German courses (Nicos Weg). Automatically detects language from URL and exports markdown files organized by grammar category.

## Features

- **URL-based course detection**: Automatically extracts course ID and language from course page URLs
- **Grammar-focused extraction**: Extracts only grammar lessons, ignoring vocabulary and culture pages
- **Flat markdown organization**: All grammar lessons in a single directory with category-prefixed filenames
- **Lesson files**: Individual markdown files for each course unit with links to grammar lessons
- **Language-specific output**: Files organized by language code from URL (es/, en/, de/, etc.)
- **GraphQL API integration**: Uses direct API access (no browser automation needed)

## Installation

1. Clone the repository or download the source code
2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python dw_extract.py --url "https://learngerman.dw.com/es/nicos-weg/c-47994059"
```

### Advanced Options

```bash
python dw_extract.py \
  --url "https://learngerman.dw.com/es/nicos-weg/c-47994059" \
  --output-dir "german_lessons" \
  --batch-size 20 \
  --keep-json \
  --verbose
```

### Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--url` | Course page URL (required) | - |
| `--output-dir` | Output directory | `output` |
| `--batch-size` | GraphQL batch size for fetching data | `20` |
| `--keep-json` | Keep intermediate JSON files | `False` |
| `--verbose` | Enable verbose output | `False` |
| `--version` | Show version | - |

## Output Structure

```
output/es/                          # Language-specific directory
├── course_structure.md             # Course overview with statistics
├── grammar/                        # All grammar lessons (flat directory)
│   ├── INDEX.md                    # Grammar index by category
│   ├── verbos-cambio-de-vocal.md   # Category-prefixed grammar files
│   ├── preposiciones-dativo.md
│   └── ...
└── lessons/                        # Individual lesson files
    ├── INDEX.md                    # Lessons index
    ├── hallo.md                    # Lesson "Hallo!"
    ├── tschüss.md                  # Lesson "Tschüss!"
    └── ...
```

### File Naming Convention

Grammar files follow the pattern: `{category}-{grammar-slug}.md`

- **Category**: Derived from grammar taxonomy (verbos, preposiciones, conjunciones, etc.)
- **Grammar slug**: Extracted from URL, transliterated (ä→ae, ö→oe, ü→ue, ß→ss)

Examples:
- `verbos-cambio-de-vocal-a-ae.md`
- `preposiciones-dativo.md`
- `conjunciones-dass-ob-und-wenn.md`

## Supported Languages

The tool automatically detects language from URL and maps to GraphQL enum:

| URL Prefix | Language | GraphQL Enum |
|------------|----------|--------------|
| `/es/` | Spanish | `SPANISH` |
| `/en/` | English | `ENGLISH` |
| `/de/` | German | `GERMAN` |
| `/fr/` | French | `FRENCH` |
| `/pt/` | Portuguese | `PORTUGUESE_BRAZIL` |
| `/ru/` | Russian | `RUSSIAN` |
| ... and 33 total languages supported by the API |

## How It Works

1. **URL Parsing**: Extracts course ID and language code from the course page URL
2. **GraphQL API**: Uses DW's GraphQL endpoint to fetch course structure and grammar lessons
3. **Batch Processing**: Fetches data in batches for efficiency
4. **HTML to Markdown**: Converts grammar lesson HTML content to readable markdown
5. **File Organization**: Generates flat grammar directory and lesson files with proper linking

## Development

### Project Structure

```
src/
├── crawler.py              # Basic GraphQL client
├── extract_grammar.py      # Grammar extraction logic
├── export_grammar.py       # Grammar export with categories
├── full_export.py          # Complete course structure export
├── enhanced_exporter.py    # Enhanced exporter with flat organization
├── url_parser.py           # URL parsing and language detection
└── slug_utils.py           # Slug utilities with umlaut transliteration
```

### Running Tests

```bash
# Component tests (no network requests)
python test_cli.py

# Integration test with existing data
python test_with_existing_data.py

# Full integration test (makes actual API requests)
python dw_extract.py --url "https://learngerman.dw.com/es/nicos-weg/c-47994059" --output-dir test_output
```

## Example Output

### Grammar File (`verbos-cambio-de-vocal-a-ae.md`)

```markdown
# Cambio de vocal: a - ä

**URL:** https://learngerman.dw.com/es/cambio-de-vocal-a-ä/gr-49930523
**ID:** 49930523
**Category:** Verbos

## Content

Ya conoces verbos en los que se produce el cambio de vocal de *e* a *i*...

*Category: Verbos*  
*Grammar ID: 49930523*  
*Source URL: https://learngerman.dw.com/es/cambio-de-vocal-a-ä/gr-49930523*
```

### Lesson File (`hallo.md`)

```markdown
# Hallo!

**URL:** https://learngerman.dw.com/es/hallo/l-49702751
**ID:** 49702751

**Grammar lessons:** 1
**Vocabulary items:** 28
**Regional studies:** 1

## Grammar Lessons

- [Formal e informal](../grammar/verbos-formal-e-informal.md)

---
*This lesson is part of the course*
```

## Limitations

- Only extracts grammar lessons (not vocabulary or regional studies)
- Requires a stable internet connection for API requests
- Rate limiting: uses batch requests with delays to be polite to the server
- Some language codes may not be mapped correctly (fallback to Spanish)

## License

This project is for educational purposes only. Please respect DW's terms of service and copyright.

## Acknowledgments

- Deutsche Welle for providing free German language learning resources
- GraphQL API exploration by the original crawler implementation