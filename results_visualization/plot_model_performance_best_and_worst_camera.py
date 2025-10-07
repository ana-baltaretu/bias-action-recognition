import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
import re


def plot_action_line_and_model_bar_accuracy_best_camera(file_paths, save_path=None):
    # Per individual video
    model_dfs = []

    for file_path in file_paths:
        df = pd.read_csv(file_path)
        initial_df = df[df['video'].str.contains('_initial')]

        # Extract model name
        model_name = os.path.basename(file_path)
        model_name = re.sub(r'^video_results_extended_(.+?)\.csv$', r'\1', model_name)

        # For each unique base video (excluding camera), keep only the best result
        # Assumes video names look like: 'xyz_camera_far' or 'abc_camera_near'
        initial_df['video_base'] = initial_df['video'].str.replace(r'_camera_.+$', '', regex=True)

        # Keep the best result for each video_base
        initial_df['correct_flag'] = (initial_df['result'] == 'correct').astype(int)
        idx = (
            initial_df.sort_values('correct_flag', ascending=False)
            .groupby('video_base')
            .head(1)
            .index
        )
        best_df = initial_df.loc[idx]

        # Accuracy per action
        correct_counts = best_df[best_df['result'] == 'correct'].groupby('true_label').size()
        total_counts = best_df.groupby('true_label').size()
        accuracy = (correct_counts / total_counts).fillna(0)

        df_model = accuracy.reset_index()
        df_model.columns = ['action', 'accuracy']
        df_model['model'] = model_name

        model_dfs.append(df_model)

    # Combine all model data
    all_data = pd.concat(model_dfs, ignore_index=True)

    # Remove actions where accuracy is 0 across all models
    pivoted = all_data.pivot_table(index='action', columns='model', values='accuracy', fill_value=0)
    non_zero_actions = pivoted[pivoted.sum(axis=1) > 0].index.tolist()
    all_data = all_data[all_data['action'].isin(non_zero_actions)]

    # Sort actions by mean accuracy
    sorted_actions = (
        all_data.groupby('action')['accuracy']
        .mean()
        .sort_values(ascending=False)
        .index.tolist()
    )
    all_data['action'] = pd.Categorical(all_data['action'], categories=sorted_actions, ordered=True)

    # --- Line Plot ---
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=all_data, x='action', y='accuracy', hue='model', marker='o')
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, 1)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.title("Model Accuracy per Action (Best Camera Distance per Video)", fontsize=16)
    plt.xlabel("Action Category", fontsize=14)
    plt.ylabel("Accuracy", fontsize=14)
    plt.tight_layout()

    if save_path:
        filename = "model_accuracy_per_action_lineplot_best_camera.pdf"
        plt.savefig(os.path.join(save_path, filename), format='pdf')
        print(f"Saved: {filename}")
    plt.show()

    # --- Bar Plot: Mean Accuracy per Model ---
    model_avg = all_data.groupby('model')['accuracy'].mean().reset_index()
    plt.figure(figsize=(10, 5))
    bars = sns.barplot(data=model_avg, x='model', y='accuracy', palette='Set2')
    plt.ylim(0, 1)
    plt.title("Overall Accuracy per Model (Best Camera Distance)", fontsize=16)
    plt.xlabel("")
    plt.ylabel("Mean Accuracy", fontsize=14)
    plt.grid(True, axis='y', linestyle='--', alpha=0.5)

    # Value labels
    for bar in bars.patches:
        height = bar.get_height()
        bars.annotate(f'{height:.2f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                      ha='center', va='bottom', fontsize=12)

    plt.tight_layout()

    if save_path:
        filename = "overall_accuracy_per_model_barplot_best_camera.pdf"
        plt.savefig(os.path.join(save_path, filename), format='pdf')
        print(f"Saved: {filename}")
    plt.show()


def plot_action_line_and_model_bar_accuracy_best_camera_per_action(file_paths, save_path=None):
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    import os
    import re

    all_dfs = []

    for file_path in file_paths:
        df = pd.read_csv(file_path)
        initial_df = df[df['video'].str.contains('_initial')]

        # Extract model name
        model_name = os.path.basename(file_path)
        model_name = re.sub(r'^video_results_extended_(.+?)\.csv$', r'\1', model_name)
        initial_df['model'] = model_name
        all_dfs.append(initial_df)

    all_data = pd.concat(all_dfs, ignore_index=True)

    # --- STEP 1: Compute average accuracy per (action, camera_distance) across all models ---
    correct_counts = (
        all_data[all_data['result'] == 'correct']
        .groupby(['true_label', 'camera_distance', 'model'])
        .size()
    )
    total_counts = (
        all_data
        .groupby(['true_label', 'camera_distance', 'model'])
        .size()
    )
    acc = (correct_counts / total_counts).reset_index(name='accuracy').fillna(0)

    # Get best camera per action (across all models)
    avg_acc = acc.groupby(['true_label', 'camera_distance'])['accuracy'].mean().reset_index()
    best_camera_per_action = (
        avg_acc.sort_values(['true_label', 'accuracy'], ascending=[True, False])
        .drop_duplicates('true_label')
        .set_index('true_label')['camera_distance']
    )

    print(best_camera_per_action)

    # --- STEP 2: Filter data to only include best camera per action ---
    acc['best_camera'] = acc['true_label'].map(best_camera_per_action)
    filtered_acc = acc[acc['camera_distance'] == acc['best_camera']].copy()

    # Rename for plotting
    filtered_acc = filtered_acc.rename(columns={'true_label': 'action'})

    # --- STEP 3: Filter out actions with 0 accuracy across all models ---
    pivoted = filtered_acc.pivot_table(index='action', columns='model', values='accuracy', fill_value=0)
    non_zero_actions = pivoted[pivoted.sum(axis=1) > 0].index.tolist()
    filtered_acc = filtered_acc[filtered_acc['action'].isin(non_zero_actions)]

    # Sort actions by avg accuracy
    sorted_actions = (
        filtered_acc.groupby('action')['accuracy']
        .mean()
        .sort_values(ascending=False)
        .index.tolist()
    )
    filtered_acc['action'] = pd.Categorical(filtered_acc['action'], categories=sorted_actions, ordered=True)

    # --- Line Plot ---
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=filtered_acc, x='action', y='accuracy', hue='model', marker='o')
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, 1)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.title("Model Accuracy per Action (Best Camera Distance per Action)", fontsize=16)
    plt.xlabel("Action Category", fontsize=14)
    plt.ylabel("Accuracy", fontsize=14)
    plt.tight_layout()

    if save_path:
        filename = "model_accuracy_per_action_lineplot_best_camera_per_action.pdf"
        plt.savefig(os.path.join(save_path, filename), format='pdf')
        print(f"Saved: {filename}")
    plt.show()

    # --- Bar Plot: Mean Accuracy per Model ---
    model_avg = filtered_acc.groupby('model')['accuracy'].mean().reset_index()
    plt.figure(figsize=(10, 5))
    bars = sns.barplot(data=model_avg, x='model', y='accuracy', palette='Set2')
    plt.ylim(0, 1)
    plt.title("Overall Accuracy per Model (Best Camera Distance per Action)", fontsize=16)
    plt.xlabel("")
    plt.ylabel("Accuracy", fontsize=14)
    plt.grid(True, axis='y', linestyle='--', alpha=0.5)

    for bar in bars.patches:
        height = bar.get_height()
        bars.annotate(f'{height:.2f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                      ha='center', va='bottom', fontsize=12)

    plt.tight_layout()

    if save_path:
        filename = "overall_accuracy_per_model_barplot_best_camera_per_action.pdf"
        plt.savefig(os.path.join(save_path, filename), format='pdf')
        print(f"Saved: {filename}")
    plt.show()

    return filtered_acc, sorted_actions


def plot_action_line_and_model_bar_accuracy_worst_camera_per_action(file_paths, sorted_actions, save_path=None):

    all_dfs = []

    for file_path in file_paths:
        df = pd.read_csv(file_path)
        initial_df = df[df['video'].str.contains('_initial')]

        # Extract model name
        model_name = os.path.basename(file_path)
        model_name = re.sub(r'^video_results_extended_(.+?)\.csv$', r'\1', model_name)
        initial_df['model'] = model_name
        all_dfs.append(initial_df)

    all_data = pd.concat(all_dfs, ignore_index=True)

    # --- STEP 1: Compute accuracy per (action, camera_distance, model) ---
    correct_counts = (
        all_data[all_data['result'] == 'correct']
        .groupby(['true_label', 'camera_distance', 'model'])
        .size()
    )
    total_counts = (
        all_data
        .groupby(['true_label', 'camera_distance', 'model'])
        .size()
    )
    acc = (correct_counts / total_counts).reset_index(name='accuracy').fillna(0)

    # --- STEP 2: Exclude actions that are 0 across all models and all cameras ---
    global_action_avg = (
        acc.groupby('true_label')['accuracy']
        .max()
        .reset_index()
    )
    valid_actions = global_action_avg[global_action_avg['accuracy'] > 0]['true_label'].tolist()
    acc = acc[acc['true_label'].isin(valid_actions)]

    # --- STEP 3: Get worst camera per action (across all models) ---
    avg_acc = acc.groupby(['true_label', 'camera_distance'])['accuracy'].mean().reset_index()
    worst_camera_per_action = (
        avg_acc.sort_values(['true_label', 'accuracy'], ascending=[True, True])
        .drop_duplicates('true_label')
        .set_index('true_label')['camera_distance']
    )

    # --- STEP 4: Filter to only rows matching the worst camera per action ---
    acc['worst_camera'] = acc['true_label'].map(worst_camera_per_action)
    filtered_acc = acc[acc['camera_distance'] == acc['worst_camera']].copy()
    filtered_acc = filtered_acc.rename(columns={'true_label': 'action'})

    # --- STEP 5: Apply external action order ---
    filtered_acc = filtered_acc.rename(columns={'true_label': 'action'})
    filtered_acc['action'] = pd.Categorical(filtered_acc['action'], categories=sorted_actions, ordered=True)

    # --- LINE PLOT ---
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=filtered_acc, x='action', y='accuracy', hue='model', marker='o')
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, 1)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.title("Model Accuracy per Action (Worst Camera Distance per Action)", fontsize=16)
    plt.xlabel("Action Category", fontsize=14)
    plt.ylabel("Accuracy", fontsize=14)
    plt.tight_layout()

    if save_path:
        filename = "model_accuracy_per_action_lineplot_worst_camera_per_action.pdf"
        plt.savefig(os.path.join(save_path, filename), format='pdf')
        print(f"Saved: {filename}")
    plt.show()

    # --- BAR PLOT ---
    model_avg = filtered_acc.groupby('model')['accuracy'].mean().reset_index()
    plt.figure(figsize=(10, 5))
    bars = sns.barplot(data=model_avg, x='model', y='accuracy', palette='Set2')
    plt.ylim(0, 1)
    plt.title("Overall Accuracy per Model (Worst Camera Distance per Action)", fontsize=16)
    plt.xlabel("")
    plt.ylabel("Accuracy", fontsize=14)
    plt.grid(True, axis='y', linestyle='--', alpha=0.5)

    for bar in bars.patches:
        height = bar.get_height()
        bars.annotate(f'{height:.2f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                      ha='center', va='bottom', fontsize=12)

    plt.tight_layout()

    if save_path:
        filename = "overall_accuracy_per_model_barplot_worst_camera_per_action.pdf"
        plt.savefig(os.path.join(save_path, filename), format='pdf')
        print(f"Saved: {filename}")
    plt.show()



experiment_name = "top_20_kinetics_actions"
model_names = ["mvit_base_16x4", "slow_r50", "slowfast_r50", "tc_clip", "x3d_xs"]
file_paths = [f"model_results/{experiment_name}/video_results_extended_{model_name}.csv" for model_name in model_names]
output_path = rf"output_plots\{experiment_name}\model_accuracy"

# plot_action_line_and_model_bar_accuracy_best_camera(file_paths, output_path)
# plot_action_line_and_model_bar_accuracy_best_camera_per_action(file_paths, output_path)
best_data, sorted_actions = plot_action_line_and_model_bar_accuracy_best_camera_per_action(file_paths)
plot_action_line_and_model_bar_accuracy_worst_camera_per_action(file_paths, sorted_actions, output_path)