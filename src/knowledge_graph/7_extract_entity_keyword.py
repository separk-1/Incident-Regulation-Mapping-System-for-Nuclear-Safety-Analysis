import json
import os
import pandas as pd
import openai
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables for API keys
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# File paths
LER_DF_PATH = "../../data/processed/2_updated_ler_df.csv"  # Path to LER data CSV
CLAUSE_CSV_PATH = "../../data/processed/3_ler_cfr.csv"  # Path to clause data CSV
OUTPUT_JSON_PATH = "../../data/processed/01030941_ler_kg_keyword.json"  # Output JSON file

# Load datasets
ler_df = pd.read_csv(LER_DF_PATH, encoding="utf-8")
clause_df = pd.read_csv(CLAUSE_CSV_PATH, encoding="utf-8")

# Merge datasets on the "File Name" field
ler_df = pd.merge(ler_df, clause_df, left_on="File Name", right_on="filename", how="left")

# Debug: Display a sample of the merged data
print("\nSample of the merged data:")
print(ler_df.head())

# Function to extract attributes using GPT
def extract_attributes(text):
    prompt = f"""
        You are an expert in extracting structured and concise information. Extract the following attributes as concise and distinct keywords from the provided text. 

        - Task: Provide up to 3 key phrases describing the task.
        - Event: Provide up to 3 key phrases summarizing what happened.
        - Cause: Provide up to 3 key phrases stating the main reason for the incident.
        - Influence: Provide up to 3 key phrases summarizing the key impact or consequence.
        - Corrective Actions: Provide up to 3 key phrases listing the actions taken.
        - Similar Events: Provide up to 2 key phrases mentioning any known similar events, or an empty list if none are known.

        Ensure there is no repetition between attributes, and focus on the most important information. Use only key phrases.

        Incident Description:
        "{text}"

        Respond strictly in JSON format:
        {{
            "Task": ["Keyword1", "Keyword2", "Keyword3"],
            "Event": ["Keyword1", "Keyword2", "Keyword3"],
            "Cause": ["Keyword1", "Keyword2", "Keyword3"],
            "Influence": ["Keyword1", "Keyword2", "Keyword3"],
            "Corrective Actions": ["Keyword1", "Keyword2", "Keyword3"],
            "Similar Events": ["Keyword1", "Keyword2"]
        }}
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in extracting structured information from complex texts for efficient graph-based search."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=500
        )
        return json.loads(response["choices"][0]["message"]["content"])
    except Exception as e:
        print(f"Error: {e}")
        return None


# Initialize a list to store knowledge graph nodes
knowledge_graph = []

# Iterate over rows in the DataFrame
for i, row in tqdm(ler_df.iterrows(), total=len(ler_df), desc="Processing rows"):
    # Combine relevant columns into a single text input
    combined_text = " ".join(
        str(row.get(col, "")) for col in ["Title", "Abstract", "Narrative"]
    )

    # Extract attributes using GPT
    attributes = extract_attributes(combined_text)

    if attributes:
        # Ensure all attributes are filled with default values if missing
        attributes = {
            "Task": attributes.get("Task", "Unknown"),
            "Event": attributes.get("Event", "Unknown"),
            "Cause": attributes.get("Cause", "Unknown"),
            "Influence": attributes.get("Influence", "Unknown"),
            "Corrective Actions": attributes.get("Corrective Actions", "None"),
            "Similar Events": attributes.get("Similar Events", "None")
        }

        # Get additional metadata
        clause = row.get("CFR", "None")

        # Create a node for the knowledge graph
        node = {
            "filename": row.get("File Name", ""),
            "attributes": attributes,
            "metadata": {
                "facility": {
                    "name": row.get("Facility Name", "Unknown Facility"),
                    "unit": row.get("Unit", "Unknown Unit")
                },
                "event_date": row.get("Event Date", ""),
                "title": row.get("Title", ""),
                "clause": row.get("CFR", "None")
            }
        }

        # Append node to the knowledge graph
        knowledge_graph.append(node)

        # Optionally, stream save each node (for large datasets)
        with open(OUTPUT_JSON_PATH, "a", encoding="utf-8") as json_file:
            json.dump(node, json_file, indent=4, ensure_ascii=False)
            json_file.write(",\n")  # Add a separator for multiple nodes

# Save the complete knowledge graph to JSON
with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as json_file:
    json.dump(knowledge_graph, json_file, indent=4, ensure_ascii=False)

print(f"\nKnowledge graph saved to {OUTPUT_JSON_PATH}.")
