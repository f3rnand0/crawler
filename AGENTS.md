# Agent Guidelines for DW Learn German Grammar Extractor

This document provides guidelines for AI agents working on this codebase, including build/lint/test commands and code style conventions.

## Build/Lint/Test Commands

### Installation
```bash
pip install -r requirements.txt
```

### Testing
This project uses custom test scripts rather than a formal test framework like pytest. Use `python` or `python3` depending on your system (the shebang uses `python3`).

- **Run component tests** (no network requests):
  ```bash
  python test_cli.py
  ```

- **Integration test with existing data**:
  ```bash
  python test_with_existing_data.py
  ```

- **Full integration test** (makes actual API requests):
  ```bash
  python dw_extract.py --url "https://learngerman.dw.com/es/nicos-weg/c-47994059" --output-dir test_output
  ```

- **Individual test files** (run directly):
  ```bash
  python test_detail.py
  python test_course_knowledge.py
  python test_lesson_knowledge.py
  python test_graphql.py
  ```

- **Run all tests** (in sequence):
  ```bash
  python test_cli.py && python test_with_existing_data.py
  ```

### Linting and Formatting
No formal linting or formatting tools are configured. However, agents should follow the existing code style (see below). If adding linting is desired, consider:

```bash
# Suggested tools (not yet installed)
pip install black isort ruff mypy
```

- **Format with black** (if adopted):
  ```bash
  black src/ tests/ *.py
  ```

- **Sort imports with isort** (if adopted):
  ```bash
  isort src/ tests/ *.py
  ```

- **Lint with ruff** (if adopted):
  ```bash
  ruff check src/ tests/ *.py --fix
  ```

- **Type checking with mypy** (if adopted):
  ```bash
  mypy src/ --ignore-missing-imports
  ```

### Build/Packaging
No build system is currently configured. The project is a collection of Python scripts.

## Code Style Guidelines

### Python Version
- Python 3.7+ (based on typing usage)

### Imports
- **Order**: Standard library imports first, then third-party imports, then local imports.
- **Grouping**: Separate groups with a blank line.
- **Format**: One import per line, except for `from typing import ...` which can import multiple names.
- **Absolute imports**: Use absolute imports for local modules (e.g., `from src.url_parser import ...`).

**Example:**
```python
import json
import time
from typing import Dict, List, Any, Optional

import requests
from bs4 import BeautifulSoup

from src.url_parser import parse_course_url
from src.slug_utils import slugify
```

### Formatting
- **Indentation**: 4 spaces per level (no tabs).
- **Line length**: Approximately 80–100 characters (not strictly enforced).
- **Quotes**: Double quotes (`"`) for strings, single quotes for characters inside strings if needed.
- **Trailing commas**: Not used consistently.
- **Whitespace**: Use blank lines to separate logical sections, functions, and classes.

### Naming Conventions
- **Classes**: `CamelCase` (e.g., `DWGraphQLClient`, `EnhancedExporter`).
- **Functions/Methods**: `snake_case` (e.g., `parse_course_url`, `extract_grammar`).
- **Variables**: `snake_case` (e.g., `course_id`, `lang_code`).
- **Constants**: `UPPER_SNAKE_CASE` (not widely used in this codebase).
- **Modules/Files**: `snake_case` (e.g., `url_parser.py`, `slug_utils.py`).

### Typing
- Use type hints for function arguments and return values.
- Common types: `Dict`, `List`, `Any`, `Optional`, `Union`.
- Type hints are placed after a colon, with return type after `->`.

**Example:**
```python
def get_course(course_id: int, lang: str = "SPANISH") -> Optional[Dict[str, Any]]:
```

### Error Handling
- Use `try`/`except` blocks for expected exceptions.
- Use `response.raise_for_status()` for HTTP errors.
- Propagate exceptions with meaningful error messages.

**Example:**
```python
try:
    course_id, lang_code, lang_enum = parse_course_url(url)
except ValueError as e:
    print(f"Invalid URL: {e}")
    return
```

### Docstrings
- Use triple double quotes (`"""`).
- First line is a brief summary.
- Follow with a longer description if needed.
- Include `Args:` and `Returns:` sections for clarity.

**Example:**
```python
def parse_course_url(url: str) -> Tuple[int, str, str]:
    """
    Extract course ID, language code, and GraphQL language enum from a DW URL.
    
    Args:
        url: The full course page URL (e.g., "https://learngerman.dw.com/es/nicos-weg/c-47994059")
    
    Returns:
        Tuple of (course_id, language_code, language_enum)
    
    Raises:
        ValueError: If the URL format is invalid
    """
```

### File Organization
- Source code resides in `src/`.
- Test files are in the root directory (a `tests/` directory exists but is currently empty).
- Output files are written to `output/` (configurable via `--output-dir`).
- Data files (JSON, logs) may be placed in `data/`.

### Project-Specific Patterns
- **GraphQL queries**: Defined as multi‑line strings inside methods.
- **Batch processing**: Use `range(0, total, batch_size)` loops for pagination.
- **Slug generation**: Use `slugify()` from `src.slug_utils` to create filenames.
- **URL parsing**: Use `parse_course_url()` from `src.url_parser` to extract IDs and language.
- **Module imports**: Some scripts add `src/` to `sys.path` to import local modules (e.g., `sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))`).

### Commit Messages
- Use imperative mood ("Add feature", "Fix bug", "Update docs").
- Keep the subject line under 50 characters.
- Provide a brief body explaining the **why** (not just the what).

## Cursor / Copilot Rules
No `.cursor/rules`, `.cursorrules`, or `.github/copilot-instructions.md` files exist in this repository.

## Notes for Agents
- This is a web‑scraping / API client project; be mindful of rate limiting and polite crawling.
- The codebase is relatively small and focused; avoid over‑engineering.
- When modifying existing code, mimic the surrounding style.
- If you add new dependencies, update `requirements.txt`.
- Before committing, run the relevant test scripts to ensure nothing is broken.

---
*Last updated: 2025‑02‑23*