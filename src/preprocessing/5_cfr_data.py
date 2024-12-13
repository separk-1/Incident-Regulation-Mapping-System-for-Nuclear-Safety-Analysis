import pandas as pd
import re
import os

# Set paths
CSV_PATH = "../../data/processed/ler_cfr.csv"
CFR_OUTPUT_PATH =  "../../data/processed/cfr_empty.csv"

df = pd.read_csv(CSV_PATH, encoding="utf-8")

# Combine all CFR items into a single list
all_cfr = []
for val in df["CFR"].dropna():
    # Split val by commas and remove whitespace
    items = [c.strip() for c in val.split(",")]
    all_cfr.extend(items)

# Remove duplicates using set
unique_cfr = list(set(all_cfr))

print("Unique CFR list:", unique_cfr)

# Create a new DataFrame for CFR and content
cfr_df = pd.DataFrame({
    "CFR": unique_cfr,  # Add the unique CFR list as the CFR column
    "Content": [""] * len(unique_cfr)  # Initialize the Content column with empty strings
})

# Save the new DataFrame to a CSV file
cfr_df.to_csv(CFR_OUTPUT_PATH, index=False, encoding="utf-8")

print(f"CFR CSV created and saved to: {CFR_OUTPUT_PATH}")
print(cfr_df.head())  # Display the first few rows of the new CSV file for verification

'''
Columns: cfr, content. The "cfr" column contains the unique CFR values, and the "content" column will hold their corresponding descriptions.
'''
