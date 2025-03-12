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
LER_DF_PATH = "../../data/processed/2_updated_ler_df.csv"  # 2_updated_ler_df
CLAUSE_CSV_PATH = "../../data/processed/3_ler_cfr.csv"  # 3_ler_cfr.csv
OUTPUT_JSON_PATH = "../../data/processed/0120_kg_procedure.json"  # Output JSON file

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
        You are an expert in analyzing nuclear power plant operations, particularly focusing on procedure interactions in Light Water Reactors (LWRs). Your task is to extract structured information regarding **procedure conflicts and insufficiencies** from the provided text.

        Definitions:
        - **Conflicting Procedures**: Identify the procedures that were involved in the conflict.
        - **Conflict Areas**: Specify the operational or functional areas where the conflict occurred.
        - **Conflict Reason**: Identify why the procedures conflicted, such as sequencing issues, resource constraints, or operational inconsistencies.
        - **Insufficient Procedures**: Identify procedures that were found to be incomplete, unclear, or inadequate.
        - **Impact**: Describe the consequence of the procedural conflict or insufficiency on plant safety, operations, or efficiency.
        - **Resolution Actions**: Describe the corrective actions taken to resolve the conflict or address the insufficiency.

        Incident Description:
        "{text}"

        Respond strictly in JSON format:
        {{
            "Conflicting Procedures": ["Procedure1", "Procedure2"],
            "Conflict Areas": ["GeneralKeyword1"],
            "Conflict Reason": ["GeneralKeyword1"],
            "Insufficient Procedures": ["Procedure3"],
            "Impact": ["GeneralKeyword1"],
            "Resolution Actions": ["GeneralKeyword1"]
        }}
        """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in extracting structured and generalized information from complex texts for efficient pattern detection and risk analysis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=200
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
            "Conflicting Procedures": attributes.get("Conflicting Procedures", []),
            "Insufficient Procedures": attributes.get("Insufficient Procedures", []),
            "Task": attributes.get("Task", ["Unknown"]),
            "Conflict Reason": attributes.get("Conflict Reason", ["Unknown"]),
            "Impact": attributes.get("Impact", ["Unknown"]),
            "Resolution Actions": attributes.get("Resolution Actions", ["None"]),
            "Incident Description": attributes.get("Incident Description", "No description provided")
        }

        # Get additional metadata
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

# Save the complete knowledge graph to JSON
with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as json_file:
    json.dump(knowledge_graph, json_file, indent=4, ensure_ascii=False)

print(f"\nKnowledge graph saved to {OUTPUT_JSON_PATH}.")
