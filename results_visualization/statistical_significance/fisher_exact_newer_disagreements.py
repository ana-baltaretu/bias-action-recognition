import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import combinations
from collections import Counter
from scipy.stats import fisher_exact
import numpy as np
import os

# --- Configuration ---
model_name = "tc_clip"  # slowfast_r50, mvit_base_16x4, tc_clip
file_path = f"../model_results/top_20_kinetics_actions/filtered_best_background_and_camera_{model_name}.csv"
output_dir = "significance_outputs"
os.makedirs(output_dir, exist_ok=True)

# --- Load and prepare data ---
df = pd.read_csv(file_path)
df['base_video'] = df['video'].str.extract(r'^(.*?)(_modified|_initial)')[0]
video_data = df[['video', 'mapped_prediction', 'skin_color_category', 'base_video']].copy()

skin_colors = video_data['skin_color_category'].dropna().unique().tolist()

# --- Build disagreement matrix per base video ---
disagreement_matrix = []

for base_video, group in video_data.groupby('base_video'):
    preds = group[['mapped_prediction', 'skin_color_category']]
    disagreement_counts = {color: 0 for color in skin_colors}

    for a, b in combinations(preds.iterrows(), 2):
        _, row_a = a
        _, row_b = b
        if row_a['mapped_prediction'] != row_b['mapped_prediction']:
            disagreement_counts[row_a['skin_color_category']] += 1
            disagreement_counts[row_b['skin_color_category']] += 1

    disagreement_matrix.append(disagreement_counts)

disagreement_df = pd.DataFrame(disagreement_matrix)
binary_df = (disagreement_df > 0).astype(int)

# --- Fisher's exact tests ---
results = []

for color1, color2 in combinations(skin_colors, 2):
    a = binary_df[color1].sum()
    b = len(binary_df) - a
    c = binary_df[color2].sum()
    d = len(binary_df) - c

    table = [[a, b], [c, d]]
    odds_ratio, p_value = fisher_exact(table)

    results.append({
        "skin_color_1": color1,
        "skin_color_2": color2,
        "p_value": p_value,
        "odds_ratio": odds_ratio
    })

# --- Bonferroni correction ---
results_df = pd.DataFrame(results)
num_tests = len(results_df)
results_df["adjusted_p_value"] = results_df["p_value"] # * num_tests
results_df["adjusted_p_value"] = results_df["adjusted_p_value"].clip(upper=1.0)
results_df["significant"] = results_df["adjusted_p_value"] < 0.05
results_df["pair"] = results_df["skin_color_1"] + " vs " + results_df["skin_color_2"]

# --- Save results to CSV ---
results_df.to_csv(os.path.join(output_dir, f"pairwise_significance_{model_name}.csv"), index=False)

# --- Prepare matrix for heatmap ---
heatmap_matrix = pd.DataFrame(
    np.ones((len(skin_colors), len(skin_colors))),
    index=skin_colors,
    columns=skin_colors
)

for _, row in results_df.iterrows():
    c1 = row["skin_color_1"]
    c2 = row["skin_color_2"]
    p = row["adjusted_p_value"]
    heatmap_matrix.loc[c1, c2] = p
    heatmap_matrix.loc[c2, c1] = p

binary_matrix = heatmap_matrix < 0.05

# --- Plot heatmap ---
plt.figure(figsize=(8, 6))
sns.heatmap(
    binary_matrix,
    annot=heatmap_matrix.round(2),
    fmt="",
    cmap=sns.color_palette(["skyblue", "crimson"]),
    cbar=False,
    linewidths=0.5,
    linecolor='gray',
    mask=np.tril(np.ones_like(binary_matrix, dtype=bool))
)
plt.title("Significant Differences in Disagreement Involvement (Bonferroni-adjusted)")
plt.tight_layout()

# Save and show
plot_path = os.path.join(output_dir, f"pairwise_significance_{model_name}.png")
plt.savefig(plot_path)
plt.show()

print(f"Saved results to {plot_path} and corresponding CSV.")
