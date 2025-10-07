import pandas as pd
from collections import defaultdict
from itertools import combinations
import matplotlib.pyplot as plt
import seaborn as sns
import os

# List of model names to compare
experiment_name = "top_20_kinetics_actions"
model_names = ["mvit_base_16x4", "slowfast_r50", "tc_clip"] # "x3d_xs", "slow_r50"
base_path = f"../model_results/{experiment_name}"
output_path = rf"..\output_plots\{experiment_name}\skin_color_change"
output_filename="model_divergence_rate_per_skincolor_pair.pdf"

colors = sns.color_palette("colorblind")
all_data = []

def extract_video_id(filename):
    return filename.replace("_initial", "_modified_").split("_modified_")[0]

for model_name in model_names:
    file_path = os.path.join(base_path, f"filtered_best_background_and_camera_{model_name}.csv")
    df = pd.read_csv(file_path)

    # Extract predictions
    predictions = [
        (extract_video_id(row["video"]), row["skin_color_category"], row["mapped_prediction"])
        for _, row in df.iterrows()
    ]

    # Group predictions by video
    video_preds = defaultdict(dict)
    for video_id, skin_color, pred in predictions:
        video_preds[video_id][skin_color] = pred

    # Count divergences between skin color pairs
    divergence_counts = defaultdict(lambda: {"div": 0, "no_div": 0})
    for preds in video_preds.values():
        for skin1, skin2 in combinations(preds.keys(), 2):
            pair = tuple(sorted([skin1, skin2]))
            if preds[skin1] != preds[skin2]:
                divergence_counts[pair]["div"] += 1
            else:
                divergence_counts[pair]["no_div"] += 1

    # Store results in a DataFrame
    for pair, counts in divergence_counts.items():
        total = counts["div"] + counts["no_div"]
        if total > 0:
            all_data.append({
                "pair": f"{pair[0]} &\n {pair[1]}",
                "divergence_rate": counts["div"] / total,
                "model": model_name
            })

# Combine into one DataFrame
combined_df = pd.DataFrame(all_data)

# Sort by mean divergence rate per pair for nice order in plot
pair_order = (
    combined_df.groupby("pair")["divergence_rate"]
    .mean()
    .sort_values(ascending=False)
    .index.tolist()
)

# Plot
plt.figure(figsize=(8, 14))
sns.barplot(
    data=combined_df,
    x="divergence_rate",
    y="pair",
    hue="model",
    order=pair_order,
    dodge=True,
    palette=[colors[0], colors[2], colors[3]]
)
plt.xlabel("Divergence Rate", fontsize=20)
plt.ylabel("Skin Color Pair", fontsize=20)
plt.title("Prediction Divergence Rate", fontsize=16)
plt.xticks(fontsize=12)
plt.yticks(fontsize=16)
plt.xlim(0, 1)
plt.legend(title="Model", fontsize=12, title_fontsize=13)
plt.tight_layout()
plt.savefig(os.path.join(output_path, output_filename), format='pdf')
plt.show()
