import pandas as pd

CSV_PATH = "../../data/processed/ler_df.csv"  # Path to the CSV file
OUTPUT_FILTERED_CSV = "../../data/processed/ler_df_filtered.csv"  # Filtered CSV output path

df = pd.read_csv(CSV_PATH, encoding="utf-8")

# df.eq("Not Found") creates a DataFrame of True/False values (True where cell is "Not Found")
# any(axis=1) returns True if any "Not Found" value appears in the row
not_found_mask = df.eq("Not Found").any(axis=1)

# Count how many rows contain at least one "Not Found"
#count_not_found_rows = not_found_mask.sum()
#print("Number of rows containing at least one 'Not Found':", count_not_found_rows)

# Remove rows that contain "Not Found"
filtered_df = df[~not_found_mask]

# Count the remaining rows (filtered rows)
remaining_rows_count = len(filtered_df)
print("Number of remaining data points after filtering:", remaining_rows_count)

# Save the filtered DataFrame to a new CSV file
filtered_df.to_csv(OUTPUT_FILTERED_CSV, index=False, encoding="utf-8")
print("Filtered CSV saved to:", OUTPUT_FILTERED_CSV)
