import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load the transitions
model_name = "tc_clip" # mvit_base_16x4, slowfast_r50, tc_clip
df = pd.read_csv(f"correct_to_wrong_transitions_{model_name}.csv")

# Pivot into matrix: rows = from, columns = to, values = count
heatmap_data = df.groupby(['from', 'to']).size().unstack(fill_value=0)


# Sort consistently
skin_colors = ['white', 'african', 'asian', 'hispanic', 'indian', 'middle_eastern', 'south_east_asian']
heatmap_data = heatmap_data.reindex(index=skin_colors, columns=skin_colors)
heatmap_data = heatmap_data.fillna(0).astype(int)

# Plot
plt.figure(figsize=(10, 8))
sns.heatmap(
    heatmap_data.astype(int),
    annot=True,
    fmt="d",
    cmap="Reds",
    vmin=0,
    vmax=15,
    cbar_kws={'label': 'Mistake Count'}
)
plt.title("Correct → Wrong Transitions\n(from → to skin color)")
plt.xlabel("To Skin Color (Target)")
plt.ylabel("From Skin Color (Original)")
plt.tight_layout()
plt.savefig(f"skin_color_transition_heatmap_{model_name}.png")
plt.show()
