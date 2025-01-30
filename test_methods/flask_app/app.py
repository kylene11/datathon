import os
from flask import Flask, render_template, request, jsonify
import pandas as pd
import subprocess
import json
from pyvis.network import Network

app = Flask(__name__)
command = ["ollama", "run", "llama3.2"]
# Function to check if the file exists in the given Excel
def check_pdf_or_link(excel_file, identifier):
    # Read the Excel file
    data = pd.read_excel(excel_file)
    print(identifier)
    print(excel_file)
    

    # Check if necessary columns exist
    if excel_file == "wikileaks_parsed.xlsx" and 'PDF Path' in data.columns:
        filtered_data = data[data['PDF Path'] == identifier]
    elif excel_file == "news_excerpts_parsed.xlsx" and 'Link' in data.columns:
        filtered_data = data[data['Link'] == identifier]
    else:
        raise ValueError(f"Column not found for {excel_file} or identifier mismatch.")
    
    # Check if the filtered data is empty
    if filtered_data.empty:
        raise ValueError(f"No data found for the identifier: {identifier}")
    
    
    return filtered_data['Text'].dropna().to_string(index=False)

# Function to generate the network graph
def generate_network_graph(entities, relationships):
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
    net.show(os.path.join('static', 'entity_network.html'))

@app.route('/')
def index():
    return render_template('index.html',graph_url=None)

@app.route('/process', methods=['POST'])
def process():
    excel_file = request.form['excel_choice']
    identifier = request.form['identifier']
    
    # Check the file name and process accordingly
    if excel_file not in ["wikileaks_parsed.xlsx", "news_excerpts_parsed.xlsx"]:
        return jsonify({"status": "error", "message": "Invalid file selection."})

    try:
        # Get text data based on the choice
        combined_data = check_pdf_or_link(excel_file, identifier)

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

        # Call subprocess to run the Ollama commands
        result = subprocess.run(command, input=prompt, capture_output=True, text=True, check=True)
        output = result.stdout
        
        result_2 = subprocess.run(command, input=prompt_2, capture_output=True, text=True, check=True)
        output_2 = result_2.stdout
        output_2 = output_2.strip()
        output_2 = output_2.strip("`")
        print("Ollama Output for Prompt 2:", output_2)
    
        output_2_dict = json.loads(output_2)

    except subprocess.CalledProcessError as e:
        print("Error:", e.stderr)
        exit()

    # Generate network graph only if the output is valid
    if isinstance(output_2_dict, dict):
        entities = output_2_dict.get('entities', [])
        relationships = output_2_dict.get('relationships', [])
        generate_network_graph(entities, relationships)
        
        return render_template('index.html', graph_url="/static/entity_network.html", identifier='')

    return jsonify({"status": "error", "message": "No valid data found for the identifier."})
if __name__ == '__main__':
    app.run(debug=True)
