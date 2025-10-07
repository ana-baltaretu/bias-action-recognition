import pandas as pd
from itertools import product
import seaborn as sns
import matplotlib.pyplot as plt

# Step 1: Load and process
model_name = "tc_clip" # mvit_base_16x4, slowfast_r50, tc_clip
df = pd.read_csv(f"prediction_divergence_summary_{model_name}.csv")

rows = []
for _, row in df.iterrows():
    from_colors = [c.strip() for c in row['skin_colors_same'].split(',') if c.strip()]
    to_colors = [c.strip() for c in row['skin_colors_changed'].split(',') if c.strip()]
    for from_sc, to_sc in product(from_colors, to_colors):
        rows.append({'from_skin': from_sc, 'to_skin': to_sc})

transitions = pd.DataFrame(rows)
transition_counts = transitions.groupby(['from_skin', 'to_skin']).size().reset_index(name='count')
# transition_counts.to_csv("skin_color_prediction_transition_counts.csv", index=False)
# print("Saved: skin_color_prediction_transition_counts.csv")

# Step 2: Create pivot with consistent ordering
skin_order = ['white', 'african', 'asian', 'hispanic', 'indian', 'middle_eastern', 'south_east_asian']

pivot = (
    transition_counts
    .pivot(index='from_skin', columns='to_skin', values='count')
    .reindex(index=skin_order, columns=skin_order)
    .fillna(0)
    .astype(int)
)

# Step 3: Plot
plt.figure(figsize=(10, 8))
sns.heatmap(
    pivot,
    annot=True,
    fmt='d',
    cmap='Oranges',
    vmin=0,
    vmax=45,
    cbar_kws={'label': 'Prediction Changes'}
)
plt.title("Skin Color Transitions Causing Prediction Changes")
plt.xlabel("To Skin Color (Modified)")
plt.ylabel("From Skin Color (Original)")
plt.tight_layout()
plt.savefig(f"skin_color_transition_heatmap_by_prediction_change_{model_name}.png")
plt.show()
