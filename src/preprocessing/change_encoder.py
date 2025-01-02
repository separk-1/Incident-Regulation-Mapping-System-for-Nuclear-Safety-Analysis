import pandas as pd

input_file = "../../data/processed/3_cfr.csv"
output_file = "../../data/processed/3_cfr.csv"

data = pd.read_csv(input_file, encoding='Windows-1252')

data.to_csv(output_file, index=False, encoding='utf-8')

print(f"File has been re-encoded and saved to {output_file}")
