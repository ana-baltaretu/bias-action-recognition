import pandas as pd
from scipy.stats import fisher_exact
from itertools import combinations
import matplotlib.pyplot as plt
import seaborn as sns

# What this test asks:
# "Is white involved in significantly more prediction-changing instances than african, across the whole dataset?"

# Load your data
experiment_name = "top_20_kinetics_actions" # older_runs, top_20_kinetics_actions
model_name = "tc_clip" # mvit_base_16x4, slowfast_r50, tc_clip
df = pd.read_csv(f"../model_results/{experiment_name}/filtered_best_background_and_camera_{model_name}.csv")

# Define all skin colors
skin_colors = [
    "white", "african", "asian", "hispanic", "indian",
    "middle_eastern", "south_east_asian"
]

# Create binary columns indicating whether each skin color appeared in 'skin_colors_changed'
for color in skin_colors:
    df[color] = df["skin_colors_changed"].fillna("").apply(
        lambda x: int(color in [c.strip() for c in x.split(",")])
    )

# Perform pairwise Fisher's Exact tests
results = []
for color1, color2 in combinations(skin_colors, 2):
    a = df[color1].sum()
    b = len(df) - a
    c = df[color2].sum()
    d = len(df) - c

    table = [[a, b], [c, d]]
    odds_ratio, p_value = fisher_exact(table)

    results.append({
        "skin_color_1": color1,
        "skin_color_2": color2,
        "p_value": p_value,
        "odds_ratio": odds_ratio
    })

# Convert to DataFrame and apply Bonferroni correction
results_df = pd.DataFrame(results)
num_tests = len(results_df)
results_df["adjusted_p_value"] = results_df["p_value"] * num_tests
results_df["adjusted_p_value"] = results_df["adjusted_p_value"].clip(upper=1.0)
results_df["significant"] = results_df["adjusted_p_value"] < 0.05
results_df["pair"] = results_df["skin_color_1"] + " vs " + results_df["skin_color_2"]

print(results_df[["skin_color_1", "skin_color_2", "p_value", "adjusted_p_value", "significant"]])

# Plot
plt.figure(figsize=(12, 6))
sns.barplot(
    x="pair",
    y="adjusted_p_value",
    hue="significant",
    data=results_df,
    dodge=False,
    palette={True: "crimson", False: "skyblue"}
)

plt.axhline(0.05, linestyle='--', color='gray', label='p = 0.05')
plt.xticks(rotation=90)
plt.title("Pairwise Fisher's Exact Tests on Prediction Divergence (Bonferroni-adjusted)")
plt.ylabel("Adjusted p-value")
plt.xlabel("Skin Color Change Pair")
plt.legend(title="Significant (p < 0.05)")
plt.tight_layout()
plt.show()


import numpy as np

# Create a square matrix of adjusted p-values
heatmap_matrix = pd.DataFrame(
    np.ones((len(skin_colors), len(skin_colors))),
    index=skin_colors,
    columns=skin_colors
)

# Fill in the matrix with adjusted p-values
for _, row in results_df.iterrows():
    c1 = row["skin_color_1"]
    c2 = row["skin_color_2"]
    p = row["adjusted_p_value"]
    heatmap_matrix.loc[c1, c2] = p
    heatmap_matrix.loc[c2, c1] = p  # symmetric


import matplotlib.colors as mcolors

# Define binary values: 1 = significant, 0 = not
binary_matrix = heatmap_matrix < 0.05

# Define a discrete color map
cmap = mcolors.ListedColormap(["skyblue", "crimson"])

# Plot using the binary matrix for color, but annotate with actual p-values
plt.figure(figsize=(8, 6))
sns.heatmap(
    binary_matrix,  # determines color (0 or 1)
    annot=heatmap_matrix.round(2),  # show actual p-values
    fmt="",
    cmap=cmap,
    cbar=False,
    linewidths=0.5,
    linecolor='gray',
    mask=np.tril(np.ones_like(binary_matrix, dtype=bool))  # lower triangle mask
)
plt.title("Significant Differences in Prediction Divergence (Bonferroni-adjusted)")
plt.tight_layout()
plt.savefig(f"pairwise_significance_{model_name}")
plt.show()