import requests
import json

query = """
query GetCourseWithKnowledge($id: Int!, $lang: Language!) {
  content(id: $id, lang: $lang) {
    ... on Course {
      id
      title
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
variables = {"id": 47994059, "lang": "SPANISH"}
response = requests.post("https://learngerman.dw.com/graphql", 
                         json={"query": query, "variables": variables})
data = response.json()
print(json.dumps(data, indent=2))
