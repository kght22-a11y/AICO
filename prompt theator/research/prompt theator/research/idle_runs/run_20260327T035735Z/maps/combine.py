import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load your data into a DataFrame (replace with your actual data)
# df = pd.read_csv('combine.txt')

# Generate the scatter plot
plt.figure(figsize=(12, 8), dpi=300)
sns.scatterplot(
    data=df,
    x='x', y='y',
    hue='model',
    palette='viridis',
    s=100,
    alpha=0.7,
    edgecolor='w'
)

# Add title and labels
plt.title('Scatter Map: Semantic Coordinates by Model', fontsize=16)
plt.xlabel('X (Semantic Coordinate)', fontsize=12)
plt.ylabel('Y (Semantic Coordinate)', fontsize=12)
plt.legend(title='Model', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, linestyle='--', alpha=0.6)

# Save the plot
plt.tight_layout()
plt.savefig('scatter_high_res.png', dpi=300, bbox_inches='tight')