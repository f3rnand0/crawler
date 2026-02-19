#!/usr/bin/env python3
"""
Test the enhanced exporter with existing JSON data (no network requests).
"""

import json
import os
import sys
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.enhanced_exporter import EnhancedExporter

def load_existing_data():
    """Load existing JSON data from output directory."""
    data_dir = Path("output")
    
    if not data_dir.exists():
        print("Error: output directory not found. Run full_export.py first.")
        return None, None
    
    # Load course structure
    course_json = data_dir / "course_spanish_structure.json"
    if not course_json.exists():
        print(f"Error: {course_json} not found")
        return None, None
    
    with open(course_json, 'r', encoding='utf-8') as f:
        course_structure = json.load(f)
    
    # Load grammar data
    grammar_json = data_dir / "grammar_spanish.json"
    if not grammar_json.exists():
        print(f"Error: {grammar_json} not found")
        return course_structure, None
    
    with open(grammar_json, 'r', encoding='utf-8') as f:
        grammar_data = json.load(f)
    
    print(f"Loaded course structure: {len(course_structure.get('lessons', []))} lessons")
    print(f"Loaded grammar data: {len(grammar_data.get('grammar_lessons', []))} grammar lessons")
    
    return course_structure, grammar_data

def test_flat_grammar_export():
    """Test flat grammar export with existing data."""
    print("\nTesting flat grammar export...")
    
    course_structure, grammar_data = load_existing_data()
    if not grammar_data:
        return False
    
    # Create temporary directory for output
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Using temporary directory: {temp_dir}")
        
        # Initialize exporter
        exporter = EnhancedExporter()
        
        # Test flat grammar export
        try:
            stats = exporter.export_flat_grammar(grammar_data, temp_dir, "es")
            print(f"  ✓ Flat grammar export succeeded")
            print(f"    Files created: {stats.get('total_grammar_files', 0)}")
            
            # Check if files were created
            grammar_dir = Path(temp_dir) / "grammar"
            if grammar_dir.exists():
                md_files = list(grammar_dir.glob("*.md"))
                print(f"    Markdown files: {len(md_files)}")
                
                # Show first few files
                for i, md_file in enumerate(md_files[:5]):
                    print(f"      {md_file.name}")
                if len(md_files) > 5:
                    print(f"      ... and {len(md_files) - 5} more")
                
                # Check index file
                index_file = grammar_dir / "INDEX.md"
                if index_file.exists():
                    print(f"    Index file created: {index_file.name}")
                else:
                    print(f"    Warning: INDEX.md not created")
            
            return True
            
        except Exception as e:
            print(f"  ✗ Flat grammar export failed: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_lesson_files_export():
    """Test lesson files export with existing data."""
    print("\nTesting lesson files export...")
    
    course_structure, grammar_data = load_existing_data()
    if not course_structure or not grammar_data:
        return False
    
    # Create temporary directory for output
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Using temporary directory: {temp_dir}")
        
        # Initialize exporter
        exporter = EnhancedExporter()
        
        # Test lesson files export
        try:
            stats = exporter.export_lesson_files(course_structure, grammar_data, temp_dir, "es")
            print(f"  ✓ Lesson files export succeeded")
            print(f"    Files created: {stats.get('total_lesson_files', 0)}")
            
            # Check if files were created
            lessons_dir = Path(temp_dir) / "lessons"
            if lessons_dir.exists():
                md_files = list(lessons_dir.glob("*.md"))
                print(f"    Markdown files: {len(md_files)}")
                
                # Show first few files
                for i, md_file in enumerate(md_files[:5]):
                    print(f"      {md_file.name}")
                if len(md_files) > 5:
                    print(f"      ... and {len(md_files) - 5} more")
            
            return True
            
        except Exception as e:
            print(f"  ✗ Lesson files export failed: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_course_structure_markdown():
    """Test course structure markdown generation."""
    print("\nTesting course structure markdown generation...")
    
    course_structure, grammar_data = load_existing_data()
    if not course_structure or not grammar_data:
        return False
    
    # Create temporary directory for output
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Using temporary directory: {temp_dir}")
        
        # Initialize exporter
        exporter = EnhancedExporter()
        
        # Test course structure markdown
        try:
            md_path = exporter.export_course_structure_markdown(
                course_structure, grammar_data, temp_dir, "es"
            )
            print(f"  ✓ Course structure markdown succeeded")
            print(f"    File: {md_path}")
            
            # Check if file exists and has content
            if os.path.exists(md_path):
                with open(md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"    File size: {len(content)} characters")
                print(f"    First 200 chars: {content[:200]}...")
            
            return True
            
        except Exception as e:
            print(f"  ✗ Course structure markdown failed: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    print("=" * 60)
    print("Enhanced Exporter Integration Test")
    print("Using existing JSON data (no network requests)")
    print("=" * 60)
    
    # Check if data exists
    if not Path("output").exists():
        print("\nError: output directory not found.")
        print("Please run full_export.py first to generate test data.")
        print("\nTo generate test data:")
        print("  cd /Users/fernando/ws/crawler")
        print("  python src/full_export.py")
        return
    
    # Run tests
    tests_passed = 0
    tests_total = 3
    
    if test_flat_grammar_export():
        tests_passed += 1
    
    if test_lesson_files_export():
        tests_passed += 1
    
    if test_course_structure_markdown():
        tests_passed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {tests_passed}/{tests_total} tests passed")
    print("=" * 60)
    
    if tests_passed == tests_total:
        print("\nAll tests passed! The enhanced exporter works correctly.")
        print("\nTo run the full CLI tool:")
        print("  python dw_extract.py --url https://learngerman.dw.com/es/nicos-weg/c-47994059 --output-dir test_output")
    else:
        print("\nSome tests failed. Check the errors above.")

if __name__ == "__main__":
    main()