import pandas as pd
import subprocess
import json
from pyvis.network import Network
import openpyxl
import sys

# Step 1: Read Excel File
file_path = sys.argv[1]
user_input = sys.argv[2]

#initialise response
response = {
    "result": None,
    "networkFile": None,
    "error": None
}


#text_data = data['Text']

if "wikileaks_parsed.xlsx" in file_path:
  data = pd.read_excel(file_path)
  filtered_data = data[data['PDF Path'] == user_input]
  combined_data = " ".join(filtered_data['Text'].dropna())
elif "news_excerpts_parsed.xlsx" in file_path:
    data = pd.read_excel(file_path)
    filtered_data = data[data['Link'] == user_input]
    combined_data = " ".join(filtered_data['Text'].dropna())
else:
    combined_data= user_input

if combined_data=="":
  print("Error: Selected data not found")
  response = {
        "result": None,
        "networkFile": None,
        "error": "Selected data not found"
    }
  print(json.dumps(response))
  sys.exit()  # Exit the program if data is invalid


# Step 2: Use Ollama to Extract Entities and Relationships
command = ["ollama", "run", "llama3.2"]
prompt = f"""
Please analyze the following text and summarize the involved entities and the relationships between them in a clear, narrative form. For each entity, provide a brief description of what it is. Then, summarize how the entities are related to each other in terms of their interactions or associations.

Output should be structured in the following way:

Here are the involved entities:
1. Entity Name (Description of what the entity is, role, or type of entity)
2. Entity Name (Description of what the entity is, role, or type of entity)
...

Relationships between entities:
* Entity 1 and Entity 2 are [description of the relationship].
* Entity 1 and Entity 3 are [description of the relationship].
...

The text to analyze is:
{combined_data}
"""

prompt_2 = f"""
Please summarize all the relationships between the entities in the following text into a JSON format. 
For each relationship, include:
- 'source' (the first entity)
- 'target' (the related entity)
- 'description' 'relationship' (a **concise** but **detailed** description)

Provide **only** the JSON output with no additional text, and ensure that the relationships and entities are correctly structured as shown in the example. Do not include any other explanation or output.
Example structure (do not copy it directly):
{{
  "entities": [
    {{
      "name": "Entity 1"
    }},
    {{
      "name": "Entity 2"
    }},
    {{
      "name": "Entity 3"
    }}
  ], 
  "relationships": [
    {{
      "source": "Entity 1", 
      "target": "Entity 2", 
      "description": "relationship description"
    }},
    {{
      "source": "Entity 2", 
      "target": "Entity 3", 
      "description": "another relationship description"
    }}
  ]
}}
{combined_data}
"""

try:
    # Run the first subprocess for entity extraction
    result = subprocess.run(command, input=prompt, capture_output=True, text=True, check=True)
    output = result.stdout
    print(output)

    # Run the second subprocess for JSON output with relationships
    result_2 = subprocess.run(command, input=prompt_2, capture_output=True, text=True, check=True)
    output_2 = result_2.stdout
    output_2 = output_2.strip()
    output_2 = output_2.strip("`")
    print(output_2)
   
    
    # Convert the JSON output to a Python dictionary
    output_2_dict = json.loads(output_2)

    # Step 3: Parse and Create Network Graph from Relationships
    if isinstance(output_2_dict, dict):
        entities = output_2_dict.get('entities', [])
        relationships = output_2_dict.get('relationships', [])

        #print(f"Entities: {entities}")
        #print(f"Relationships: {relationships}")

        # Initialize a Directed Graph with better spacing
        net = Network(notebook=True, height="750px", width="100%", directed=True)
        
        net.barnes_hut()
        net.toggle_physics(True)

        # Add nodes for entities
        entity_names = set(entity['name'] for entity in entities)  # Track existing nodes
        for entity in entities:
            net.add_node(entity['name'])
        if relationships:
          first_relationship = relationships[0]  # Check the first relationship to get key names dynamically
          keys = list(first_relationship.keys())

          # Assign the first key as source_key, second key as target_key, and third key as description_key
          if len(keys) >= 3:
              source_key = keys[0]  # First key is source
              target_key = keys[1]  # Second key is target
              description = keys[2]  # Third key is description
          else:
              # If there are less than 3 keys, print an error message
              print("Error: Expected at least 3 keys in the relationship, found fewer.")
              sys.exit()  # Exit the program if the structure is incorrect

        # Add edges for relationships
        for relationship in relationships:
            from_node = relationship[source_key]
            to_node = relationship[target_key]

            # Add missing nodes dynamically
            if from_node not in entity_names:
                net.add_node(from_node)
                entity_names.add(from_node)
            if to_node not in entity_names:
                net.add_node(to_node)
                entity_names.add(to_node)

            # Add the edge
            net.add_edge(from_node, to_node, title=relationship[description], label=relationship[description])

        # Show the network
        # Save the generated HTML in the public directory
        try:
          net.show('public/entity_network.html')
        except Exception as e:
            response = {
        "result": None,
        "networkFile": None,
        "error": str(e)  # Send error message
    }
    print(json.dumps(response))
    sys.exit()

except subprocess.CalledProcessError as e:
    print("Error in subprocess:", e.stderr)
    response = {  # Initialize response here for subprocess errors
        "result": None,
        "networkFile": None,
        "error": f"Error in subprocess: {e.stderr}"
    }
    print(json.dumps(response))

except FileNotFoundError as e:
    print(f"File not found: {e}")
    response = {  # Initialize response here for file not found errors
        "result": None,
        "networkFile": None,
        "error": f"File not found: {e}"
    }
    print(json.dumps(response))
except ModuleNotFoundError as e:
    print(f"Module not found: {e}")
    response = {  # Initialize response here for module not found errors
        "result": None,
        "networkFile": None,
        "error": f"Module not found: {e}"
    }
    print(json.dumps(response))
except json.JSONDecodeError as e:
    print(f"JSON Decode Error: {e}")
    response = {  # Initialize response here for JSON decode errors
        "result": None,
        "networkFile": None,
        "error": f"JSON Decode Error: {e}"
    }
    print(json.dumps(response))
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    response = {  # Initialize response here for unexpected errors
        "result": None,
        "networkFile": None,
        "error": f"An unexpected error occurred: {e}"
    }
    print(json.dumps(response))
