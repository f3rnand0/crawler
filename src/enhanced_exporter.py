import os
import json
import html2text
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse

from full_export import FullCourseExporter
from slug_utils import slugify, extract_grammar_slug_from_url, extract_lesson_slug_from_url, generate_grammar_filename
from url_parser import parse_course_url

class EnhancedExporter(FullCourseExporter):
    """Enhanced exporter for flat grammar organization and markdown generation."""
    
    def export_course_from_url(self, url: str, output_dir: str = "output") -> Dict[str, Any]:
        """
        Main export function: parse URL and export course data.
        
        Args:
            url: Course page URL
            output_dir: Root output directory
        
        Returns:
            Dictionary with export results and statistics
        """
        print(f"Parsing URL: {url}")
        
        try:
            # Parse URL to get course ID and language
            course_id, lang_code, lang_enum = parse_course_url(url)
        except Exception as e:
            print(f"Error parsing URL: {e}")
            raise
        
        print(f"Course ID: {course_id}")
        print(f"Language code: {lang_code}")
        print(f"Language enum: {lang_enum}")
        
        # Create language-specific output directory
        lang_output_dir = os.path.join(output_dir, lang_code)
        os.makedirs(lang_output_dir, exist_ok=True)
        
        # Export course structure (includes grammar details)
        print(f"\nExporting course structure...")
        course_structure = self.export_course_structure(course_id, lang_enum, lang_output_dir)
        
        if not course_structure:
            print("Failed to export course structure")
            return {}
        
        # Export grammar overview for categories
        print(f"\nExporting grammar overview...")
        grammar_data = self.export_grammar(lang_enum, lang_output_dir)
        
        # Generate flat grammar markdown files
        print(f"\nGenerating flat grammar markdown files...")
        grammar_stats = self.export_flat_grammar(grammar_data, lang_output_dir, lang_code)
        
        # Generate lesson markdown files
        print(f"\nGenerating lesson markdown files...")
        lesson_stats = self.export_lesson_files(course_structure, grammar_data, lang_output_dir, lang_code)
        
        # Generate course structure markdown
        print(f"\nGenerating course structure markdown...")
        course_md_path = self.export_course_structure_markdown(
            course_structure, grammar_data, lang_output_dir, lang_code
        )
        
        # Compile results
        results = {
            "course_id": course_id,
            "language_code": lang_code,
            "language_enum": lang_enum,
            "course_structure": course_structure,
            "grammar_data": grammar_data,
            "output_directory": lang_output_dir,
            "stats": {
                "lessons": course_structure.get("stats", {}).get("total_lessons", 0),
                "lessons_with_grammar": course_structure.get("stats", {}).get("lessons_with_grammar", 0),
                "grammar_lessons": grammar_stats.get("total_grammar_files", 0),
                "lesson_files": lesson_stats.get("total_lesson_files", 0),
            }
        }
        
        print(f"\nExport completed successfully!")
        print(f"Output directory: {lang_output_dir}")
        print(f"Lessons: {results['stats']['lessons']}")
        print(f"Lessons with grammar: {results['stats']['lessons_with_grammar']}")
        print(f"Grammar files: {results['stats']['grammar_lessons']}")
        print(f"Lesson files: {results['stats']['lesson_files']}")
        
        return results
    
    def export_flat_grammar(self, grammar_data: Dict[str, Any], output_dir: str, lang_code: str) -> Dict[str, Any]:
        """
        Export grammar lessons as flat markdown files with category prefixes.
        
        Args:
            grammar_data: Grammar data from export_grammar
            output_dir: Language-specific output directory
            lang_code: Language code for naming
        
        Returns:
            Statistics about exported files
        """
        grammar_dir = os.path.join(output_dir, "grammar")
        os.makedirs(grammar_dir, exist_ok=True)
        
        # Initialize HTML to markdown converter
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        h.body_width = 0  # No line wrapping
        
        # Get category mapping
        category_map = {}
        for category in grammar_data.get("categories", []):
            category_slug = slugify(category.get("name", ""))
            category_map[category["slug"]] = {
                "name": category["name"],
                "slug": category_slug,
                "grammar_ids": [g["id"] for g in category.get("grammar_lessons", [])]
            }
        
        # Create a mapping from grammar ID to category
        grammar_to_category = {}
        for category_slug, cat_info in category_map.items():
            for grammar_id in cat_info["grammar_ids"]:
                grammar_to_category[grammar_id] = cat_info
        
        # Export all grammar lessons
        grammar_lessons = grammar_data.get("grammar_lessons", [])
        exported_files = 0
        skipped_files = 0
        
        for lesson in grammar_lessons:
            grammar_id = lesson.get("id")
            grammar_title = lesson.get("title", "")
            grammar_url = lesson.get("url", "")
            grammar_text = lesson.get("text", "")
            
            # Get category information
            cat_info = grammar_to_category.get(grammar_id)
            if not cat_info:
                # Try to find category from dkGrammarCategory
                category_slug = "uncategorized"
                category_name = "Uncategorized"
            else:
                category_slug = cat_info["slug"]
                category_name = cat_info["name"]
            
            # Extract grammar slug from URL
            grammar_slug = extract_grammar_slug_from_url(grammar_url)
            
            # Generate filename
            filename = generate_grammar_filename(category_slug, grammar_slug)
            filepath = os.path.join(grammar_dir, filename)
            
            # Convert HTML to markdown
            text_md = h.handle(grammar_text) if grammar_text else ""
            
            # Build markdown content
            md_content = f"# {grammar_title}\n\n"
            md_content += f"**URL:** https://learngerman.dw.com{grammar_url}\n\n"
            md_content += f"**ID:** {grammar_id}\n\n"
            md_content += f"**Category:** {category_name}\n\n"
            
            if lesson.get("teaser"):
                md_content += f"**Teaser:** {lesson['teaser']}\n\n"
            
            md_content += "## Content\n\n"
            md_content += text_md
            
            # Add metadata at the end
            md_content += "\n\n---\n"
            md_content += f"*Category: {category_name}*  \n"
            md_content += f"*Grammar ID: {grammar_id}*  \n"
            md_content += f"*Source URL: https://learngerman.dw.com{grammar_url}*\n"
            
            # Write file
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(md_content)
                exported_files += 1
            except Exception as e:
                print(f"  Error writing {filename}: {e}")
                skipped_files += 1
        
        # Create grammar index file
        self._create_grammar_index(grammar_dir, grammar_lessons, grammar_to_category, lang_code)
        
        print(f"  Exported {exported_files} grammar files to {grammar_dir}")
        if skipped_files > 0:
            print(f"  Skipped {skipped_files} files due to errors")
        
        return {
            "total_grammar_files": exported_files,
            "skipped_files": skipped_files,
            "grammar_directory": grammar_dir,
        }
    
    def _create_grammar_index(self, grammar_dir: str, grammar_lessons: List[Dict[str, Any]], 
                              grammar_to_category: Dict[int, Dict[str, Any]], lang_code: str):
        """Create index file listing all grammar lessons."""
        index_path = os.path.join(grammar_dir, "INDEX.md")
        
        # Group by category
        categories = {}
        for lesson in grammar_lessons:
            grammar_id = lesson.get("id")
            cat_info = grammar_to_category.get(grammar_id, {"name": "Uncategorized", "slug": "uncategorized"})
            category_name = cat_info["name"]
            
            if category_name not in categories:
                categories[category_name] = []
            
            categories[category_name].append(lesson)
        
        # Write index file
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("# Grammar Lessons Index\n\n")
            f.write(f"Total grammar lessons: {len(grammar_lessons)}\n\n")
            
            # List by category
            for category_name, lessons in sorted(categories.items()):
                f.write(f"## {category_name}\n\n")
                f.write(f"Count: {len(lessons)}\n\n")
                
                for lesson in sorted(lessons, key=lambda x: x.get("title", "")):
                    title = lesson.get("title", "")
                    grammar_id = lesson.get("id")
                    grammar_slug = extract_grammar_slug_from_url(lesson.get("url", ""))
                    category_slug = slugify(category_name)
                    filename = generate_grammar_filename(category_slug, grammar_slug)
                    
                    f.write(f"- [{title}]({filename})\n")
                
                f.write("\n")
    
    def export_lesson_files(self, course_structure: Dict[str, Any], grammar_data: Dict[str, Any], 
                           output_dir: str, lang_code: str) -> Dict[str, Any]:
        """
        Export individual lesson markdown files.
        
        Args:
            course_structure: Course structure data
            grammar_data: Grammar data for category mapping
            output_dir: Language-specific output directory
            lang_code: Language code for naming
        
        Returns:
            Statistics about exported files
        """
        lessons_dir = os.path.join(output_dir, "lessons")
        os.makedirs(lessons_dir, exist_ok=True)
        
        # Create mapping from grammar ID to filename
        grammar_file_map = self._create_grammar_file_map(grammar_data, output_dir)
        
        # Create mapping from lesson ID to grammar lessons
        lesson_grammar_map = {}
        grammar_mapping = course_structure.get("grammar_mapping", [])
        
        for mapping in grammar_mapping:
            lesson_id = mapping.get("lesson_id")
            grammar_id = mapping.get("grammar_id")
            grammar_title = mapping.get("grammar_title", "")
            
            if lesson_id not in lesson_grammar_map:
                lesson_grammar_map[lesson_id] = []
            
            # Find grammar filename
            grammar_filename = grammar_file_map.get(grammar_id, "")
            if grammar_filename:
                lesson_grammar_map[lesson_id].append({
                    "id": grammar_id,
                    "title": grammar_title,
                    "filename": grammar_filename,
                })
        
        # Export each lesson
        lessons = course_structure.get("lessons", [])
        exported_files = 0
        
        for lesson in lessons:
            lesson_id = lesson.get("id")
            lesson_title = lesson.get("title", "")
            lesson_url = lesson.get("url", "")
            
            # Extract lesson slug from URL
            lesson_slug = extract_lesson_slug_from_url(lesson_url)
            if not lesson_slug:
                lesson_slug = slugify(lesson_title)
            
            # Create filename
            filename = f"{lesson_slug}.md"
            filepath = os.path.join(lessons_dir, filename)
            
            # Get grammar lessons for this lesson
            grammar_lessons = lesson_grammar_map.get(lesson_id, [])
            
            # Build markdown content
            md_content = f"# {lesson_title}\n\n"
            md_content += f"**URL:** https://learngerman.dw.com{lesson_url}\n\n"
            md_content += f"**ID:** {lesson_id}\n\n"
            
            # Add statistics
            md_content += f"**Grammar lessons:** {len(grammar_lessons)}\n"
            md_content += f"**Vocabulary items:** {lesson.get('vocabulary_count', 0)}\n"
            md_content += f"**Regional studies:** {lesson.get('regional_studies_count', 0)}\n\n"
            
            # Add grammar section if any
            if grammar_lessons:
                md_content += "## Grammar Lessons\n\n"
                for grammar in grammar_lessons:
                    md_content += f"- [{grammar['title']}](../grammar/{grammar['filename']})\n"
                md_content += "\n"
            
            # Add navigation placeholder
            md_content += "---\n"
            md_content += "*This lesson is part of the course*\n\n"
            
            # Write file
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(md_content)
                exported_files += 1
            except Exception as e:
                print(f"  Error writing lesson file {filename}: {e}")
        
        # Create lessons index file
        self._create_lessons_index(lessons_dir, lessons, lesson_grammar_map)
        
        print(f"  Exported {exported_files} lesson files to {lessons_dir}")
        
        return {
            "total_lesson_files": exported_files,
            "lessons_directory": lessons_dir,
        }
    
    def _create_grammar_file_map(self, grammar_data: Dict[str, Any], output_dir: str) -> Dict[int, str]:
        """
        Create mapping from grammar ID to filename.
        
        Args:
            grammar_data: Grammar data
            output_dir: Output directory
        
        Returns:
            Dictionary mapping grammar_id -> filename
        """
        grammar_file_map = {}
        
        for category in grammar_data.get("categories", []):
            category_slug = slugify(category.get("name", ""))
            
            for lesson in category.get("grammar_lessons", []):
                grammar_id = lesson.get("id")
                grammar_slug = extract_grammar_slug_from_url(lesson.get("url", ""))
                filename = generate_grammar_filename(category_slug, grammar_slug)
                grammar_file_map[grammar_id] = filename
        
        return grammar_file_map
    
    def _create_lessons_index(self, lessons_dir: str, lessons: List[Dict[str, Any]], 
                             lesson_grammar_map: Dict[int, List[Dict[str, Any]]]):
        """Create index file listing all lessons."""
        index_path = os.path.join(lessons_dir, "INDEX.md")
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("# Lessons Index\n\n")
            f.write(f"Total lessons: {len(lessons)}\n\n")
            
            # Sort lessons by title
            sorted_lessons = sorted(lessons, key=lambda x: x.get("title", ""))
            
            for lesson in sorted_lessons:
                lesson_id = lesson.get("id")
                lesson_title = lesson.get("title", "")
                lesson_slug = extract_lesson_slug_from_url(lesson.get("url", ""))
                if not lesson_slug:
                    lesson_slug = slugify(lesson_title)
                
                filename = f"{lesson_slug}.md"
                grammar_count = len(lesson_grammar_map.get(lesson_id, []))
                
                f.write(f"## {lesson_title}\n\n")
                f.write(f"- **ID:** {lesson_id}\n")
                f.write(f"- **Grammar lessons:** {grammar_count}\n")
                f.write(f"- **Vocabulary:** {lesson.get('vocabulary_count', 0)}\n")
                f.write(f"- **Regional studies:** {lesson.get('regional_studies_count', 0)}\n")
                f.write(f"- [View lesson]({filename})\n\n")
    
    def export_course_structure_markdown(self, course_structure: Dict[str, Any], 
                                         grammar_data: Dict[str, Any], 
                                         output_dir: str, lang_code: str) -> str:
        """
        Export course structure as human-readable markdown file.
        
        Args:
            course_structure: Course structure data
            grammar_data: Grammar data
            output_dir: Language-specific output directory
            lang_code: Language code
        
        Returns:
            Path to generated markdown file
        """
        course_md_path = os.path.join(output_dir, "course_structure.md")
        
        course = course_structure.get("course", {})
        lessons = course_structure.get("lessons", [])
        stats = course_structure.get("stats", {})
        
        # Count grammar lessons by category
        category_counts = {}
        for category in grammar_data.get("categories", []):
            category_name = category.get("name", "Uncategorized")
            grammar_count = len(category.get("grammar_lessons", []))
            category_counts[category_name] = grammar_count
        
        with open(course_md_path, 'w', encoding='utf-8') as f:
            # Course header
            f.write(f"# {course.get('title', 'Course')}\n\n")
            f.write(f"**Language:** {lang_code} ({course.get('language', 'Unknown')})\n")
            f.write(f"**Course ID:** {course.get('id', 'N/A')}\n")
            f.write(f"**URL:** https://learngerman.dw.com{course.get('url', '')}\n\n")
            
            # Statistics
            f.write("## Statistics\n\n")
            f.write(f"- **Total lessons:** {stats.get('total_lessons', 0)}\n")
            f.write(f"- **Lessons with grammar:** {stats.get('lessons_with_grammar', 0)}\n")
            f.write(f"- **Unique grammar lessons:** {stats.get('unique_grammar_lessons', 0)}\n\n")
            
            # Grammar by category
            f.write("## Grammar by Category\n\n")
            for category_name, count in sorted(category_counts.items()):
                f.write(f"- **{category_name}:** {count} lessons\n")
            f.write("\n")
            
            # Lessons table
            f.write("## Lessons\n\n")
            f.write("| Lesson | Grammar | Vocabulary | Regional Studies |\n")
            f.write("|--------|---------|------------|------------------|\n")
            
            for lesson in lessons:
                lesson_title = lesson.get("title", "")
                lesson_slug = extract_lesson_slug_from_url(lesson.get("url", ""))
                if not lesson_slug:
                    lesson_slug = slugify(lesson_title)
                
                grammar_count = lesson.get("grammar_count", 0)
                vocab_count = lesson.get("vocabulary_count", 0)
                regional_count = lesson.get("regional_studies_count", 0)
                
                # Create link if there's a lesson file
                if grammar_count > 0:
                    lesson_link = f"[{lesson_title}](lessons/{lesson_slug}.md)"
                else:
                    lesson_link = lesson_title
                
                f.write(f"| {lesson_link} | {grammar_count} | {vocab_count} | {regional_count} |\n")
            
            f.write("\n")
            
            # Grammar mapping
            f.write("## Grammar Mapping\n\n")
            f.write("Each lesson contains links to its grammar lessons in the `grammar/` directory.\n\n")
            
            # Instructions
            f.write("## File Structure\n\n")
            f.write("```\n")
            f.write(f"{output_dir}/\n")
            f.write("├── course_structure.md          # This file\n")
            f.write("├── grammar/                    # All grammar lessons\n")
            f.write("│   ├── INDEX.md                # Grammar index\n")
            f.write("│   ├── category1-lesson1.md\n")
            f.write("│   └── ...\n")
            f.write("└── lessons/                    # Individual lesson files\n")
            f.write("    ├── INDEX.md                # Lessons index\n")
            f.write("    ├── lesson1.md\n")
            f.write("    └── ...\n")
            f.write("```\n\n")
            
            # Usage notes
            f.write("## Usage\n\n")
            f.write("1. Browse grammar lessons in the `grammar/` directory\n")
            f.write("2. View individual lessons in the `lessons/` directory\n")
            f.write("3. Each lesson file links to its grammar lessons\n")
            f.write("4. Grammar files are named `category-grammar-slug.md`\n")
        
        print(f"  Course structure markdown saved to {course_md_path}")
        return course_md_path

def main():
    """Test the enhanced exporter."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python enhanced_exporter.py <course_url> [output_dir]")
        print("Example: python enhanced_exporter.py https://learngerman.dw.com/es/nicos-weg/c-47994059 output")
        sys.exit(1)
    
    url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
    
    exporter = EnhancedExporter()
    
    try:
        results = exporter.export_course_from_url(url, output_dir)
        if results:
            print("\nExport successful!")
        else:
            print("\nExport failed.")
    except Exception as e:
        print(f"\nError during export: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()