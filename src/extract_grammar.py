import requests
import json
import time
from typing import Dict, List, Any, Optional

class DWGraphQLClient:
    def __init__(self, base_url="https://learngerman.dw.com"):
        self.base_url = base_url
        self.graphql_url = f"{base_url}/graphql"
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Origin": base_url,
            "Referer": f"{base_url}/",
        })
    
    def query(self, query: str, variables: Dict[str, Any] = None) -> Dict[str, Any]:
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        response = self.session.post(self.graphql_url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_course(self, course_id: int, lang: str = "SPANISH") -> Optional[Dict[str, Any]]:
        """Get course details including lessons."""
        query = """
        query GetCourse($id: Int!, $lang: Language!) {
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
            return None
        return result.get("data", {}).get("content")
    
    def batch_get_lessons_with_knowledge(self, lesson_ids: List[int], lang: str = "SPANISH") -> List[Dict[str, Any]]:
        """Batch fetch lessons with their knowledges."""
        # Create keys input
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
            return []
        return result.get("data", {}).get("contents", [])
    
    def batch_get_knowledge_details(self, knowledge_ids: List[int], lang: str = "SPANISH") -> List[Dict[str, Any]]:
        """Batch fetch knowledge details including text."""
        keys = [{"id": kid, "type": "KNOWLEDGE"} for kid in knowledge_ids]
        query = """
        query BatchGetKnowledge($keys: [ContentKeyInput!]!, $lang: Language!) {
          contents(keys: $keys, lang: $lang) {
            ... on Knowledge {
              id
              title
              namedUrl
              dkGrammar
              dkGrammarCategory
              text
              teaser
            }
          }
        }
        """
        variables = {"keys": keys, "lang": lang}
        result = self.query(query, variables)
        if "errors" in result:
            print(f"GraphQL errors: {result['errors']}")
            return []
        return result.get("data", {}).get("contents", [])
    
    def get_grammar_overview_all(self, lang: str = "SPANISH") -> List[Dict[str, Any]]:
        """Get all grammar lessons from grammarOverview."""
        query = """
        query GetGrammarOverviewAll($lang: Language!) {
          grammarOverview(lang: $lang) {
            all {
              id
              title
              namedUrl
              dkGrammar
              dkGrammarCategory
            }
          }
        }
        """
        variables = {"lang": lang}
        result = self.query(query, variables)
        if "errors" in result:
            print(f"GraphQL errors: {result['errors']}")
            return []
        overview = result.get("data", {}).get("grammarOverview", {})
        return overview.get("all", [])

def extract_grammar_from_course(client, course_id=47994059, lang="SPANISH"):
    """Extract all grammar lessons associated with course lessons."""
    print(f"Fetching course {course_id}...")
    course = client.get_course(course_id, lang)
    if not course:
        print("Failed to fetch course")
        return []
    
    print(f"Course: {course['title']}")
    lessons = course.get('lessons', [])
    print(f"Total lessons: {len(lessons)}")
    
    # Batch fetch lessons with knowledges (in chunks to avoid huge query)
    lesson_ids = [lesson['id'] for lesson in lessons]
    print(f"Batch fetching {len(lesson_ids)} lessons with knowledges...")
    
    # Split into chunks of 20 (GraphQL may have limits)
    chunk_size = 20
    all_lessons_data = []
    for i in range(0, len(lesson_ids), chunk_size):
        chunk = lesson_ids[i:i+chunk_size]
        print(f"  Fetching chunk {i//chunk_size + 1}/{(len(lesson_ids)-1)//chunk_size + 1}")
        lessons_data = client.batch_get_lessons_with_knowledge(chunk, lang)
        all_lessons_data.extend(lessons_data)
        time.sleep(0.1)  # Small delay to be polite
    
    # Extract grammar knowledges (those with 'gr-' in namedUrl)
    grammar_knowledge_ids = set()
    grammar_by_lesson = []
    
    for lesson in all_lessons_data:
        lesson_id = lesson.get('id')
        lesson_title = lesson.get('title')
        knowledges = lesson.get('knowledges', [])
        
        grammar_knowledges = []
        for knowledge in knowledges:
            named_url = knowledge.get('namedUrl', '')
            if '/gr-' in named_url:  # Grammar lesson
                grammar_knowledge_ids.add(knowledge['id'])
                grammar_knowledges.append({
                    'id': knowledge['id'],
                    'title': knowledge['title'],
                    'namedUrl': named_url,
                })
        
        if grammar_knowledges:
            grammar_by_lesson.append({
                'lesson_id': lesson_id,
                'lesson_title': lesson_title,
                'grammar_knowledges': grammar_knowledges,
            })
    
    print(f"\nFound {len(grammar_knowledge_ids)} unique grammar lessons across {len(grammar_by_lesson)} lessons.")
    
    # Fetch grammar details in batch
    print(f"\nFetching grammar lesson details...")
    grammar_ids = list(grammar_knowledge_ids)
    grammar_details = {}
    
    chunk_size = 30
    for i in range(0, len(grammar_ids), chunk_size):
        chunk = grammar_ids[i:i+chunk_size]
        print(f"  Fetching chunk {i//chunk_size + 1}/{(len(grammar_ids)-1)//chunk_size + 1}")
        details = client.batch_get_knowledge_details(chunk, lang)
        for detail in details:
            grammar_details[detail['id']] = detail
        time.sleep(0.1)
    
    # Also get grammar overview to see if we missed any
    print(f"\nFetching grammar overview for completeness...")
    overview_grammars = client.get_grammar_overview_all(lang)
    overview_ids = {g['id'] for g in overview_grammars}
    print(f"Grammar overview has {len(overview_ids)} grammar lessons.")
    
    # Check which grammar lessons we have vs overview
    missing_ids = overview_ids - grammar_knowledge_ids
    print(f"Grammar lessons not linked to any lesson: {len(missing_ids)}")
    
    # Fetch missing grammar details
    if missing_ids:
        print(f"Fetching {len(missing_ids)} missing grammar lessons...")
        missing_list = list(missing_ids)
        for i in range(0, len(missing_list), chunk_size):
            chunk = missing_list[i:i+chunk_size]
            details = client.batch_get_knowledge_details(chunk, lang)
            for detail in details:
                grammar_details[detail['id']] = detail
            time.sleep(0.1)
    
    # Prepare final data structure
    result = {
        'course': {
            'id': course_id,
            'title': course['title'],
            'url': course.get('namedUrl'),
        },
        'grammar_lessons': [],
        'grammar_by_lesson': grammar_by_lesson,
        'stats': {
            'total_lessons': len(lessons),
            'lessons_with_grammar': len(grammar_by_lesson),
            'total_grammar_lessons': len(grammar_details),
            'grammar_from_overview': len(overview_ids),
        }
    }
    
    # Add grammar lessons with full details
    for grammar_id, detail in grammar_details.items():
        result['grammar_lessons'].append({
            'id': grammar_id,
            'title': detail.get('title'),
            'url': detail.get('namedUrl'),
            'dkGrammar': detail.get('dkGrammar'),
            'dkGrammarCategory': detail.get('dkGrammarCategory'),
            'teaser': detail.get('teaser'),
            'text': detail.get('text'),  # HTML content
        })
    
    return result

def save_results(data, filename_prefix="grammar_lessons"):
    """Save results to JSON file."""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {filename}")
    
    # Also save a simplified version with just titles and URLs
    simple_filename = f"{filename_prefix}_simple_{timestamp}.json"
    simple_data = []
    for grammar in data['grammar_lessons']:
        simple_data.append({
            'id': grammar['id'],
            'title': grammar['title'],
            'url': grammar['url'],
            'category': grammar.get('dkGrammarCategory'),
        })
    with open(simple_filename, 'w', encoding='utf-8') as f:
        json.dump(simple_data, f, indent=2, ensure_ascii=False)
    print(f"Simple list saved to {simple_filename}")

def main():
    client = DWGraphQLClient()
    data = extract_grammar_from_course(client)
    if data:
        save_results(data)
        print(f"\nExtraction complete!")
        print(f"Course: {data['course']['title']}")
        print(f"Total grammar lessons extracted: {len(data['grammar_lessons'])}")
        
        # Print sample
        if data['grammar_lessons']:
            print(f"\nSample grammar lesson:")
            sample = data['grammar_lessons'][0]
            print(f"  Title: {sample['title']}")
            print(f"  URL: {sample['url']}")
            print(f"  Text preview: {sample.get('text', '')[:100]}...")

if __name__ == "__main__":
    main()
