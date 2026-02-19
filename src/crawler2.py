import requests
import json
from typing import Dict, Any, Optional, List

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
                dkGrammar
                dkGrammarCategory
              }
              exercises {
                id
                title
              }
              dkGrammar
              dkGrammarCategory
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
    
    def get_grammar_overview(self, lang: str = "SPANISH") -> Optional[Dict[str, Any]]:
        """Get grammar overview categories."""
        query = """
        query GetGrammarOverview($lang: Language!) {
          grammarOverview(lang: $lang) {
            all {
              id
              title
              namedUrl
              dkGrammar
              dkGrammarCategory
            }
            verbs {
              id
              headline
              grammars {
                id
                title
                namedUrl
                dkGrammar
                dkGrammarCategory
              }
            }
            tenses {
              id
              headline
              grammars {
                id
                title
                namedUrl
                dkGrammar
                dkGrammarCategory
              }
            }
            nounsAndArticles {
              id
              headline
              grammars {
                id
                title
                namedUrl
                dkGrammar
                dkGrammarCategory
              }
            }
            declination {
              id
              headline
              grammars {
                id
                title
                namedUrl
                dkGrammar
                dkGrammarCategory
              }
            }
            negation {
              id
              headline
              grammars {
                id
                title
                namedUrl
                dkGrammar
                dkGrammarCategory
              }
            }
            pronoun {
              id
              headline
              grammars {
                id
                title
                namedUrl
                dkGrammar
                dkGrammarCategory
              }
            }
            prepositions {
              id
              headline
              grammars {
                id
                title
                namedUrl
                dkGrammar
                dkGrammarCategory
              }
            }
            adjectivesAndAdverbs {
              id
              headline
              grammars {
                id
                title
                namedUrl
                dkGrammar
                dkGrammarCategory
              }
            }
            sentenceStructure {
              id
              headline
              grammars {
                id
                title
                namedUrl
                dkGrammar
                dkGrammarCategory
              }
            }
            numbers {
              id
              headline
              grammars {
                id
                title
                namedUrl
                dkGrammar
                dkGrammarCategory
              }
            }
            spellingOrthography {
              id
              headline
              grammars {
                id
                title
                namedUrl
                dkGrammar
                dkGrammarCategory
              }
            }
            others {
              id
              headline
              grammars {
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
        variables = {"lang": lang}
        result = self.query(query, variables)
        if "errors" in result:
            print(f"GraphQL errors: {result['errors']}")
            return None
        return result.get("data", {}).get("grammarOverview")
    
    def get_grammar_detail(self, grammar_id: int, lang: str = "SPANISH") -> Optional[Dict[str, Any]]:
        """Get detailed grammar lesson content."""
        query = """
        query GetGrammarDetail($id: Int!, $lang: Language!) {
          content(id: $id, lang: $lang) {
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
        variables = {"id": grammar_id, "lang": lang}
        result = self.query(query, variables)
        if "errors" in result:
            print(f"GraphQL errors: {result['errors']}")
            return None
        return result.get("data", {}).get("content")

def analyze_course_grammar_links(client, course_id=47994059, lang="SPANISH"):
    """Analyze how grammar lessons are linked to course lessons."""
    course = client.get_course(course_id, lang)
    if not course:
        print("Failed to fetch course")
        return
    
    print(f"Course: {course['title']}")
    print(f"Total lessons: {len(course['lessons'])}")
    
    # Check lessons with dkGrammar
    lessons_with_grammar = [l for l in course['lessons'] if l.get('dkGrammar')]
    print(f"Lessons with dkGrammar field non-zero: {len(lessons_with_grammar)}")
    for lesson in lessons_with_grammar[:10]:
        print(f"  Lesson {lesson['id']}: {lesson['title']}")
        print(f"    dkGrammar: {lesson['dkGrammar']}, dkGrammarCategory: {lesson['dkGrammarCategory']}")
    
    # Get all grammar lessons
    overview = client.get_grammar_overview(lang)
    if not overview:
        print("Failed to fetch grammar overview")
        return
    
    # Build map of grammar ID to grammar lesson
    grammar_map = {}
    categories = ['verbs', 'tenses', 'nounsAndArticles', 'declination', 'negation', 
                 'pronoun', 'prepositions', 'adjectivesAndAdverbs', 'sentenceStructure',
                 'numbers', 'spellingOrthography', 'others']
    
    for cat in categories:
        cat_data = overview.get(cat)
        if cat_data:
            for grammar in cat_data.get('grammars', []):
                grammar_map[grammar['id']] = grammar
    
    # Also add from 'all' (which is a list)
    for grammar in overview.get('all', []):
        grammar_map[grammar['id']] = grammar
    
    print(f"\nTotal unique grammar lessons found: {len(grammar_map)}")
    
    # Check if any lesson dkGrammar matches grammar IDs
    matched = 0
    for lesson in lessons_with_grammar:
        grammar_id = lesson.get('dkGrammar')
        if grammar_id and grammar_id in grammar_map:
            matched += 1
            grammar = grammar_map[grammar_id]
            print(f"  Match: Lesson '{lesson['title']}' -> Grammar '{grammar['title']}'")
    
    print(f"\nMatched lessons: {matched}/{len(lessons_with_grammar)}")
    
    # Check course-level dkGrammar
    course_dk_grammar = course.get('dkGrammar')
    course_dk_category = course.get('dkGrammarCategory')
    print(f"\nCourse dkGrammar: {course_dk_grammar}, dkGrammarCategory: {course_dk_category}")
    
    # Try to find grammar lessons by category
    if course_dk_category:
        print(f"\nLooking for grammar lessons with category {course_dk_category}...")
        # Not sure how category mapping works
    
    # Sample first few grammar lessons
    print(f"\nSample grammar lessons:")
    for i, (gid, grammar) in enumerate(list(grammar_map.items())[:5]):
        print(f"  {grammar['title']} (ID: {gid})")
        print(f"    URL: {grammar.get('namedUrl', 'N/A')}")
        # Fetch detail
        detail = client.get_grammar_detail(gid, lang)
        if detail:
            teaser = detail.get('teaser', '')[:100]
            print(f"    Teaser: {teaser}...")

def main():
    client = DWGraphQLClient()
    analyze_course_grammar_links(client)

if __name__ == "__main__":
    main()
