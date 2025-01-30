import pandas as pd
import subprocess
import json
import networkx as nx
import matplotlib.pyplot as plt

# Step 1: Read Excel File
file_path = "wikileaks_parsed.xlsx"
data = pd.read_excel(file_path)
text_data = data['Text']  # Replace 'Text' with your column name
filtered_data = data[data['PDF Path'] == '106.pdf']
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
Please summarize all the relationships between the entities in the following text into a JSON format. Provide only the JSON output, without any additional text. Use the example format as a reference for structure, but do not copy it directly. The JSON should include the names of entities and the relationships between them, with descriptions of those relationships. 
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
    result = subprocess.run(command, input=prompt, capture_output=True, text=True, check=True)
    output = result.stdout
    print("Ollama Output:", output)  # Debugging line to examine raw output
    result_2 = subprocess.run(command, input=prompt_2, capture_output=True, text=True, check=True)
    output_2 = result_2.stdout
    output_2 = output_2.strip()
    output_2 = output_2.strip("`")
    print("Ollama Output for Prompt 2:", output_2)
   
    output_2_dict = json.loads(output_2)

except subprocess.CalledProcessError as e:
    print("Error:", e.stderr)
    exit()

# Step 3: Parse and Create Network Graph from Relationships
if isinstance(output_2_dict, dict):
    entities = output_2_dict.get('entities', [])
    relationships = output_2_dict.get('relationships', [])

    print(f"Entities: {entities}")
    print(f"Relationships: {relationships}")

    # Initialize a Directed Graph
    G = nx.DiGraph()

    # Add Nodes (Entities)
    for entity in entities:
        G.add_node(entity['name'])

    # Add Edges (Relationships)
    for relationship in relationships:
        G.add_edge(relationship['from'], relationship['to'], description=relationship['description'])

    # Step 3: Visualize the Network Graph
    plt.figure(figsize=(15, 15))
    pos = nx.kamada_kawai_layout(G, scale=2)  # For better visualization of the graph
    nx.draw(G, pos, with_labels=True, node_size=3000, node_color='skyblue', font_size=10, font_weight='bold', edge_color='gray', arrows=True)

    # Display edge labels (relationship descriptions)
    edge_labels = nx.get_edge_attributes(G, 'description')
    def insert_line_breaks_after_n_words(text, n=5):
      words = text.split()
      lines = []

      # Create lines with n words each
      for i in range(0, len(words), n):
          lines.append(" ".join(words[i:i+n]))

      return "\n".join(lines)

  # Example usage:
    edge_labels_multiline = {key: insert_line_breaks_after_n_words(value, 5) for key, value in edge_labels.items()}

  # Draw edge labels with multiline text
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels_multiline, font_size=8)


    plt.title("Entity Relationship Network")
    plt.show()  # Display the plot

else:
    print("Error: Parsed data is not in the expected format.")