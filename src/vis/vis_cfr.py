import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap

# Step 1: Load the file
file_path = '../../data/processed/3_ler_cfr.csv'
ler_data = pd.read_csv(file_path)

# Step 2: Expand CFR values into individual entries
cfr_expanded = ler_data['CFR'].str.split(',').sum()
cfr_expanded = [cfr.strip() for cfr in cfr_expanded]  # Remove extra spaces

# Step 3: Calculate frequency of each CFR entry
cfr_counts = pd.Series(cfr_expanded).value_counts()

# Step 4: Plot the distribution as a pie chart with custom colors
plt.figure(figsize=(10, 8))
colors = get_cmap('Pastel1').colors  # Use a pastel colormap for softer colors

# Plot with customized properties
wedges, texts, autotexts = plt.pie(
    cfr_counts, 
    labels=cfr_counts.index, 
    autopct='%1.1f%%', 
    startangle=90, 
    colors=colors, 
    textprops={'fontsize': 10}  # Adjust text font size
)

# Adjust text position to prevent overlap
for text in texts:
    text.set_fontsize(9)
for autotext in autotexts:
    autotext.set_fontsize(9)

plt.title('Distribution of CFR Provisions', fontsize=14)
plt.tight_layout()
plt.show()
