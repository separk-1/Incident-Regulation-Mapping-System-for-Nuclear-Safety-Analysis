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
OUTPUT_JSON_PATH = "../../data/processed/01030941_ler_kg_hsi_keywords.json"  # Output JSON file

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
        You are an expert in extracting structured and generalized information. Extract the following attributes as **generalized and abstract keywords** from the provided text.

        Definitions:
        - **Task**: What specific work, activity, or operation was being performed when the incident occurred? Summarize it with **one general keyword**.
        - **Event**: What happened during the incident? Summarize it with **one abstract and broad keyword**.
        - **Cause**: What was the primary cause of the incident? Summarize it with **one general keyword**.
        - **Influence**: What was the key impact or consequence of the incident? Summarize it with **one broad keyword**.
        - **Corrective Actions**: What corrective actions were taken after the incident? Summarize it with **one generalized keyword**.
        - **HSI Issues**: Identify specific issues or challenges related to Human-System Interfaces (HSI) in this incident, e.g., "Ambiguous Interface", "Poor Visualization", "Inadequate Feedback".
        - **Similar Events**: Are there known similar events? Provide **a general keyword** or leave as an empty list `[]` if no similar events are known.

        Incident Description:
        "{text}"

        Respond strictly in JSON format:
        {{
            "Task": ["GeneralKeyword1"],
            "Event": ["GeneralKeyword1"],
            "Cause": ["GeneralKeyword1"],
            "Influence": ["GeneralKeyword1"],
            "Corrective Actions": ["GeneralKeyword1"],
            "HSI Issues": ["Issue1", "Issue2"],
            "Similar Events": []
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
            "Task": attributes.get("Task", ["Unknown"]),
            "Event": attributes.get("Event", ["Unknown"]),
            "Cause": attributes.get("Cause", ["Unknown"]),
            "Influence": attributes.get("Influence", ["Unknown"]),
            "Corrective Actions": attributes.get("Corrective Actions", ["None"]),
            "HSI Issues": attributes.get("HSI Issues", []),  # Changed to return []
            "Similar Events": attributes.get("Similar Events", [])
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
