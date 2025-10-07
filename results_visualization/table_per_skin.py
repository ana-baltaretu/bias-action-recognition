import pandas as pd


def compute_joint_accuracy(file_paths):
    all_dfs = []
    for file_path in file_paths:
        df = pd.read_csv(file_path)
        # remove .str.contains('_initial') — we want all skin colors now
        model_name = (
            file_path.split('/')[-1]
            .replace("video_results_extended_", "")
            .replace(".csv", "")
        )
        df['model'] = model_name
        all_dfs.append(df)

    all_data = pd.concat(all_dfs, ignore_index=True)

    # Same as before (not strictly needed here anymore)
    correct_counts = (
        all_data[all_data['result'] == 'correct']
        .groupby(['true_label', 'background', 'camera_distance', 'model', 'skin_color_category'])
        .size()
    )
    total_counts = (
        all_data
        .groupby(['true_label', 'background', 'camera_distance', 'model', 'skin_color_category'])
        .size()
    )
    acc = (correct_counts / total_counts).reset_index(name='accuracy').fillna(0)
    return acc, all_data


def compute_best_bg_cam_per_action(all_data: pd.DataFrame):
    # Step 1: per-skin-color accuracy
    correct = (
        all_data[all_data['result'] == 'correct']
        .groupby(['true_label', 'background', 'camera_distance', 'model', 'skin_color_category'])
        .size()
        .rename("correct")
    )
    total = (
        all_data
        .groupby(['true_label', 'background', 'camera_distance', 'model', 'skin_color_category'])
        .size()
        .rename("total")
    )

    acc = pd.concat([correct, total], axis=1).reset_index()
    acc['correct'] = acc['correct'].fillna(0)
    acc['accuracy'] = acc['correct'] / acc['total']

    # Step 2: keep only actions where at least one correct prediction exists
    any_correct = (
        acc.groupby(['true_label', 'skin_color_category'])['correct']
        .sum()
        .reset_index()
        .query("correct > 0")
        .drop(columns='correct')
    )
    acc = acc.merge(any_correct, on=['true_label', 'skin_color_category'])

    # Step 3: average accuracy across models to find best bg+cam per action per skin
    avg_acc = (
        acc.groupby(['true_label', 'background', 'camera_distance', 'skin_color_category'])['accuracy']
        .mean()
        .reset_index()
    )

    best_bg_cam = (
        avg_acc.sort_values('accuracy', ascending=False)
        .drop_duplicates(subset=['true_label', 'skin_color_category'])
        .drop(columns='accuracy')
    )

    filtered_acc = acc.merge(best_bg_cam, on=['true_label', 'background', 'camera_distance', 'skin_color_category'])
    return filtered_acc, best_bg_cam


def compute_avg_accuracy_best_bg_cam(filtered_acc: pd.DataFrame):
    avg_acc = (
        filtered_acc.groupby(['model', 'skin_color_category'])['accuracy']
        .mean()
        .reset_index()
        .sort_values(by=['skin_color_category', 'accuracy'], ascending=[True, False])
    )
    return avg_acc


def generate_pivoted_latex_table_by_skin_color(avg_acc_df: pd.DataFrame, caption: str, label: str):
    df = avg_acc_df.copy()
    df['model'] = df['model'].str.replace('_', ' ')

    # Pivot so each skin color category becomes a column
    pivot = df.pivot(index='model', columns='skin_color_category', values='accuracy')

    # Clean column names: replace underscores with spaces
    pivot.columns = [col.replace('_', ' ') for col in pivot.columns]

    # Compute mean and std across skin tones
    skin_tone_cols = sorted(pivot.columns)
    pivot['Mean'] = pivot[skin_tone_cols].mean(axis=1)
    pivot['Std.'] = pivot[skin_tone_cols].std(axis=1)

    # Reorder: skin tones + Mean + Std.
    ordered_cols = skin_tone_cols + ['Mean', 'Std.']
    pivot = pivot[ordered_cols].reset_index()

    # Optionally: add citation references
    citation_map = {
        "mvit base 16x4": "\\cite{fan2021multiscale}",
        "slow r50": "\\cite{feichtenhofer2019slowfast}",
        "slowfast r50": "\\cite{feichtenhofer2019slowfast}",
        "tc clip": "\\cite{kim2024leveraging}",
        "x3d xs": "\\cite{feichtenhofer2020x3dxs}"
    }

    # LaTeX header
    latex = (
        "\\begin{strip}\n"
        "\\centering\n"
        f"\\captionof{{table}}{{{caption}}}\n"
        f"\\label{{{label}}}\n"
        f"\\begin{{tabular}}{{l|{'c' * (len(ordered_cols)-2)}|cc}}\n"
        "\\toprule\n"
        "\\textbf{Model} & " + " & ".join(f"\\textbf{{{col}}}" for col in ordered_cols) + " \\\\\n"
        "\\midrule\n"
    )

    # Format each row with bold max values per row (excluding Mean and Std.)
    for _, row in pivot.iterrows():
        model_name = row['model']
        citation = citation_map.get(model_name.lower(), "")
        max_val = row[skin_tone_cols].max()
        row_values = []

        for col in skin_tone_cols:
            val = row[col]
            if pd.isna(val):
                row_values.append("-")
            elif abs(val - max_val) < 1e-6:
                row_values.append(f"\\textbf{{{val:.3f}}}")
            else:
                row_values.append(f"{val:.3f}")

        # Append Mean and Std.
        row_values.append(f"{row['Mean']:.3f}")
        row_values.append(f"{row['Std.']:.3f}")

        latex += f"{model_name} {citation} & " + " & ".join(row_values) + " \\\\\n"

    latex += "\\bottomrule\n\\end{tabular}\n\\end{strip}"
    return latex


def print_best_bg_cam_per_action(best_bg_cam: pd.DataFrame):
    print("\nBest background and camera distance per action:\n")
    for _, row in best_bg_cam.sort_values('true_label').iterrows():
        action = row['true_label']
        bg = row['background'].replace('_', ' ')
        cam = row['camera_distance'].replace('_', ' ')
        print(f"{action}: {bg}, {cam}")



experiment_name = "top_20_kinetics_actions"
model_names = ["mvit_base_16x4", "slow_r50", "slowfast_r50", "tc_clip", "x3d_xs"]
file_paths = [f"model_results/{experiment_name}/video_results_extended_{model_name}.csv" for model_name in model_names]
output_path = rf"output_plots\{experiment_name}\model_accuracy"

joint_acc, all_data = compute_joint_accuracy(file_paths)
filtered_acc, best_bg_cam = compute_best_bg_cam_per_action(all_data)
avg_acc_df = compute_avg_accuracy_best_bg_cam(filtered_acc)
print(avg_acc_df)

# Print selected background and camera per action
# print_best_bg_cam_per_action(best_bg_cam)

latex_str = generate_pivoted_latex_table_by_skin_color(
    avg_acc_df,
    caption="Average accuracy per model across skin color categories using best background-camera combination per action.",
    label="tab:avg_acc_by_skin_color"
)
print(latex_str)


