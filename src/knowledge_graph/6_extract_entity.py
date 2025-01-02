import json
import os
import re
import pandas as pd
import openai
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables for API keys
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# File paths
LER_DF_PATH = "../../data/processed/2_ler_df_filtered.csv"  # Path to LER data CSV
CLAUSE_CSV_PATH = "../../data/processed/3_ler_cfr.csv"
OUTPUT_JSON_PATH = "../../data/processed/ler_knowledge_graph_with_clause.json"  # Output JSON file

# Read data
ler_df = pd.read_csv(LER_DF_PATH, encoding="utf-8")
clause_df = pd.read_csv(CLAUSE_CSV_PATH, encoding="utf-8")

ler_df = pd.merge(ler_df, clause_df, left_on="File Name", right_on="filename", how="left")

# Debugging: Display a sample of the merged data
print("\nSample of the merged data:")
print(ler_df.head())

# Define a function to extract attributes using GPT
def extract_attributes(text):
    try:
        # GPT prompt for concise incident analysis
        messages = [
            {"role": "system", "content": "You are an expert in analyzing incidents and extracting key attributes."},
            {"role": "user", "content": f"""
            Extract the following attributes from the provided incident description:

            - Event: What happened?
            - Cause: Why did it happen?
            - Influence: What was the impact?
            - Corrective Actions: What actions were taken to resolve it?
            - Similar Events: Any similar events reported?

            Text: \"{text}\"

            Respond in JSON format.
            """},
        ]

        # Call OpenAI GPT API
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.3,
            max_tokens=1500,
            top_p=0.8,
            frequency_penalty=0.2,
            presence_penalty=0.0
        )

        return json.loads(response["choices"][0]["message"]["content"])
    except Exception as e:
        print(f"GPT API error occurred: {e}")
        return None


# Initialize a list to store knowledge graph nodes
knowledge_graph = []

# Iterate over each row in the DataFrame
# Iterate over each row in the DataFrame
for i, row in tqdm(ler_df.iterrows(), total=len(ler_df), desc="Processing rows"):
    # Combine relevant columns to create the text input for GPT
    combined_text = " ".join(
        str(row.get(col, "")) for col in ["Title", "Abstract", "Narrative"]  # Include Title
    )

    # Extract attributes from the text using GPT
    attributes = extract_attributes(combined_text)

    if attributes:
        # Fill missing attributes with defaults
        attributes = {
            "Event": attributes.get("Event", "Unknown"),
            "Cause": attributes.get("Cause", "Unknown"),
            "Influence": attributes.get("Influence", "Unknown"),
            "Corrective Actions": attributes.get("Corrective Actions", "None"),
            "Similar Events": attributes.get("Similar Events", "None")
        }
        clause = row.get("CFR", "None")

        # Create a node for the knowledge graph
        node = {
            "filename": row.get("File Name", ""),  # Unique identifier for the file
            "attributes": attributes,  # Extracted attributes
            "metadata": {
                "facility": row.get("Facility Name", ""),
                "event_date": row.get("Event Date", ""),
                "title": row.get("Title", ""),
                "clause": clause  # Add clause to metadata
            }
        }
        knowledge_graph.append(node)

        # Optional: Stream save each node (for large datasets)
        with open(OUTPUT_JSON_PATH, "a", encoding="utf-8") as json_file:
            json.dump(node, json_file, indent=4, ensure_ascii=False)
            json_file.write(",\n")  # Add separator for multiple nodes


print(f"\nKnowledge graph saved to {OUTPUT_JSON_PATH}.")
