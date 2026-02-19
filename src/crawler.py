import requests
import json
from typing import Dict, Any, Optional

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

def main():
    client = DWGraphQLClient()
    
    # Test course query
    print("Fetching course 47994059...")
    course = client.get_course(47994059, "SPANISH")
    if course:
        print(f"Course: {course.get('title')}")
        print(f"URL: {course.get('namedUrl')}")
        print(f"Lessons: {len(course.get('lessons', []))}")
        for lesson in course.get('lessons', [])[:5]:
            print(f"  - {lesson.get('id')}: {lesson.get('title')}")
            if lesson.get('dkGrammar'):
                print(f"    Grammar ID: {lesson.get('dkGrammar')}")
        print(f"Course dkGrammar: {course.get('dkGrammar')}")
        print(f"Course dkGrammarCategory: {course.get('dkGrammarCategory')}")
    
    # Test grammar overview
    print("\nFetching grammar overview...")
    overview = client.get_grammar_overview("SPANISH")
    if overview:
        # Count total grammar lessons
        total = 0
        categories = ['verbs', 'tenses', 'nounsAndArticles', 'declination', 'negation', 
                     'pronoun', 'prepositions', 'adjectivesAndAdverbs', 'sentenceStructure',
                     'numbers', 'spellingOrthography', 'others']
        for cat in categories:
            cat_data = overview.get(cat)
            if cat_data:
                grammars = cat_data.get('grammars', [])
                total += len(grammars)
                print(f"{cat}: {len(grammars)} grammar lessons")
        print(f"Total grammar lessons: {total}")
        
        # Show first few from all
        all_grammars = overview.get('all', {}).get('grammars', []) if overview.get('all') else []
        if not all_grammars:
            all_grammars = overview.get('all', [])
        if all_grammars:
            print(f"First grammar lesson: {all_grammars[0].get('title')} (ID: {all_grammars[0].get('id')})")
            # Get detail
            detail = client.get_grammar_detail(all_grammars[0]['id'], "SPANISH")
            if detail:
                print(f"Teaser: {detail.get('teaser', '')[:100]}...")

if __name__ == "__main__":
    main()
