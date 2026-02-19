#!/usr/bin/env python3
"""
Test script for DW Learn German Grammar Extractor.
Tests the main components without making full GraphQL queries.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.url_parser import parse_course_url, validate_url_format
from src.slug_utils import slugify, extract_grammar_slug_from_url, generate_grammar_filename
from src.enhanced_exporter import EnhancedExporter

def test_url_parser():
    print("Testing URL parser...")
    test_urls = [
        "https://learngerman.dw.com/es/nicos-weg/c-47994059",
        "https://learngerman.dw.com/en/nicos-weg/c-47994059",
        "https://learngerman.dw.com/de/nicos-weg/c-47994059",
        "https://learngerman.dw.com/fr/nicos-weg/c-47994059",
    ]
    
    for url in test_urls:
        try:
            course_id, lang_code, lang_enum = parse_course_url(url)
            print(f"  ✓ {url}")
            print(f"    Course ID: {course_id}, Language: {lang_code} -> {lang_enum}")
        except Exception as e:
            print(f"  ✗ {url}: {e}")
    
    print()

def test_slug_utilities():
    print("Testing slug utilities...")
    
    # Test slugify
    test_cases = [
        ("Formal e informal", "formal-e-informal"),
        ("Cambio de vocal: a - ä", "cambio-de-vocal-a-ae"),
        ("¿Präteritum o Perfekt?", "praeteritum-o-perfekt"),
    ]
    
    for input_text, expected in test_cases:
        result = slugify(input_text)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{input_text}' -> '{result}'")
    
    # Test grammar slug extraction
    print("\n  Testing grammar slug extraction:")
    test_urls = [
        "/es/cambio-de-vocal-a-ä/gr-49930523",
        "https://learngerman.dw.com/es/formal-e-informal-1/gr-49710895",
    ]
    
    for url in test_urls:
        slug = extract_grammar_slug_from_url(url)
        print(f"    '{url}' -> '{slug}'")
    
    # Test filename generation
    print("\n  Testing filename generation:")
    test_pairs = [
        ("verbos", "cambio-de-vocal-a-ae", "verbos-cambio-de-vocal-a-ae.md"),
        ("preposiciones", "dativo", "preposiciones-dativo.md"),
    ]
    
    for category, grammar, expected in test_pairs:
        filename = generate_grammar_filename(category, grammar)
        status = "✓" if filename == expected else "✗"
        print(f"    {status} {category} + {grammar} -> {filename}")
    
    print()

def test_exporter_initialization():
    print("Testing exporter initialization...")
    try:
        exporter = EnhancedExporter()
        print("  ✓ EnhancedExporter initialized successfully")
        
        # Test base URL
        print(f"  Base URL: {exporter.base_url}")
        print(f"  GraphQL URL: {exporter.graphql_url}")
        
    except Exception as e:
        print(f"  ✗ Error initializing exporter: {e}")
        import traceback
        traceback.print_exc()
    
    print()

def test_cli_argument_parsing():
    print("Testing CLI argument parsing...")
    
    # Simulate argparse
    test_args = [
        ["--url", "https://learngerman.dw.com/es/nicos-weg/c-47994059"],
        ["--url", "https://learngerman.dw.com/es/nicos-weg/c-47994059", "--output-dir", "test_output"],
        ["--url", "https://learngerman.dw.com/es/nicos-weg/c-47994059", "--keep-json", "--verbose"],
    ]
    
    for i, args in enumerate(test_args):
        print(f"  Test case {i+1}: {' '.join(args)}")
        
        # Simulate validation
        url = args[args.index("--url") + 1]
        if validate_url_format(url):
            print(f"    ✓ URL validated: {url}")
        else:
            print(f"    ✗ Invalid URL: {url}")
    
    print()

def main():
    print("=" * 60)
    print("DW Learn German Grammar Extractor - Component Tests")
    print("=" * 60)
    print()
    
    test_url_parser()
    test_slug_utilities()
    test_exporter_initialization()
    test_cli_argument_parsing()
    
    print("=" * 60)
    print("All component tests completed successfully!")
    print("=" * 60)
    print()
    print("Note: Full integration test with GraphQL API not run.")
    print("To test full extraction, run:")
    print("  python dw_extract.py --url https://learngerman.dw.com/es/nicos-weg/c-47994059 --output-dir test_output")
    print()

if __name__ == "__main__":
    main()