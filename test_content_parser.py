#!/usr/bin/env python3
"""
Test the GrammarContentParser with real HTML samples.
"""
import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from content_parser import GrammarContentParser, parse_html_content

def test_with_sample_html():
    """Test parser with sample HTML from grammar lessons."""
    # Load a sample from the JSON file
    try:
        with open('grammar_lessons_20260219_111531.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return
    
    if 'grammar_lessons' not in data:
        print("No grammar_lessons in JSON")
        return
    
    grammar_lessons = data['grammar_lessons']
    print(f"Loaded {len(grammar_lessons)} grammar lessons")
    
    # Test with first few lessons that have HTML
    parser = GrammarContentParser()
    tested = 0
    
    for i, lesson in enumerate(grammar_lessons):
        if not lesson.get('text') or not lesson['text'].strip():
            continue
        
        html = lesson['text']
        title = lesson.get('title', f'Lesson {i}')
        
        print(f"\n{'='*80}")
        print(f"Testing: {title}")
        print(f"HTML length: {len(html)} chars")
        
        # Parse the HTML
        structured = parser.parse_html(html)
        
        # Show results
        print(f"\nOverview: {structured['overview'][:100]}..." if structured['overview'] else "No overview")
        print(f"Rules found: {len(structured['rules'])}")
        for j, rule in enumerate(structured['rules'][:3], 1):
            print(f"  {j}. {rule[:80]}...")
        
        print(f"Examples found: {len(structured['examples'])}")
        for j, example in enumerate(structured['examples'][:2], 1):
            print(f"  {j}. German: {example['german'][:50]}...")
            if example['context']:
                print(f"     Context: {example['context'][:50]}...")
        
        print(f"Tables found: {len(structured['tables'])}")
        for j, table in enumerate(structured['tables'][:2], 1):
            print(f"  {j}. Table: {table.get('row_count', 0)}x{table.get('col_count', 0)}")
            if table.get('markdown'):
                # Show first line of markdown table
                lines = table['markdown'].split('\n')
                if lines:
                    print(f"     First line: {lines[0][:60]}...")
        
        print(f"Exceptions found: {len(structured['exceptions'])}")
        print(f"Glossary terms found: {len(structured['glossary'])}")
        
        # Test markdown generation
        markdown = parser.html_to_structured_markdown(html)
        print(f"\nGenerated markdown length: {len(markdown)} chars")
        print(f"First 200 chars of markdown:")
        print(markdown[:200])
        
        tested += 1
        if tested >= 3:
            break
    
    print(f"\n{'='*80}")
    print(f"Tested {tested} lessons")
    
    # Also test the convenience functions
    print("\nTesting convenience functions...")
    if grammar_lessons and grammar_lessons[0].get('text'):
        sample_html = grammar_lessons[0]['text']
        structured = parse_html_content(sample_html)
        print(f"parse_html_content returned dict with keys: {list(structured.keys())}")
        
        markdown = parser.html_to_structured_markdown(sample_html)
        print(f"html_to_structured_markdown returned {len(markdown)} chars")

if __name__ == '__main__':
    test_with_sample_html()