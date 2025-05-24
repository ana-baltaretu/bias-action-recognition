import pandas as pd
from scipy.stats import fisher_exact
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.colors as mcolors
import numpy as np
from collections import defaultdict

# What this test asks:
# "Is changing from white → african significantly more likely to change predictions than from white → asian, etc.?"
# from white → african, white → asian

# Even though white → african has the highest raw count of prediction changes (36), it’s not statistically significant after Bonferroni correction, because:
#   White transitions overall have high numbers to many other skin tones.
#   The test compares TO = african vs all other TOs for the same FROM, so a large number needs to stand out relative to the rest.

# --- Load the input data ---
model_name = "mvit_base_16x4" # slowfast_r50, tc_clip, mvit_base_16x4
df = pd.read_csv(f"../video_results_with_skin_{model_name}.csv")

# Extract a "base video" identifier for grouping (e.g., cartwheel_0)
df["base_video"] = df["video"].str.extract(r"(.*?_\d+)_")[0]

# Define skin colors
skin_colors = ['white', 'african', 'asian', 'hispanic', 'indian', 'middle_eastern', 'south_east_asian']

# Initialize transition matrix
transition_matrix = pd.DataFrame(0, index=skin_colors, columns=skin_colors, dtype=int)

# Group by base video and calculate prediction changes
for base_video, group in df.groupby("base_video"):
    preds = group.set_index("skin_color_category")["mapped_prediction"].to_dict()

    for from_color in skin_colors:
        if from_color not in preds:
            continue
        base_pred = preds[from_color]
        for to_color in skin_colors:
            if to_color == from_color or to_color not in preds:
                continue
            if preds[to_color] != base_pred:
                transition_matrix.loc[from_color, to_color] += 1

# --- Perform directional Fisher's Exact Tests ---
results = []

for from_color in skin_colors:
    for to_color in skin_colors:
        if from_color == to_color:
            continue

        a = transition_matrix.loc[from_color, to_color]
        b = transition_matrix.loc[from_color].sum() - a
        c = transition_matrix[to_color].sum() - a
        d = transition_matrix.values.sum() - (a + b + c)

        table = [[a, b], [c, d]]
        odds_ratio, p_value = fisher_exact(table)

        results.append({
            "from": from_color,
            "to": to_color,
            "a": a,
            "b": b,
            "c": c,
            "d": d,
            "p_value": p_value,
            "odds_ratio": odds_ratio
        })

# --- Adjust p-values using Bonferroni correction ---
results_df = pd.DataFrame(results)
results_df["adjusted_p_value"] = results_df["p_value"] * len(results_df)
results_df["adjusted_p_value"] = results_df["adjusted_p_value"].clip(upper=1.0)
results_df["significant"] = results_df["adjusted_p_value"] < 0.05

# --- Pivot for heatmap plotting ---
heatmap_data = results_df.pivot(index="from", columns="to", values="adjusted_p_value")
binary_matrix = heatmap_data < 0.05

# --- Plot annotated heatmap with significance ---
cmap = mcolors.ListedColormap(["skyblue", "crimson"])
plt.figure(figsize=(10, 8))
sns.heatmap(
    binary_matrix,
    annot=heatmap_data.round(2),
    fmt="",
    cmap=cmap,
    cbar=False,
    linewidths=0.5,
    linecolor='gray'
)
plt.title("Significant Directional Differences in Prediction Changes (Bonferroni-adjusted)")
plt.xlabel("To Skin Color (Modified)")
plt.ylabel("From Skin Color (Original)")
plt.tight_layout()
plt.savefig(f"directional_pairwise_significance_{model_name}")
plt.show()