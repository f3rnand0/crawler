#!/usr/bin/env python3
"""
Analyze HTML structure in grammar lessons to understand parsing needs.
"""
import json
from bs4 import BeautifulSoup
import re

def analyze_html_sample():
    """Analyze a sample of HTML content from the JSON file."""
    try:
        with open('grammar_lessons_20260219_111531.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return
    
    print(f"JSON structure keys: {list(data.keys())}")
    
    if 'grammar_lessons' in data:
        grammar_lessons = data['grammar_lessons']
        print(f"Total grammar lessons: {len(grammar_lessons)}")
        
        # Analyze first 3 items with text
        analyzed = 0
        for i, item in enumerate(grammar_lessons):
            if not isinstance(item, dict):
                continue
                
            if 'text' in item and item['text'] and item['text'].strip():
                html = item['text']
                title = item.get('title', 'No title')
                
                print(f"\n{'='*60}")
                print(f"Analyzing: {title}")
                print(f"HTML length: {len(html)} chars")
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')
                
                # Count tags
                tags = {}
                for tag in soup.find_all():
                    tag_name = tag.name
                    tags[tag_name] = tags.get(tag_name, 0) + 1
                
                print(f"Tags found: {dict(sorted(tags.items(), key=lambda x: x[1], reverse=True)[:10])}")
                
                # Look for specific structures
                tables = soup.find_all('table')
                print(f"Tables: {len(tables)}")
                if tables:
                    # Show first table structure
                    table = tables[0]
                    print(f"Table structure - Rows: {len(table.find_all('tr'))}")
                    print(f"First row cells: {len(table.find_all('tr')[0].find_all(['td', 'th']))}")
                
                # Look for examples (italic text)
                italics = soup.find_all('em')
                print(f"Italic elements (<em>): {len(italics)}")
                if italics:
                    print(f"First italic: {italics[0].get_text()[:100]}...")
                
                # Look for paragraphs
                paragraphs = soup.find_all('p')
                print(f"Paragraphs: {len(paragraphs)}")
                if paragraphs:
                    print(f"First paragraph: {paragraphs[0].get_text()[:150]}...")
                
                # Look for lists
                lists = soup.find_all(['ul', 'ol'])
                print(f"Lists (ul/ol): {len(lists)}")
                
                # Look for "Términos gramaticales" section
                text_lower = html.lower()
                if 'términos' in text_lower or 'glosario' in text_lower:
                    print("Found glossary/terms section")
                
                # Show raw HTML preview
                print(f"\nHTML preview (first 300 chars):")
                print(html[:300].replace('\n', ' '))
                
                analyzed += 1
                if analyzed >= 3:
                    break
    
    print(f"\n{'='*60}")
    print("Analysis complete")

if __name__ == '__main__':
    analyze_html_sample()