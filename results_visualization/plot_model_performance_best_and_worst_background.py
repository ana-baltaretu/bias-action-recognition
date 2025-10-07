import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re
from typing import List, Tuple

def compute_accuracy_by_condition(file_paths, condition_column):
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

    correct_counts = (
        all_data[all_data['result'] == 'correct']
        .groupby(['true_label', condition_column, 'model'])
        .size()
    )
    total_counts = (
        all_data
        .groupby(['true_label', condition_column, 'model'])
        .size()
    )
    acc = (correct_counts / total_counts).reset_index(name='accuracy').fillna(0)
    return acc, all_data

def get_best_or_worst_per_action(acc, condition_column, best=True):
    avg_acc = acc.groupby(['true_label', condition_column])['accuracy'].mean().reset_index()
    sort_order = [True, False] if best else [True, True]
    condition_per_action = (
        avg_acc.sort_values(['true_label', 'accuracy'], ascending=sort_order)
        .drop_duplicates('true_label')
        .set_index('true_label')[condition_column]
    )
    return condition_per_action

def prepare_filtered_accuracy(acc, condition_per_action, condition_column, sorted_actions=None):
    acc['selected_condition'] = acc['true_label'].map(condition_per_action)
    filtered_acc = acc[acc[condition_column] == acc['selected_condition']].copy()
    filtered_acc = filtered_acc.rename(columns={'true_label': 'action'})

    # Only discard actions that are 0 across all backgrounds and all models
    pivot_full = acc.pivot_table(index='true_label', columns=condition_column, values='accuracy', aggfunc='max', fill_value=0)
    non_zero_actions = pivot_full[pivot_full.max(axis=1) > 0].index.tolist()
    filtered_acc = filtered_acc[filtered_acc['action'].isin(non_zero_actions)]

    if sorted_actions is None:
        sorted_actions = (
            filtered_acc.groupby('action')['accuracy']
            .mean()
            .sort_values(ascending=False)
            .index.tolist()
        )

    filtered_acc['action'] = pd.Categorical(filtered_acc['action'], categories=sorted_actions, ordered=True)
    return filtered_acc, sorted_actions

def plot_accuracy_per_action(filtered_acc: pd.DataFrame, title: str, save_path: str = None, filename_prefix: str = "plot"):
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=filtered_acc, x='action', y='accuracy', hue='model', marker='o')
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, 1)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.title(title, fontsize=16)
    plt.xlabel("Action Category", fontsize=14)
    plt.ylabel("Accuracy", fontsize=14)
    plt.tight_layout()
    if save_path:
        filename = f"{filename_prefix}_lineplot.pdf"
        plt.savefig(os.path.join(save_path, filename), format='pdf')
    plt.show()

    model_avg = filtered_acc.groupby('model')['accuracy'].mean().reset_index()
    plt.figure(figsize=(10, 5))
    bars = sns.barplot(data=model_avg, x='model', y='accuracy', palette='Set2')
    plt.ylim(0, 1)
    plt.title("Overall Accuracy per Model", fontsize=16)
    plt.xlabel("")
    plt.ylabel("Accuracy", fontsize=14)
    plt.grid(True, axis='y', linestyle='--', alpha=0.5)
    for bar in bars.patches:
        height = bar.get_height()
        bars.annotate(f'{height:.2f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                      ha='center', va='bottom', fontsize=12)
    plt.tight_layout()
    if save_path:
        filename = f"{filename_prefix}_barplot.pdf"
        plt.savefig(os.path.join(save_path, filename), format='pdf')
    plt.show()
    return model_avg


experiment_name = "top_20_kinetics_actions"
model_names = ["mvit_base_16x4", "slow_r50", "slowfast_r50", "tc_clip", "x3d_xs"]
file_paths = [f"model_results/{experiment_name}/video_results_extended_{model_name}.csv" for model_name in model_names]
output_path = rf"output_plots\{experiment_name}\model_accuracy"

# Step 1: Compute accuracy by background
acc_data, _ = compute_accuracy_by_condition(file_paths, 'background')

# Step 2: Best background per action
best_bg = get_best_or_worst_per_action(acc_data, 'background', best=True)
print(best_bg)
best_filtered, sorted_actions = prepare_filtered_accuracy(acc_data, best_bg, 'background')

# Step 3: Worst background per action (uses same order)
worst_bg = get_best_or_worst_per_action(acc_data, 'background', best=False)
worst_filtered, _ = prepare_filtered_accuracy(acc_data, worst_bg, 'background', sorted_actions)

# Step 4: Plot
plot_accuracy_per_action(best_filtered, "Accuracy per Action (Best Background)", output_path, "best_background")
plot_accuracy_per_action(worst_filtered, "Accuracy per Action (Worst Background)", output_path, "worst_background")
