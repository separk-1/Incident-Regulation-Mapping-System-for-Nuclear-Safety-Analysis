import pandas as pd
import re
import os

# 경로 설정
CFR_TEXT_PATH = "../../data/raw/cfr/50_73.txt"
CSV_PATH = "../../data/processed/ler_cfr.csv"
CFR_OUTPUT_PATH =  "../../data/processed/cfr.csv"

df = pd.read_csv(CSV_PATH, encoding="utf-8")

# 모든 CFR 항목을 하나의 리스트로 합치기
all_cfr = []
for val in df["CFR"].dropna():
    # val을 쉼표로 split 후 공백 제거
    items = [c.strip() for c in val.split(",")]
    all_cfr.extend(items)

# set을 사용해 중복 제거
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
col: cfr, content. cfr에는 unique_cfr를 넣고, content에는 cfr에 해당하는 설명
'''