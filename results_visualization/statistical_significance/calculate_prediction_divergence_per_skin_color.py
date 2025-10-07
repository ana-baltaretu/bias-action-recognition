import pandas as pd
from collections import defaultdict
from itertools import combinations
from scipy.stats import fisher_exact, chi2_contingency
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load the CSV
model_name = "tc_clip"  # slowfast_r50, mvit_base_16x4, tc_clip, x3d_xs, slow_r50
file_path = f"../model_results/top_20_kinetics_actions/filtered_best_background_and_camera_{model_name}.csv"
df = pd.read_csv(file_path)

# Helper function to extract base video ID
def extract_video_id(filename):
    updated_filename = filename.replace("_initial", "_modified_").split("_modified_")[0]
    return updated_filename

# Build list of (video_id, skin_color, prediction)
predictions = [
    (extract_video_id(row["video"]), row["skin_color_category"], row["mapped_prediction"])
    for _, row in df.iterrows()
]

# Step 1: group predictions by video_id
video_preds = defaultdict(dict)
for video_id, skin_color, pred in predictions:
    video_preds[video_id][skin_color] = pred

# Step 2: initialize counters for each pair
divergence_counts = defaultdict(lambda: {"div": 0, "no_div": 0})

# Step 3: compare predictions pairwise
for preds in video_preds.values():
    for skin1, skin2 in combinations(preds.keys(), 2):
        pred1 = preds[skin1]
        pred2 = preds[skin2]
        pair = tuple(sorted([skin1, skin2]))
        if pred1 != pred2:
            divergence_counts[pair]["div"] += 1
        else:
            divergence_counts[pair]["no_div"] += 1

# Step 4: convert to DataFrame
divergence_df = pd.DataFrame([
    {
        "skin_color_1": pair[0],
        "skin_color_2": pair[1],
        "divergences": counts["div"],
        "no_divergences": counts["no_div"]
    }
    for pair, counts in divergence_counts.items()
])


# Save or inspect
print(divergence_df)
# divergence_df.to_csv("divergence_counts.csv", index=False)  # Optional: save to file


###################
###################
### ABOVE: Counted the amount of times skin color change => difference in predictions
###################
###################








# Step 1: Add divergence rate to the DataFrame (if not already added)
divergence_df["divergence_rate"] = divergence_df["divergences"] / (
    divergence_df["divergences"] + divergence_df["no_divergences"]
)

# Step 2: Create a string label for each pair
divergence_df["pair"] = divergence_df["skin_color_1"] + " & " + divergence_df["skin_color_2"]

# Step 3: Sort by divergence rate
divergence_df_sorted = divergence_df.sort_values("divergence_rate", ascending=False)

# Step 4: Plot
plt.figure(figsize=(12, 8))
sns.barplot(
    data=divergence_df_sorted,
    x="divergence_rate",
    y="pair",
    palette="viridis"
)
plt.xlabel("Divergence Rate", fontsize=14)
plt.ylabel("Skin Color Pair", fontsize=14)
plt.title("Prediction Divergence Rate per Skin Color Pair", fontsize=16)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.tight_layout()
plt.show()











# Step 1: Add divergence rate
divergence_df["divergence_rate"] = divergence_df["divergences"] / (
    divergence_df["divergences"] + divergence_df["no_divergences"]
)

# Step 2: Create symmetric matrix
all_colors = sorted(set(divergence_df["skin_color_1"]).union(divergence_df["skin_color_2"]))
rate_matrix = pd.DataFrame(index=all_colors, columns=all_colors, dtype=float)

for _, row in divergence_df.iterrows():
    c1 = row["skin_color_1"]
    c2 = row["skin_color_2"]
    rate = row["divergences"]
    rate_matrix.loc[c1, c2] = rate
    rate_matrix.loc[c2, c1] = rate  # make symmetric

# Step 3: Create mask for upper triangle
mask = np.triu(np.ones_like(rate_matrix, dtype=bool))

# Step 4: Plot
plt.figure(figsize=(10, 8))
sns.heatmap(rate_matrix, mask=mask, annot=True,
            fmt=".2f", cmap="coolwarm",
            vmin=10,  # lower bound of color scale
            vmax=46,  # upper bound of color scale
            linewidths=0.5)
plt.title("Divergence Rate Between Skin Color Pairs (Lower Triangle Only)")
plt.xlabel("Skin Color")
plt.ylabel("Skin Color")
plt.tight_layout()
plt.show()






#
# from scipy.stats import fisher_exact, chi2_contingency
#
#
# def test_significance_for_pair(df, target_pair):
#     # Extract values for the target pair
#     row = df[
#         ((df["skin_color_1"] == target_pair[0]) & (df["skin_color_2"] == target_pair[1])) |
#         ((df["skin_color_1"] == target_pair[1]) & (df["skin_color_2"] == target_pair[0]))
#         ].iloc[0]
#
#     a = row["divergences"]
#     b = row["no_divergences"]
#
#     # Aggregate all other pairs
#     others = df[
#         ~(
#                 ((df["skin_color_1"] == target_pair[0]) & (df["skin_color_2"] == target_pair[1])) |
#                 ((df["skin_color_1"] == target_pair[1]) & (df["skin_color_2"] == target_pair[0]))
#         )
#     ]
#
#     print(others)
#
#     c = others["divergences"].sum()
#     d = others["no_divergences"].sum()
#
#     contingency = [[a, b], [c, d]]
#
#     if min(min(row) for row in contingency) < 5:
#         stat, p = fisher_exact(contingency)
#         test = "Fisher"
#     else:
#         stat, p, _, _ = chi2_contingency(contingency)
#         test = "Chi-squared"
#
#     rate_pair = a / (a + b)
#     rate_others = c / (c + d)
#
#     return {
#         "pair": target_pair,
#         "p_value": p,
#         "test_used": test,
#         "pair_divergence_rate": rate_pair,
#         "others_divergence_rate": rate_others,
#         "contingency": contingency
#     }
#
#
# # Example usage:
# target = ("african", "white")
# result = test_significance_for_pair(divergence_df, target)
#
# print(f"\nSignificance test for pair {result['pair']}:")
# print(f"  Test used: {result['test_used']}")
# print(f"  p-value: {result['p_value']:.4f}")
# print(f"  Pair divergence rate: {result['pair_divergence_rate']:.2%}")
# print(f"  Others divergence rate: {result['others_divergence_rate']:.2%}")
# print(f"  Contingency table: {result['contingency']}")


from scipy.stats import fisher_exact, chi2_contingency


def test_significance_for_pair(df, target_pair):
    # Extract values for the target pair
    row = df[
        ((df["skin_color_1"] == target_pair[0]) & (df["skin_color_2"] == target_pair[1])) |
        ((df["skin_color_1"] == target_pair[1]) & (df["skin_color_2"] == target_pair[0]))
        ].iloc[0]

    a = row["divergences"]
    b = row["no_divergences"]

    # Aggregate all other pairs
    others = df[
        ~(
                ((df["skin_color_1"] == target_pair[0]) & (df["skin_color_2"] == target_pair[1])) |
                ((df["skin_color_1"] == target_pair[1]) & (df["skin_color_2"] == target_pair[0]))
        )
    ]

    c = others["divergences"].sum()
    d = others["no_divergences"].sum()

    contingency = [[a, b], [c, d]]

    if min(min(row) for row in contingency) < 5:
        stat, p = fisher_exact(contingency)
        test = "Fisher"
    else:
        stat, p, _, _ = chi2_contingency(contingency)
        test = "Chi-squared"

    rate_pair = a / (a + b)
    rate_others = c / (c + d)

    return {
        "pair": target_pair,
        "p_value": p,
        "test_used": test,
        "pair_divergence_rate": rate_pair,
        "others_divergence_rate": rate_others,
        "contingency": contingency
    }


all_pairs = list(zip(divergence_df["skin_color_1"], divergence_df["skin_color_2"]))
results = []

for pair in all_pairs:
    result = test_significance_for_pair(divergence_df, pair)
    # print(pair, result)
    results.append(result)

# Convert to DataFrame
significance_df = pd.DataFrame(results)

# Sort by p-value (most significant first)
significance_df = significance_df.sort_values(by="p_value")

# Print significant results (e.g., p < 0.05)
print("p < 0.05")
for _, row in significance_df.iterrows():
    if row['p_value'] < 0.05:
        print(f"{row['pair']}: p = {row['p_value']:.4f}")

from statsmodels.stats.multitest import multipletests

# Apply correction
pvals = significance_df["p_value"].values

# Choose method: "bonferroni" or "fdr_bh"
corrected = multipletests(pvals, alpha=0.05, method="fdr_bh")

# Add results to DataFrame
significance_df["p_corrected"] = corrected[1]
significance_df["significant"] = corrected[0]  # True if below corrected threshold
significance_df["correction_method"] = "fdr_bh"  # or "bonferroni"

# Optional: mark significance level with stars
def significance_stars(p):
    if p < 0.001: return "***"
    elif p < 0.01: return "**"
    elif p < 0.05: return "*"
    return ""

significance_df["significance_level"] = significance_df["p_corrected"].apply(significance_stars)

# View most significant
print(significance_df[significance_df["significant"]])

















import matplotlib.colors as mcolors

# Create matrix of corrected p-values
heatmap_matrix = pd.DataFrame(index=all_colors, columns=all_colors, dtype=float)

# Fill symmetric matrix with corrected p-values
for _, row in significance_df.iterrows():
    c1, c2 = row["pair"]
    pval = row["p_value"]
    heatmap_matrix.loc[c1, c2] = pval
    heatmap_matrix.loc[c2, c1] = pval

# Binary matrix: 1 = significant, 0 = not
binary_matrix = heatmap_matrix < 0.05

# Define a discrete colormap: skyblue = not significant, crimson = significant
cmap = mcolors.ListedColormap(["skyblue", "crimson"])

# Plot: color by binary, annotate with corrected p-values
plt.figure(figsize=(10, 8))
sns.heatmap(
    binary_matrix,
    annot=heatmap_matrix.round(3),
    fmt=".3f",
    cmap=cmap,
    cbar=False,
    linewidths=0.5,
    linecolor='gray',
    mask=np.triu(np.ones_like(binary_matrix, dtype=bool)),
    annot_kws={"size": 22}
)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.title("Significant Divergences Between Skin Color Pairs ", fontsize=16)
plt.xlabel("Skin Color", fontsize=14)
plt.ylabel("Skin Color", fontsize=14)
plt.tight_layout()
plt.savefig(f"pairwise_significance_fdr_{model_name}.png")
plt.show()










######################### bonferroni





from statsmodels.stats.multitest import multipletests

# Apply Bonferroni correction
bonferroni_corrected = multipletests(significance_df["p_value"], alpha=0.05, method="bonferroni")
significance_df["p_bonferroni"] = bonferroni_corrected[1]
significance_df["significant_bonferroni"] = bonferroni_corrected[0]

# Create heatmap matrix with Bonferroni-corrected p-values
heatmap_matrix = pd.DataFrame(index=all_colors, columns=all_colors, dtype=float)
binary_matrix = pd.DataFrame(index=all_colors, columns=all_colors, dtype=bool)

# Fill both matrices symmetrically
for _, row in significance_df.iterrows():
    c1, c2 = row["pair"]
    pval = row["p_bonferroni"]
    sig = row["significant_bonferroni"]
    heatmap_matrix.loc[c1, c2] = pval
    heatmap_matrix.loc[c2, c1] = pval
    binary_matrix.loc[c1, c2] = sig
    binary_matrix.loc[c2, c1] = sig

# Define color map
cmap = mcolors.ListedColormap(["skyblue", "crimson"])

# Plot
plt.figure(figsize=(10, 8))
sns.heatmap(
    binary_matrix,
    annot=heatmap_matrix,
    fmt=".2f",
    cmap=cmap,
    cbar=False,
    linewidths=0.5,
    linecolor='gray',
    mask=np.triu(np.ones_like(binary_matrix, dtype=bool)),
    annot_kws={"size": 22}
)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.title("Significant Divergences Between Skin Color Pairs (Bonferroni-adjusted)", fontsize=16)
plt.xlabel("Skin Color", fontsize=14)
plt.ylabel("Skin Color", fontsize=14)
plt.tight_layout()
plt.savefig(f"pairwise_significance_bonferroni_{model_name}.png")
plt.show()


