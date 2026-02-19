import json
import os
from typing import Dict, List, Any
from export_grammar import DWGrammarExporter

class FullCourseExporter(DWGrammarExporter):
    def get_course_with_lessons(self, course_id: int, lang: str = "SPANISH") -> Dict[str, Any]:
        """Get course with all lessons."""
        query = """
        query GetCourseWithLessons($id: Int!, $lang: Language!) {
          content(id: $id, lang: $lang) {
            ... on Course {
              id
              title
              namedUrl
              lessons {
                id
                title
                namedUrl
              }
            }
          }
        }
        """
        variables = {"id": course_id, "lang": lang}
        result = self.query(query, variables)
        if "errors" in result:
            print(f"GraphQL errors: {result['errors']}")
            return {}
        return result.get("data", {}).get("content", {})
    
    def get_lessons_with_knowledges_batch(self, lesson_ids: List[int], lang: str = "SPANISH") -> Dict[int, Dict[str, Any]]:
        """Batch fetch lessons with their knowledges."""
        keys = [{"id": lid, "type": "LESSON"} for lid in lesson_ids]
        query = """
        query BatchGetLessons($keys: [ContentKeyInput!]!, $lang: Language!) {
          contents(keys: $keys, lang: $lang) {
            ... on Lesson {
              id
              title
              namedUrl
              knowledges {
                id
                title
                namedUrl
                dkGrammar
                dkGrammarCategory
              }
            }
          }
        }
        """
        variables = {"keys": keys, "lang": lang}
        result = self.query(query, variables)
        if "errors" in result:
            print(f"GraphQL errors: {result['errors']}")
            return {}
        
        contents = result.get("data", {}).get("contents", [])
        return {item['id']: item for item in contents}
    
    def export_course_structure(self, course_id: int = 47994059, lang: str = "SPANISH", output_dir: str = "output"):
        """Export full course structure with grammar mapping."""
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Fetching course {course_id}...")
        course = self.get_course_with_lessons(course_id, lang)
        if not course:
            print("Failed to fetch course")
            return
        
        print(f"Course: {course['title']}")
        lessons = course.get('lessons', [])
        print(f"Total lessons: {len(lessons)}")
        
        # Batch fetch lessons with knowledges
        lesson_ids = [lesson['id'] for lesson in lessons]
        print(f"Fetching knowledges for {len(lesson_ids)} lessons...")
        
        batch_size = 20
        lessons_with_knowledge = {}
        for i in range(0, len(lesson_ids), batch_size):
            batch = lesson_ids[i:i+batch_size]
            print(f"  Batch {i//batch_size + 1}/{(len(lesson_ids)-1)//batch_size + 1}")
            batch_result = self.get_lessons_with_knowledges_batch(batch, lang)
            lessons_with_knowledge.update(batch_result)
        
        # Extract grammar knowledges
        grammar_lesson_map = {}
        vocabulary_lesson_map = {}
        regional_studies_map = {}
        
        for lesson_id, lesson_data in lessons_with_knowledge.items():
            knowledges = lesson_data.get('knowledges', [])
            grammar = []
            vocabulary = []
            regional = []
            
            for knowledge in knowledges:
                url = knowledge.get('namedUrl', '')
                if '/gr-' in url:
                    grammar.append(knowledge)
                elif '/lv-' in url:
                    vocabulary.append(knowledge)
                elif '/rs-' in url:
                    regional.append(knowledge)
            
            if grammar:
                grammar_lesson_map[lesson_id] = {
                    'lesson_title': lesson_data.get('title'),
                    'lesson_url': lesson_data.get('namedUrl'),
                    'grammar_knowledges': grammar,
                }
        
        print(f"\nLessons with grammar: {len(grammar_lesson_map)}")
        
        # Get all grammar IDs from map
        grammar_ids = set()
        for lesson_info in grammar_lesson_map.values():
            for knowledge in lesson_info['grammar_knowledges']:
                grammar_ids.add(knowledge['id'])
        
        print(f"Unique grammar lessons from course: {len(grammar_ids)}")
        
        # Fetch grammar details
        print(f"Fetching grammar details...")
        grammar_details = self.get_knowledge_details_batch(list(grammar_ids), lang)
        
        # Build final structure
        course_structure = {
            'course': {
                'id': course_id,
                'title': course['title'],
                'url': course.get('namedUrl'),
                'language': lang,
            },
            'lessons': [],
            'grammar_mapping': [],
            'stats': {
                'total_lessons': len(lessons),
                'lessons_with_grammar': len(grammar_lesson_map),
                'unique_grammar_lessons': len(grammar_details),
            }
        }
        
        # Add lessons
        for lesson in lessons:
            lesson_id = lesson['id']
            lesson_info = lessons_with_knowledge.get(lesson_id, {})
            knowledges = lesson_info.get('knowledges', [])
            
            grammar = [k for k in knowledges if '/gr-' in k.get('namedUrl', '')]
            vocabulary = [k for k in knowledges if '/lv-' in k.get('namedUrl', '')]
            regional = [k for k in knowledges if '/rs-' in k.get('namedUrl', '')]
            
            course_structure['lessons'].append({
                'id': lesson_id,
                'title': lesson['title'],
                'url': lesson['namedUrl'],
                'grammar_count': len(grammar),
                'vocabulary_count': len(vocabulary),
                'regional_studies_count': len(regional),
            })
        
        # Add grammar mapping
        for lesson_id, lesson_info in grammar_lesson_map.items():
            for knowledge in lesson_info['grammar_knowledges']:
                grammar_id = knowledge['id']
                detail = grammar_details.get(grammar_id, {})
                course_structure['grammar_mapping'].append({
                    'lesson_id': lesson_id,
                    'lesson_title': lesson_info['lesson_title'],
                    'grammar_id': grammar_id,
                    'grammar_title': knowledge['title'],
                    'grammar_url': knowledge['namedUrl'],
                    'has_detail': grammar_id in grammar_details,
                })
        
        # Save to file
        filename = os.path.join(output_dir, f"course_{lang.lower()}_structure.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(course_structure, f, indent=2, ensure_ascii=False)
        print(f"Course structure saved to {filename}")
        
        return course_structure

def main():
    exporter = FullCourseExporter()
    
    # Export Spanish course structure
    print("Exporting Spanish course structure...")
    course_data = exporter.export_course_structure(47994059, "SPANISH", "output")
    
    if course_data:
        print(f"\nCourse export completed!")
        print(f"Lessons: {course_data['stats']['total_lessons']}")
        print(f"Lessons with grammar: {course_data['stats']['lessons_with_grammar']}")
        print(f"Unique grammar lessons: {course_data['stats']['unique_grammar_lessons']}")
        
        # Also export grammar overview
        print(f"\nExporting grammar overview...")
        exporter.export_grammar("SPANISH", "output")

if __name__ == "__main__":
    main()
