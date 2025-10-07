import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import combinations
from scipy.stats import fisher_exact
import numpy as np
import matplotlib.colors as mcolors

# Load your data
experiment_name = "top_20_kinetics_actions"
model_name = "slowfast_r50" # slowfast_r50, mvit_base_16x4, tc_clip
file_path = f"../model_results/{experiment_name}/filtered_best_background_and_camera_{model_name}.csv"
df = pd.read_csv(file_path)

# Extract base video name
df['base_video'] = df['video'].str.extract(r'^(.*?)(_modified|_initial)')[0]

# Define all skin colors
skin_colors = [
    "white", "african", "asian", "hispanic", "indian",
    "middle_eastern", "south_east_asian"
]

# For each base_video, compare all predictions and record which skin colors disagreed
skin_colors_changed = []

for base_video, group in df.groupby('base_video'):
    preds = group[['mapped_prediction', 'skin_color_category']]
    disagreed_colors = set()
    for a, b in combinations(preds.itertuples(index=False), 2):
        if a.mapped_prediction != b.mapped_prediction:
            disagreed_colors.update([a.skin_color_category, b.skin_color_category])
    skin_colors_changed.append({
        'base_video': base_video,
        'skin_colors_changed': ', '.join(disagreed_colors)
    })

# Create a DataFrame from disagreement records
divergence_df = pd.DataFrame(skin_colors_changed)

# Create binary columns for each skin color
for color in skin_colors:
    divergence_df[color] = divergence_df["skin_colors_changed"].apply(
        lambda x: int(color in [c.strip() for c in x.split(",")])
    )

# Perform pairwise Fisher's Exact tests
results = []
for color1, color2 in combinations(skin_colors, 2):
    a = divergence_df[color1].sum()
    b = len(divergence_df) - a
    c = divergence_df[color2].sum()
    d = len(divergence_df) - c

    table = [[a, b], [c, d]]
    odds_ratio, p_value = fisher_exact(table)

    results.append({
        "skin_color_1": color1,
        "skin_color_2": color2,
        "p_value": p_value,
        "odds_ratio": odds_ratio
    })

# Adjust p-values
results_df = pd.DataFrame(results)
num_tests = len(results_df)
results_df["adjusted_p_value"] = results_df["p_value"] #* num_tests
results_df["adjusted_p_value"] = results_df["adjusted_p_value"].clip(upper=1.0)
results_df["significant"] = results_df["adjusted_p_value"] < 0.05
results_df["pair"] = results_df["skin_color_1"] + " vs " + results_df["skin_color_2"]

# Print summary table
print(results_df[["pair", "p_value", "adjusted_p_value", "significant"]])

# --- Plot bar chart ---
plt.figure(figsize=(12, 6))
sns.barplot(
    x="pair",
    y="adjusted_p_value",
    hue="significant",
    data=results_df,
    dodge=False,
    palette={True: "crimson", False: "skyblue"}
)
plt.axhline(0.05, linestyle='--', color='gray')
plt.xticks(rotation=90)
plt.title("Pairwise Fisher's Exact Tests on Prediction Divergence (Bonferroni-adjusted)")
plt.ylabel("Adjusted p-value")
plt.xlabel("Skin Color Pair")
plt.tight_layout()
plt.show()

# --- Plot heatmap ---
# Create square matrix
heatmap_matrix = pd.DataFrame(
    np.ones((len(skin_colors), len(skin_colors))),
    index=skin_colors,
    columns=skin_colors
)

# Fill it with adjusted p-values
for _, row in results_df.iterrows():
    c1 = row["skin_color_1"]
    c2 = row["skin_color_2"]
    p = row["adjusted_p_value"]
    heatmap_matrix.loc[c1, c2] = p
    heatmap_matrix.loc[c2, c1] = p

# Create binary mask for significance
binary_matrix = heatmap_matrix < 0.05

# Plot
plt.figure(figsize=(8, 6))
sns.heatmap(
    binary_matrix,
    annot=heatmap_matrix.round(2),
    fmt="",
    cmap=mcolors.ListedColormap(["skyblue", "crimson"]),
    cbar=False,
    linewidths=0.5,
    linecolor='gray',
    mask=np.tril(np.ones_like(binary_matrix, dtype=bool))
)
plt.title("Significant Differences in Prediction Divergence (Bonferroni-adjusted)")
plt.tight_layout()
plt.savefig(f"pairwise_significance_{model_name}.png")
plt.show()
