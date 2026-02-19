import requests
import json

def test_introspection():
    url = "https://learngerman.dw.com/graphql"
    
    # Try to get schema introspection
    introspection_query = {
        "query": """
        query IntrospectionQuery {
          __schema {
            queryType { name }
            mutationType { name }
            subscriptionType { name }
            types {
              ...FullType
            }
            directives {
              name
              description
              locations
              args {
                ...InputValue
              }
            }
          }
        }
        
        fragment FullType on __Type {
          kind
          name
          description
          fields(includeDeprecated: true) {
            name
            description
            args {
              ...InputValue
            }
            type {
              ...TypeRef
            }
            isDeprecated
            deprecationReason
          }
          inputFields {
            ...InputValue
          }
          interfaces {
            ...TypeRef
          }
          enumValues(includeDeprecated: true) {
            name
            description
            isDeprecated
            deprecationReason
          }
          possibleTypes {
            ...TypeRef
          }
        }
        
        fragment InputValue on __InputValue {
          name
          description
          type { ...TypeRef }
          defaultValue
        }
        
        fragment TypeRef on __Type {
          kind
          name
          ofType {
            kind
            name
            ofType {
              kind
              name
              ofType {
                kind
                name
                ofType {
                  kind
                  name
                  ofType {
                    kind
                    name
                    ofType {
                      kind
                      name
                      ofType {
                        kind
                        name
                      }
                    }
                  }
                }
              }
            }
          }
        }
        """
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    try:
        response = requests.post(url, json=introspection_query, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if "errors" in data:
                print("Errors:", json.dumps(data["errors"], indent=2))
            else:
                # Save schema
                with open("graphql_schema.json", "w") as f:
                    json.dump(data, f, indent=2)
                print("Schema saved to graphql_schema.json")
                
                # Try to find relevant types
                types = data.get("data", {}).get("__schema", {}).get("types", [])
                relevant = [t for t in types if t.get("name") and 
                           ("Course" in t["name"] or "Lesson" in t["name"] or "Grammar" in t["name"])]
                print(f"Found {len(relevant)} relevant types")
                for t in relevant:
                    print(f"  - {t['name']}: {t.get('description', '')}")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_introspection()
