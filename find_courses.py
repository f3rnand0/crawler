import requests
import json

query = """
query GetNavigationRoot($lang: Language!) {
  lgNavigationRoot(lang: $lang) {
    allCoursesNavigation {
      id
      title
      namedUrl
    }
  }
}
"""
for lang in ["SPANISH", "ENGLISH", "GERMAN"]:
    print(f"\n{lang}:")
    variables = {"lang": lang}
    response = requests.post("https://learngerman.dw.com/graphql", 
                             json={"query": query, "variables": variables})
    data = response.json()
    courses = data.get('data', {}).get('lgNavigationRoot', {}).get('allCoursesNavigation', [])
    for course in courses:
        print(f"  {course['id']}: {course['title']} - {course['namedUrl']}")
