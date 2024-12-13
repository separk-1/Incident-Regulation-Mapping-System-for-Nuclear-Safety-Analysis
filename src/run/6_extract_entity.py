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
LER_DF_PATH = "../../data/processed/ler_df_filtered.csv"  # Path to first CSV
LER_CFR_PATH = "../../data/processed/ler_cfr.csv"  # Path to second CSV
CFR_PATH = "../../data/processed/cfr.csv"  # Path to CFR description CSV
OUTPUT_JSON = "../../data/processed/knowledge_graph.json"  # Output JSON path

# Read data
ler_data = pd.read_csv(LER_DF_PATH)
ler_cfr_data = pd.read_csv(LER_CFR_PATH)
cfr_data = pd.read_csv(CFR_PATH)

# Filter rows where "File Name" matches between ler_data and ler_cfr_data
common_files = set(ler_data["File Name"]).intersection(set(ler_cfr_data["filename"]))
filtered_data = ler_data[ler_data["File Name"].isin(common_files)]

# Merge ler_cfr_data based on filename
filtered_data = pd.merge(filtered_data, ler_cfr_data, left_on="File Name", right_on="filename", how="inner")

# Merge CFR data based on CFR column
filtered_data = pd.merge(filtered_data, cfr_data, on="CFR", how="left")

# Debugging output
print("\nFiltered data after merging (sample):")
print(filtered_data.head())

def extract_attributes(text):
    try:
        messages = [
            {"role": "system", "content": "You are an expert in incident analysis and attribute extraction."},
            {"role": "user", "content": f"""
            Analyze the following text and extract the following attributes:

            - Event: Key events that occurred.
            - Cause: The cause or reasons for the event.
            - Influence: The influence or impact of the event.
            - Corrective Actions: Actions taken to address the issue.
            - Similar Events: Similar events reported in the past.
            - Guideline: Procedures or guidelines referenced.
            - Clause: Specific clauses or rules cited.

            Text: \"{text}\"

            Output the results in JSON format with keys matching the attributes listed above.
            """},
        ]

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.5,
            max_tokens=1200,
        )
        return json.loads(response["choices"][0]["message"]["content"])
    except Exception as e:
        print(f"GPT API error occurred: {e}")
        return None

def cluster_by_cfr(filename, attributes, cfr_hierarchy):
    cluster = {
        "filename": filename,
        "cfr": {
            "content_1": cfr_hierarchy.get("content_1", ""),
            "content_2": cfr_hierarchy.get("content_2", ""),
            "content_3": cfr_hierarchy.get("content_3", ""),
            "content_4": cfr_hierarchy.get("content_4", "")
        },
        "attributes": attributes
    }
    return cluster

knowledge_clusters = []

for i, row in tqdm(filtered_data.iterrows(), total=len(filtered_data), desc="Processing rows"):
    # Combine text from selected columns
    combined_text = " ".join(
        str(row.get(col, "")) for col in ["Abstract", "Narrative"]
    )

    extracted_attributes = extract_attributes(combined_text)

    if extracted_attributes:
        cfr_hierarchy = {
            "content_1": row.get("content_1", ""),
            "content_2": row.get("content_2", ""),
            "content_3": row.get("content_3", ""),
            "content_4": row.get("content_4", "")
        }
        cluster = cluster_by_cfr(row.get("filename", ""), extracted_attributes, cfr_hierarchy)
        knowledge_clusters.append(cluster)

print("\nKnowledge Clusters (sample):")
print(knowledge_clusters[:3])

# Save results to JSON
with open(OUTPUT_JSON, "w", encoding="utf-8") as json_file:
    json.dump(knowledge_clusters, json_file, indent=4, ensure_ascii=False)

print(f"\nKnowledge clusters saved to {OUTPUT_JSON}.")
