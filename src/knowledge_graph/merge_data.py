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
LER_DF_PATH = "../../data/processed/2_ler_df_filtered_mini.csv"  # Path to first CSV
LER_CFR_PATH = "../../data/processed/3_ler_cfr.csv"  # Path to second CSV
CFR_PATH = "../../data/processed/3_cfr.csv"  # Path to CFR description CSV
OUTPUT_MERGED_CSV = "../../data/processed/4_merged.csv" 

# Read data
ler_data = pd.read_csv(LER_DF_PATH, encoding="Windows-1252")
ler_cfr_data = pd.read_csv(LER_CFR_PATH, encoding="Windows-1252")
cfr_data = pd.read_csv(CFR_PATH, encoding="Windows-1252")

# Filter rows where "File Name" matches between ler_data and ler_cfr_data
common_files = set(ler_data["File Name"]).intersection(set(ler_cfr_data["filename"]))
merged_data = ler_data[ler_data["File Name"].isin(common_files)]

# Merge ler_cfr_data based on filename
merged_data = pd.merge(merged_data, ler_cfr_data, left_on="File Name", right_on="filename", how="inner")

# Merge CFR data based on CFR column
merged_data = pd.merge(merged_data, cfr_data, on="CFR", how="left")

# Debugging output
print("\nMerged data (sample):")
print(merged_data.head())

try:
    merged_data.to_csv(OUTPUT_MERGED_CSV, index=False, encoding="utf-8")
    print(f"CSV successfully saved at {OUTPUT_MERGED_CSV}")
except Exception as e:
    print(f"Error occurred while saving CSV: {e}")
