import requests
import json

query = """
query GetLessonWithKnowledge($id: Int!, $lang: Language!) {
  content(id: $id, lang: $lang) {
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
variables = {"id": 49702751, "lang": "SPANISH"}
response = requests.post("https://learngerman.dw.com/graphql", 
                         json={"query": query, "variables": variables})
data = response.json()
print(json.dumps(data, indent=2))
