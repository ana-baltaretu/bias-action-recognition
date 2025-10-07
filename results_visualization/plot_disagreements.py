import pandas as pd
import matplotlib.pyplot as plt
from itertools import combinations
from collections import Counter
import os

# Path to your filtered CSV file
file_path = "model_results/top_20_kinetics_actions/filtered_best_background_and_camera_mvit_base_16x4.csv"

# Load the CSV
df = pd.read_csv(file_path)

# Prepare mapping: extract base video name (e.g., "cartwheel_0" from "cartwheel_0_modified_asian.mp4")
df['base_video'] = df['video'].str.extract(r'^(.*?)(_modified|_initial)')[0]

# Extract the relevant columns
video_data = df[['video', 'mapped_prediction', 'skin_color_category', 'base_video']].copy()

# Initialize counter for disagreements and list for disagreement video names
skin_color_diff_count = Counter()
disagreeing_base_videos = set()  # use set to avoid duplicates

# For each group of videos from the same base video (e.g., cartwheel_0), compare predictions
for base_video, group in video_data.groupby('base_video'):
    preds = group[['video', 'mapped_prediction', 'skin_color_category']].to_dict(orient='records')

    # Compare all pairs of predictions in this group
    for a, b in combinations(preds, 2):
        if a['mapped_prediction'] != b['mapped_prediction']:
            skin_color_diff_count[a['skin_color_category']] += 1
            skin_color_diff_count[b['skin_color_category']] += 1
            disagreeing_base_videos.add(base_video)

# Convert results to DataFrame for plotting
diff_df = pd.DataFrame(list(skin_color_diff_count.items()), columns=['skin_color_category', 'total_disagreements'])
diff_df = diff_df.sort_values(by='total_disagreements', ascending=False)

# Plot
plt.figure(figsize=(8, 5))
plt.bar(diff_df['skin_color_category'], diff_df['total_disagreements'])
plt.title('Total Disagreements per Skin Color Across All Video Groups')
plt.xlabel('Skin Color')
plt.ylabel('Number of Disagreements')
plt.tight_layout()
plt.show()

# Print or save the list of base video names with disagreements
print("Videos with disagreements:", sorted(disagreeing_base_videos))
