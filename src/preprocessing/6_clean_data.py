import pandas as pd

# Load the CSV file
file_path = "../../data/processed/2_ler_df_filtered_checked.csv"
df = pd.read_csv(file_path)

# Split the 'Facility Name' column into 'Facility Name' and 'Unit'
df[['Facility Name', 'Unit']] = df['Facility Name'].str.extract(r'^(.*?)(?:,\s*(Unit\s*\d+))?$')

# Fill missing values with defaults
df['Facility Name'].fillna('Unknown Facility', inplace=True)
df['Unit'].fillna('Unknown Unit', inplace=True)

# Save the updated DataFrame back to a CSV file
output_path = "../../data/processed/updated_ler_df.csv"
df.to_csv(output_path, index=False)

print(f"Updated CSV file saved to {output_path}.")
