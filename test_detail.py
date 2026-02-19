import requests
import json

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
variables = {"id": 49930523, "lang": "SPANISH"}
response = requests.post("https://learngerman.dw.com/graphql", 
                         json={"query": query, "variables": variables})
data = response.json()
print(json.dumps(data, indent=2))
