import os
import pandas as pd
from scipy.stats import fisher_exact
from itertools import combinations
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.colors as mcolors
import re

# Configuration
experiment_name = "older_runs"
model_names = ["mvit_base_16x4", "slow_r50", "slowfast_r50", "tc_clip", "x3d_xs"]
file_paths = [f"../model_results/{experiment_name}/video_results_extended_{model_name}.csv" for model_name in model_names]
output_path = rf"output_plots\{experiment_name}\model_accuracy"
os.makedirs(output_path, exist_ok=True)

# Skin colors to consider
skin_colors = [
    "white", "african", "asian", "hispanic", "indian",
    "middle_eastern", "south_east_asian"
]


# Run analysis for each model
for model_name, file_path in zip(model_names, file_paths):
    print(f"\nProcessing {model_name}...")

    try:
        df = pd.read_csv(file_path)
        # Filter to only base_ids that were predicted correctly on _initial by THIS model
        df["base_id"] = df["video"].apply(lambda x: re.sub(r"_(initial|modified_.*)\.mp4", "", x))
        initial_df = df[df["video"].str.contains("_initial.mp4")]
        correct_ids = initial_df[initial_df["result"] == "correct"]["base_id"].unique()
        df = df[df["base_id"].isin(correct_ids)]
        print(model_name, len(df))
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        continue

    # Extract base identity: remove _initial or _modified_* and .mp4
    df["base_id"] = df["video"].apply(lambda x: re.sub(r"_(initial|modified_.*)\.mp4", "", x))

    # Get the reference prediction for each base_id (initial version, i.e., white)
    reference_preds = df[df["video"].str.contains("_initial.mp4")][["base_id", "mapped_prediction"]]
    reference_preds = reference_preds.rename(columns={"mapped_prediction": "reference_prediction"})

    # Merge back to get reference prediction per row
    df = df.merge(reference_preds, on="base_id", how="left")

    # Determine if the prediction changed compared to the white (initial) version
    df["prediction_changed"] = df["mapped_prediction"] != df["reference_prediction"]

    # Create a new binary column per skin color: did this skin color appear *and* was prediction changed
    for color in skin_colors:
        df[color] = ((df["skin_color_category"] == color) & (df["prediction_changed"])).astype(int)

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

    # Plot barplot
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
    plt.savefig(os.path.join(output_path, f"barplot_significance_{model_name}.png"))
    plt.show()

    # Create a square matrix of adjusted p-values
    heatmap_matrix = pd.DataFrame(
        np.ones((len(skin_colors), len(skin_colors))),
        index=skin_colors,
        columns=skin_colors
    )

    for _, row in results_df.iterrows():
        c1, c2 = row["skin_color_1"], row["skin_color_2"]
        p = row["adjusted_p_value"]
        heatmap_matrix.loc[c1, c2] = p
        heatmap_matrix.loc[c2, c1] = p  # symmetric

    binary_matrix = heatmap_matrix < 0.05
    cmap = mcolors.ListedColormap(["skyblue", "crimson"])

    plt.figure(figsize=(8, 6))
    sns.heatmap(
        binary_matrix,
        annot=heatmap_matrix.round(2),
        fmt="",
        cmap=cmap,
        cbar=False,
        linewidths=0.5,
        linecolor='gray',
        mask=np.tril(np.ones_like(binary_matrix, dtype=bool))
    )
    plt.title("Significant Differences in Prediction Divergence (Bonferroni-adjusted)")
    plt.tight_layout()
    plt.savefig(os.path.join(output_path, f"heatmap_significance_{model_name}.png"))
    plt.show()

    # === Accuracy per skin color ===
    accuracy_df = (
        df.groupby("skin_color_category")["result"]
        .apply(lambda x: (x == "correct").mean())
        .reindex(skin_colors)  # ensure consistent order
        .reset_index()
        .rename(columns={"result": "accuracy"})
    )

    plt.figure(figsize=(8, 5))
    sns.barplot(data=accuracy_df, x="skin_color_category", y="accuracy", palette="viridis")
    plt.ylim(0, 1)
    plt.ylabel("Accuracy")
    plt.xlabel("Skin Color")
    plt.title(f"Prediction Accuracy per Skin Color ({model_name})")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_path, f"accuracy_per_skin_color_{model_name}.png"))
    plt.show()

