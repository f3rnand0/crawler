import requests
import json

query = """
query GetGrammarCategories($lang: Language!) {
  grammarOverview(lang: $lang) {
    verbs { id headline }
    tenses { id headline }
    nounsAndArticles { id headline }
    declination { id headline }
    negation { id headline }
    pronoun { id headline }
    prepositions { id headline }
    adjectivesAndAdverbs { id headline }
    sentenceStructure { id headline }
    numbers { id headline }
    spellingOrthography { id headline }
    others { id headline }
  }
}
"""
variables = {"lang": "SPANISH"}
response = requests.post("https://learngerman.dw.com/graphql", 
                         json={"query": query, "variables": variables})
data = response.json()
categories = []
for field, value in data.get('data', {}).get('grammarOverview', {}).items():
    if isinstance(value, dict) and 'id' in value:
        categories.append({
            'id': value['id'],
            'headline': value['headline'],
            'type': field
        })
print(json.dumps(categories, indent=2, ensure_ascii=False))
