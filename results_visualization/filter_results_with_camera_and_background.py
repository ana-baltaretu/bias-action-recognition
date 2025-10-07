import pandas as pd
import os

experiment_name = "top_20_kinetics_actions"
model_names = ["mvit_base_16x4", "slow_r50", "slowfast_r50", "tc_clip", "x3d_xs"]
file_paths = [f"model_results/{experiment_name}/video_results_extended_{model_name}.csv" for model_name in model_names]
output_path = f"model_results/{experiment_name}/"

# Load best background and camera settings
best_settings_path = os.path.join(output_path, "best_background_and_camera_per_action.csv")
best_settings = pd.read_csv(best_settings_path)

# Check required columns
expected_columns = {"action", "best_background", "best_camera"}
if not expected_columns.issubset(best_settings.columns):
    raise ValueError(f"Expected columns: {expected_columns}, but got: {set(best_settings.columns)}")

# Rename for merging
best_settings = best_settings.rename(columns={"action": "true_label"})

# Filter and save one file per model
for model_name, path in zip(model_names, file_paths):
    df = pd.read_csv(path)
    merged_df = df.merge(best_settings, on="true_label", how="inner")
    filtered_df = merged_df[
        (merged_df["background"] == merged_df["best_background"]) &
        (merged_df["camera_distance"] == merged_df["best_camera"])
        ]

    output_file = os.path.join(output_path, f"filtered_best_background_and_camera_{model_name}.csv")
    filtered_df.to_csv(output_file, index=False)
    print(f"Saved filtered file for {model_name} to: {output_file}")
