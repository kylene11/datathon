import pandas as pd
import subprocess
import json
from pyvis.network import Network
import os

os.environ['PYTHONIOENCODING'] = 'utf-8'

# Step 1: Read Excel File
file_path = "wikileaks_parsed.xlsx"
data = pd.read_excel(file_path)
text_data = data['Text']  
filtered_data = data[data['PDF Path'] == '14.pdf']
combined_data = " ".join(filtered_data['Text'].dropna())

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
Please summarize all the relationships between the entities in the following text into a JSON format. Provide **only** the JSON output with no additional text, and ensure that the relationships and entities are correctly structured as shown in the example. Do not include any other explanation or output.
For each relationship, include:
- 'from' (the first entity)
- 'to' (the related entity)
- 'description' (a short explanation of the relationship).

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
      "from": "Entity 1", 
      "to": "Entity 2", 
      "description": "relationship description"
    }},
    {{
      "from": "Entity 2", 
      "to": "Entity 3", 
      "description": "another relationship description"
    }}
  ]
}}
{combined_data}
"""

try:
    result = subprocess.run(command, input=prompt, capture_output=True, text=True, check=True, encoding='utf-8')
    output = result.stdout
    #print("Ollama Output:", output)  # Debugging line to examine raw output
    
    result_2 = subprocess.run(command, input=prompt_2, capture_output=True, text=True, check=True, encoding='utf-8')
    output_2 = result_2.stdout
    output_2 = output_2.strip()
    output_2 = output_2.strip("`")
    print("Ollama Output for Prompt 2:", output_2)
    
    output_2_dict = json.loads(output_2)

except subprocess.CalledProcessError as e:
    print("Error:", e.stderr)
    exit()

# Step 3: Parse and Create Network Graph from Relationships
# Step 3: Parse and Create Network Graph from Relationships
if isinstance(output_2_dict, dict):
    entities = output_2_dict.get('entities', [])
    relationships = output_2_dict.get('relationships', [])

    print(f"Entities: {entities}")
    print(f"Relationships: {relationships}")

    # Initialize a Directed Graph with better spacing
    net = Network(notebook=True, height="750px", width="100%", directed=True)
    net.barnes_hut()
    net.toggle_physics(True)

    # Add nodes for entities
    entity_names = set(entity['name'] for entity in entities)  # Track existing nodes
    for entity in entities:
        net.add_node(entity['name'])

    # Add edges for relationships
    for relationship in relationships:
        from_node = relationship['from']
        to_node = relationship['to']

        # Add missing nodes dynamically
        if from_node not in entity_names:
            net.add_node(from_node)
            entity_names.add(from_node)
        if to_node not in entity_names:
            net.add_node(to_node)
            entity_names.add(to_node)

        # Add the edge
        net.add_edge(from_node, to_node, title=relationship['description'], label=relationship['description'])

    # Show the network
    net.show("entity_network.html")
