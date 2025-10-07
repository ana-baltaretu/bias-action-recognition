import pandas as pd
import os

def load_all_initial_videos(file_paths):
    all_dfs = []
    for file_path in file_paths:
        df = pd.read_csv(file_path)
        df = df[df['video'].str.contains('_initial')].copy()
        all_dfs.append(df)
    return pd.concat(all_dfs, ignore_index=True)

def get_best_per_condition(df, condition_column):
    correct = df[df['result'] == 'correct']
    correct_counts = correct.groupby(['true_label', condition_column]).size()
    total_counts = df.groupby(['true_label', condition_column]).size()
    accuracy = (correct_counts / total_counts).reset_index(name='accuracy')

    # Filter out action-condition pairs where all accuracies are 0
    accuracy = accuracy[accuracy['accuracy'] > 0]

    # Find the best condition per action
    best = (
        accuracy.sort_values(['true_label', 'accuracy'], ascending=[True, False])
        .drop_duplicates('true_label')
        .set_index('true_label')[condition_column]
    )
    return best

if __name__ == "__main__":
    experiment_name = "top_20_kinetics_actions"
    model_names = ["mvit_base_16x4", "slow_r50", "slowfast_r50", "tc_clip", "x3d_xs"]
    file_paths = [f"model_results/{experiment_name}/video_results_extended_{model}.csv" for model in model_names]
    output_path = f"model_results/{experiment_name}/"
    os.makedirs(output_path, exist_ok=True)

    # Step 1: Load all data
    full_df = load_all_initial_videos(file_paths)

    # Step 2: Remove action labels where all settings fail (accuracy == 0 for all backgrounds/cameras)
    correct = full_df[full_df['result'] == 'correct']
    total_counts = full_df.groupby(['true_label']).size()
    correct_counts = correct.groupby(['true_label']).size()
    accuracy_by_action = (correct_counts / total_counts).fillna(0)

    # Keep only actions with any non-zero accuracy
    valid_actions = accuracy_by_action[accuracy_by_action > 0].index.tolist()
    filtered_df = full_df[full_df['true_label'].isin(valid_actions)]

    # Step 3: Get best background and camera
    best_bg = get_best_per_condition(filtered_df, 'background')
    best_cam = get_best_per_condition(filtered_df, 'camera_distance')

    # Step 4: Merge and save
    summary = pd.DataFrame({
        'action': best_bg.index,
        'best_background': best_bg.values,
        'best_camera': best_cam.reindex(best_bg.index).values
    })

    output_file = os.path.join(output_path, "best_background_and_camera_per_action.csv")
    summary.to_csv(output_file, index=False)
    print(f"Saved summary to: {output_file}")
