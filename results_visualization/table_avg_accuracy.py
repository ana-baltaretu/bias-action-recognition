import pandas as pd


def compute_joint_accuracy(file_paths):
    all_dfs = []
    for file_path in file_paths:
        df = pd.read_csv(file_path)
        initial_df = df[df['video'].str.contains('_initial')].copy()

        model_name = (
            file_path.split('/')[-1]
            .replace("video_results_extended_", "")
            .replace(".csv", "")
        )
        initial_df['model'] = model_name
        all_dfs.append(initial_df)

    all_data = pd.concat(all_dfs, ignore_index=True)

    # Group by action, background, camera, and model
    correct_counts = (
        all_data[all_data['result'] == 'correct']
        .groupby(['true_label', 'background', 'camera_distance', 'model'])
        .size()
    )
    total_counts = (
        all_data
        .groupby(['true_label', 'background', 'camera_distance', 'model'])
        .size()
    )
    acc = (correct_counts / total_counts).reset_index(name='accuracy').fillna(0)
    return acc, all_data


def compute_avg_accuracy_per_model_bg_cam_filtered(all_data: pd.DataFrame):
    # Step 1: Compute per-action accuracy
    correct_counts = (
        all_data[all_data['result'] == 'correct']
        .groupby(['background', 'camera_distance', 'model', 'true_label'])
        .size()
        .rename("correct")
    )
    total_counts = (
        all_data
        .groupby(['background', 'camera_distance', 'model', 'true_label'])
        .size()
        .rename("total")
    )

    acc_per_action = pd.concat([correct_counts, total_counts], axis=1).reset_index()
    acc_per_action['accuracy'] = acc_per_action['correct'] / acc_per_action['total']
    acc_per_action['accuracy'] = acc_per_action['accuracy'].fillna(0)

    # Step 2: Filter out actions where all models have 0 accuracy for a given bg+cam
    non_zero_action_mask = (
        acc_per_action
        .groupby(['background', 'camera_distance', 'true_label'])['accuracy']
        .sum()
        .reset_index(name='total_accuracy')
        .query('total_accuracy > 0')
    )

    acc_per_action = acc_per_action.merge(
        non_zero_action_mask[['background', 'camera_distance', 'true_label']],
        on=['background', 'camera_distance', 'true_label'],
        how='inner'
    )

    # Step 3: Average over remaining actions
    avg_acc = (
        acc_per_action
        .groupby(['background', 'camera_distance', 'model'])['accuracy']
        .mean()
        .reset_index()
        .sort_values(by=['background', 'camera_distance', 'model'])
    )

    return avg_acc


def generate_fixed_layout_latex_table(avg_acc_df: pd.DataFrame):
    df = avg_acc_df.copy()
    df['background'] = df['background'].str.replace('_', ' ')
    df['camera_distance'] = df['camera_distance'].str.replace('_', ' ')
    df['model'] = df['model'].str.replace('_', ' ')

    # Desired order
    backgrounds = ['autumn hockey', 'konzerthaus', 'stadium 01']
    camera_positions = ['camera near', 'camera far']
    ordered_columns = [(cam, bg) for cam in camera_positions for bg in backgrounds]

    # Pivot and ensure MultiIndex columns
    pivot = df.pivot_table(index='model', columns=['camera_distance', 'background'], values='accuracy', aggfunc='mean')
    pivot.columns = pd.MultiIndex.from_tuples(pivot.columns)
    pivot = pivot.reindex(columns=ordered_columns)

    # Compute average accuracy per row
    avg_col = pivot.mean(axis=1).rename(('average', ''))  # fake multiindex to avoid confusion
    pivot[('average', '')] = avg_col

    # Sort columns so average comes last
    ordered_columns += [('average', '')]
    pivot = pivot[ordered_columns]

    # Format values
    formatted = pivot.applymap(lambda x: f"{x:.2f}" if pd.notnull(x) else "-")
    formatted.index.name = 'model'
    formatted = formatted.reset_index()
    formatted['model'] = formatted['model'].str.replace('_', ' ')

    # Header rows
    header_top = (
        "\\begin{table*}[t]\n"
        "\\centering\n"
        "\\caption{Average accuracy per model by background and camera distance (excluding action categories which were never correctly predicted by any of the models).}\n"
        "\\label{tab:avg_acc_bg_cam}\n"
        "\\begin{tabular}{l|ccc|ccc|c}\n"
        "\\toprule\n"
        "\\textbf{Model} & \\multicolumn{3}{c|}{\\textbf{Camera Near}} & \\multicolumn{3}{c|}{\\textbf{Camera Far}} & \\textbf{Avg.} \\\\\n"
        "\\cmidrule(lr){2-4} \\cmidrule(lr){5-7}\n"
        "& Autumn Hockey & Konzerthaus & Stadium 01 & Autumn Hockey & Konzerthaus & Stadium 01 & \\\\\n"
        "\\midrule"
    )

    # Rows
    rows = "\n".join(
        f"{row[0]} & " + " & ".join(str(val) for val in row[1:]) + r" \\"
        for model, row in formatted.iterrows()
    )

    footer = "\n\\bottomrule\n\\end{tabular}\n\\end{table*}"

    return f"{header_top}\n{rows}{footer}"



experiment_name = "top_20_kinetics_actions"
model_names = ["mvit_base_16x4", "slow_r50", "slowfast_r50", "tc_clip", "x3d_xs"]
file_paths = [f"model_results/{experiment_name}/video_results_extended_{model_name}.csv" for model_name in model_names]
output_path = rf"output_plots\{experiment_name}\model_accuracy"

joint_acc, all_data = compute_joint_accuracy(file_paths)
avg_table = compute_avg_accuracy_per_model_bg_cam_filtered(all_data)
print(avg_table)

latex_str = generate_fixed_layout_latex_table(avg_table)
print(latex_str)
