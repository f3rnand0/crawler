import json
import requests

client = requests.Session()
client.headers.update({"Content-Type": "application/json"})

query = """
query GetGrammarOverview($lang: Language!) {
  grammarOverview(lang: $lang) {
    all {
      id
      title
    }
    verbs {
      id
      headline
      grammars {
        id
        title
      }
    }
  }
}
"""
result = client.post("https://learngerman.dw.com/graphql", json={"query": query, "variables": {"lang": "SPANISH"}})
data = result.json()
print(json.dumps(data, indent=2))
