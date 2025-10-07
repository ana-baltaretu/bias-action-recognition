import pandas as pd

# Load the data
experiment_name = "top_20_kinetics_actions"
model_name = "tc_clip" # mvit_base_16x4, slowfast_r50, tc_clip
df = pd.read_csv(f"model_results/{experiment_name}/video_results_extended_{model_name}.csv")

# Extract base_video
df['base_video'] = df['video'].str.extract(r'(.*)_(?:initial|modified.*)')

# Group by base video
output_rows = []

for base_video, group in df.groupby('base_video'):
    # Get the initial prediction
    initial_row = group[group['video'].str.contains('initial')]
    if initial_row.empty:
        continue  # skip if no initial prediction
    initial_pred = initial_row['raw_prediction'].values[0]

    # Group modified videos by their prediction
    modified = group[~group['video'].str.contains('initial')]
    pred_groups = modified.groupby('raw_prediction')

    for pred, sub_group in pred_groups:
        if pred != initial_pred:
            output_rows.append({
                'base_video': base_video,
                'from_prediction': initial_pred,
                'to_prediction': pred,
                'skin_colors_same': ', '.join(group[group['raw_prediction'] == initial_pred]['skin_color_category'].dropna().unique()),
                'skin_colors_changed': ', '.join(sub_group['skin_color_category'].dropna().unique())
            })

# Output to CSV
output_df = pd.DataFrame(output_rows)
output_df.to_csv(f"model_results/{experiment_name}/prediction_divergence_summary_{model_name}.csv", index=False)
print(f"Saved to prediction_divergence_summary_{model_name}.csv")
