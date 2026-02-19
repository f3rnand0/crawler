import requests
import json
import os
import html2text
from typing import Dict, List, Any, Optional

class DWGrammarExporter:
    def __init__(self, base_url="https://learngerman.dw.com"):
        self.base_url = base_url
        self.graphql_url = f"{base_url}/graphql"
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
    
    def query(self, query: str, variables: Dict[str, Any] = None) -> Dict[str, Any]:
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        response = self.session.post(self.graphql_url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_grammar_overview_with_categories(self, lang: str = "SPANISH") -> Dict[str, Any]:
        """Get grammar overview with categories and their grammar lessons."""
        query = """
        query GetGrammarOverviewWithCategories($lang: Language!) {
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
            return {}
        return result.get("data", {}).get("grammarOverview", {})
    
    def get_knowledge_details_batch(self, knowledge_ids: List[int], lang: str = "SPANISH") -> Dict[int, Dict[str, Any]]:
        """Batch fetch knowledge details."""
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
            return {}
        
        contents = result.get("data", {}).get("contents", [])
        return {item['id']: item for item in contents}
    
    def export_grammar(self, lang: str = "SPANISH", output_dir: str = "output"):
        """Main export function."""
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Fetching grammar overview for {lang}...")
        overview = self.get_grammar_overview_with_categories(lang)
        
        if not overview:
            print("Failed to fetch grammar overview")
            return
        
        # Collect all grammar IDs
        all_grammar_ids = set()
        category_grammars = {}
        
        # Process each category
        categories = [
            ('verbs', 'Verbs'),
            ('tenses', 'Tenses'),
            ('nounsAndArticles', 'Nouns and Articles'),
            ('declination', 'Declination'),
            ('negation', 'Negation'),
            ('pronoun', 'Pronoun'),
            ('prepositions', 'Prepositions'),
            ('adjectivesAndAdverbs', 'Adjectives and Adverbs'),
            ('sentenceStructure', 'Sentence Structure'),
            ('numbers', 'Numbers'),
            ('spellingOrthography', 'Spelling and Orthography'),
            ('others', 'Others')
        ]
        
        for field, display_name in categories:
            cat_data = overview.get(field)
            if cat_data and isinstance(cat_data, dict):
                category_id = cat_data.get('id')
                headline = cat_data.get('headline', display_name)
                grammars = cat_data.get('grammars', [])
                
                grammar_ids = [g['id'] for g in grammars]
                all_grammar_ids.update(grammar_ids)
                
                category_grammars[field] = {
                    'id': category_id,
                    'headline': headline,
                    'grammar_ids': grammar_ids,
                    'grammars': grammars  # basic info
                }
        
        # Also add 'all' grammars (might be duplicates)
        all_grammars_list = overview.get('all', [])
        all_grammar_ids.update([g['id'] for g in all_grammars_list])
        
        print(f"Total unique grammar lessons: {len(all_grammar_ids)}")
        
        # Fetch details in batches
        print(f"Fetching grammar details...")
        all_grammar_ids_list = list(all_grammar_ids)
        batch_size = 30
        grammar_details = {}
        
        for i in range(0, len(all_grammar_ids_list), batch_size):
            batch = all_grammar_ids_list[i:i+batch_size]
            print(f"  Batch {i//batch_size + 1}/{(len(all_grammar_ids_list)-1)//batch_size + 1}")
            details = self.get_knowledge_details_batch(batch, lang)
            grammar_details.update(details)
        
        # Build final data structure
        export_data = {
            'language': lang,
            'categories': [],
            'grammar_lessons': [],
            'stats': {
                'total_grammar_lessons': len(grammar_details),
                'categories': len(category_grammars),
            }
        }
        
        # Add categories with grammar details
        for field, cat_info in category_grammars.items():
            category_lessons = []
            for grammar_id in cat_info['grammar_ids']:
                if grammar_id in grammar_details:
                    detail = grammar_details[grammar_id]
                    category_lessons.append({
                        'id': grammar_id,
                        'title': detail.get('title'),
                        'url': detail.get('namedUrl'),
                        'text': detail.get('text'),
                        'teaser': detail.get('teaser'),
                        'dkGrammar': detail.get('dkGrammar'),
                        'dkGrammarCategory': detail.get('dkGrammarCategory'),
                    })
            
            export_data['categories'].append({
                'id': cat_info['id'],
                'name': cat_info['headline'],
                'slug': field,
                'grammar_count': len(category_lessons),
                'grammar_lessons': category_lessons,
            })
        
        # Add all grammar lessons (including those not in categories)
        all_lessons = []
        for grammar_id, detail in grammar_details.items():
            all_lessons.append({
                'id': grammar_id,
                'title': detail.get('title'),
                'url': detail.get('namedUrl'),
                'text': detail.get('text'),
                'teaser': detail.get('teaser'),
                'dkGrammar': detail.get('dkGrammar'),
                'dkGrammarCategory': detail.get('dkGrammarCategory'),
            })
        export_data['grammar_lessons'] = all_lessons
        
        # Save JSON
        json_path = os.path.join(output_dir, f"grammar_{lang.lower()}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        print(f"Saved JSON to {json_path}")
        
        # Save markdown files
        self.export_markdown(export_data, output_dir, lang)
        
        return export_data
    
    def export_markdown(self, data, output_dir, lang):
        """Export grammar lessons as markdown files."""
        md_dir = os.path.join(output_dir, "markdown", lang.lower())
        os.makedirs(md_dir, exist_ok=True)
        
        # Initialize HTML to text converter
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        
        # Export by category
        for category in data['categories']:
            cat_slug = category['slug']
            cat_name = category['name']
            cat_dir = os.path.join(md_dir, cat_slug)
            os.makedirs(cat_dir, exist_ok=True)
            
            # Create category README
            cat_readme = f"# {cat_name}\n\n"
            cat_readme += f"Grammar lessons: {category['grammar_count']}\n\n"
            for lesson in category['grammar_lessons']:
                title = lesson['title']
                url = lesson['url']
                lesson_id = lesson['id']
                cat_readme += f"- [{title}]({lesson_id}.md)\n"
            
            with open(os.path.join(cat_dir, "README.md"), 'w', encoding='utf-8') as f:
                f.write(cat_readme)
            
            # Export each lesson
            for lesson in category['grammar_lessons']:
                title = lesson['title']
                url = lesson['url']
                text_html = lesson.get('text', '')
                text_md = h.handle(text_html) if text_html else ""
                
                md_content = f"# {title}\n\n"
                md_content += f"**URL:** {self.base_url}{url}\n\n"
                md_content += f"**ID:** {lesson['id']}\n\n"
                if lesson.get('teaser'):
                    md_content += f"**Teaser:** {lesson['teaser']}\n\n"
                md_content += f"**Category:** {category['name']}\n\n"
                md_content += "## Content\n\n"
                md_content += text_md
                
                filename = os.path.join(cat_dir, f"{lesson['id']}.md")
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(md_content)
        
        print(f"Markdown files saved to {md_dir}")
        
        # Also create an index of all grammar lessons
        index_path = os.path.join(md_dir, "ALL_GRAMMAR.md")
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("# All Grammar Lessons\n\n")
            f.write(f"Total: {len(data['grammar_lessons'])}\n\n")
            for category in data['categories']:
                f.write(f"## {category['name']}\n\n")
                for lesson in category['grammar_lessons']:
                    f.write(f"- [{lesson['title']}]({category['slug']}/{lesson['id']}.md)\n")
                f.write("\n")

def main():
    exporter = DWGrammarExporter()
    
    # Export Spanish grammar
    print("Exporting Spanish grammar lessons...")
    data = exporter.export_grammar("SPANISH", "output")
    
    if data:
        print(f"\nExport completed successfully!")
        print(f"Total grammar lessons: {data['stats']['total_grammar_lessons']}")
        print(f"Categories: {data['stats']['categories']}")
        print(f"\nOutput saved to 'output/' directory")

if __name__ == "__main__":
    main()
