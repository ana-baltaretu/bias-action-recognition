import pandas as pd
import os

# Skin color mapping
skin_color_map = {
    "African": "african",
    "Asian": "asian",
    "Hispanic": "hispanic",
    "Indian": "indian",
    "Middle eastern": "middle_eastern",
    "South east asian": "south_east_asian",
    "White": "white"
}
valid_categories = list(skin_color_map.values())
sorted_categories = sorted(valid_categories, key=len, reverse=True)

# Paths
data_path = r"C:\Users\Ana\Desktop\bias-action-recognition\framework\models\i3d-torch\data\run_results\older_runs"
final_csv_path = r"C:\Users\Ana\Desktop\bias-action-recognition\results_visualization\model_results\older_runs"

# Models to process
model_names = ["tc_clip", "slowfast_r50", "mvit_base_16x4", "slow_r50", "x3d_xs"]

# Helper to extract skin color from video name
def extract_skin_color(video):
    video_lower = video.lower()
    for skin in sorted_categories:
        if skin in video_lower:
            return skin
    return None

# Process each model
for model_name in model_names:
    all_dfs = []

    for camera_distance in os.listdir(data_path):
        cam_path = os.path.join(data_path, camera_distance)
        if not os.path.isdir(cam_path):
            continue

        for background_name in os.listdir(cam_path):
            bg_path = os.path.join(cam_path, background_name)
            video_results_path = os.path.join(bg_path, model_name, "video_results.csv")
            if os.path.exists(video_results_path):
                df = pd.read_csv(video_results_path)

                # Add metadata columns
                df["camera_distance"] = camera_distance
                df["background"] = background_name

                # Extract skin color
                df["skin_color_category"] = df["video"].apply(extract_skin_color)

                # Fill in missing skin color based on video name prefix
                prefix_to_skin = {}
                for i, row in df.iterrows():
                    if pd.isna(row["skin_color_category"]):
                        prefix = "_".join(row["video"].split("_")[:2]) + "_"
                        if prefix not in prefix_to_skin:
                            used = df[df["video"].str.startswith(prefix)]["skin_color_category"].dropna().unique().tolist()
                            remaining = list(set(valid_categories) - set(used))
                            prefix_to_skin[prefix] = remaining[0] if len(remaining) == 1 else None
                        df.at[i, "skin_color_category"] = prefix_to_skin[prefix]

                all_dfs.append(df)

    # Save combined results for this model
    if all_dfs:
        combined_df = pd.concat(all_dfs, ignore_index=True)
        combined_df.to_csv(os.path.join(final_csv_path, f"video_results_extended_{model_name}.csv"), index=False)
