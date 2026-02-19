#!/usr/bin/env python3
"""
DW Learn German Grammar Extractor

A command-line tool to extract grammar lessons from DW Learn German courses.
Automatically detects language from URL and exports markdown files organized by category.
"""

import argparse
import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.enhanced_exporter import EnhancedExporter
from src.url_parser import validate_url_format

def main():
    parser = argparse.ArgumentParser(
        description="Extract grammar lessons from DW Learn German courses",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --url "https://learngerman.dw.com/es/nicos-weg/c-47994059"
  %(prog)s --url "https://learngerman.dw.com/es/nicos-weg/c-47994059" --output-dir "german_lessons"
  %(prog)s --url "https://learngerman.dw.com/en/nicos-weg/c-47994059" --keep-json
  
Output Structure:
  {output_dir}/{language_code}/
  ├── course_structure.md          # Course overview
  ├── grammar/                    # All grammar lessons (flat directory)
  │   ├── verbos-cambio-de-vocal.md
  │   ├── preposiciones-dativo.md
  │   └── ...
  └── lessons/                    # Individual lesson files
      ├── hallo.md
      ├── tschüss.md
      └── ...
        """
    )
    
    # Required arguments
    parser.add_argument(
        "--url",
        required=True,
        help="Course page URL (e.g., https://learngerman.dw.com/es/nicos-weg/c-47994059)"
    )
    
    # Optional arguments
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Output directory (default: output)"
    )
    
    parser.add_argument(
        "--batch-size",
        type=int,
        default=20,
        help="GraphQL batch size for fetching data (default: 20)"
    )
    
    parser.add_argument(
        "--keep-json",
        action="store_true",
        help="Keep intermediate JSON files (default: False)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output (default: False)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    args = parser.parse_args()
    
    # Validate URL
    if not validate_url_format(args.url):
        print(f"Error: Invalid URL format: {args.url}")
        print("URL should be in format: https://learngerman.dw.com/{lang}/{course-slug}/c-{course-id}")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("DW Learn German Grammar Extractor")
    print("=" * 60)
    print(f"URL: {args.url}")
    print(f"Output directory: {output_dir}")
    print(f"Batch size: {args.batch_size}")
    print(f"Keep JSON files: {args.keep_json}")
    print("-" * 60)
    
    try:
        # Initialize exporter
        exporter = EnhancedExporter()
        
        # Export course
        results = exporter.export_course_from_url(args.url, str(output_dir))
        
        if not results:
            print("\nError: Export failed. No results returned.")
            sys.exit(1)
        
        # Clean up JSON files if not keeping them
        if not args.keep_json:
            lang_dir = results.get("output_directory", "")
            if lang_dir and os.path.exists(lang_dir):
                json_files = list(Path(lang_dir).glob("*.json"))
                for json_file in json_files:
                    try:
                        json_file.unlink()
                        if args.verbose:
                            print(f"Removed JSON file: {json_file}")
                    except Exception as e:
                        print(f"Warning: Could not remove {json_file}: {e}")
        
        print("\n" + "=" * 60)
        print("Export completed successfully!")
        print("=" * 60)
        
        # Print summary
        stats = results.get("stats", {})
        print(f"\nSummary:")
        print(f"  Course: {results.get('language_code', 'unknown')}")
        print(f"  Lessons: {stats.get('lessons', 0)}")
        print(f"  Lessons with grammar: {stats.get('lessons_with_grammar', 0)}")
        print(f"  Grammar files: {stats.get('grammar_lessons', 0)}")
        print(f"  Lesson files: {stats.get('lesson_files', 0)}")
        print(f"\nOutput directory: {results.get('output_directory', '')}")
        
        # Show file structure
        if os.path.exists(results.get("output_directory", "")):
            print("\nGenerated files:")
            output_path = Path(results["output_directory"])
            
            # List top-level files
            for item in output_path.iterdir():
                if item.is_file():
                    print(f"  {item.name}")
                elif item.is_dir():
                    print(f"  {item.name}/")
                    # List first few files in directories
                    dir_items = list(item.iterdir())
                    for dir_item in dir_items[:5]:
                        print(f"    {dir_item.name}")
                    if len(dir_items) > 5:
                        print(f"    ... and {len(dir_items) - 5} more")
        
        print("\n" + "=" * 60)
        
    except KeyboardInterrupt:
        print("\n\nExport interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\nError during export: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()