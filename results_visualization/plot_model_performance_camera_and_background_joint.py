import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re
from matplotlib.patches import Patch
import colorsys
import numpy as np

MODEL_ORDER = ["mvit_base_16x4", "slow_r50", "slowfast_r50", "tc_clip", "x3d_xs"]
PALETTE = dict(zip(MODEL_ORDER, sns.color_palette("colorblind", len(MODEL_ORDER))))






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


def get_joint_best_or_worst_per_action(acc, best=True):
    avg_acc = acc.groupby(['true_label', 'background', 'camera_distance'])['accuracy'].mean().reset_index()
    sort_order = [True, False] if best else [True, True]
    joint_condition = (
        avg_acc.sort_values(['true_label', 'accuracy'], ascending=sort_order)
        .drop_duplicates('true_label')
        .set_index('true_label')[['background', 'camera_distance']]
    )
    return joint_condition


def prepare_filtered_joint_accuracy(acc, joint_condition, sorted_actions=None, base_actions=None):
    acc = acc.copy()
    acc['bg_cam'] = list(zip(acc['background'], acc['camera_distance']))
    joint_condition = joint_condition.copy()
    joint_condition['bg_cam'] = list(zip(joint_condition['background'], joint_condition['camera_distance']))
    acc = acc.merge(joint_condition[['bg_cam']], left_on=['true_label', 'bg_cam'], right_on=['true_label', 'bg_cam'])

    acc = acc.rename(columns={'true_label': 'action'})

    # Only discard actions if they are zero across all models for the *base condition*
    if base_actions is not None:
        acc = acc[acc['action'].isin(base_actions)]
    else:
        # Derive non-zero actions from current accuracy values
        pivot_full = acc.pivot_table(index='action', values='accuracy', aggfunc='max', fill_value=0)
        non_zero_actions = pivot_full[pivot_full['accuracy'] > 0].index.tolist()
        acc = acc[acc['action'].isin(non_zero_actions)]

    # Determine or apply the sorting order
    if sorted_actions is None:
        sorted_actions = (
            acc.groupby('action')['accuracy']
            .mean()
            .sort_values(ascending=False)
            .index.tolist()
        )

    acc['action'] = pd.Categorical(acc['action'], categories=sorted_actions, ordered=True)
    return acc, sorted_actions


def plot_joint_accuracy_per_action(filtered_acc: pd.DataFrame, title: str, save_path: str = None, filename_prefix: str = "plot"):
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=filtered_acc, x='action', y='accuracy', hue='model', marker='o', palette=PALETTE)
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
    bars = sns.barplot(data=model_avg, x='model', y='accuracy', palette=PALETTE)
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


def plot_best_worst_joint_barplot(best_acc: pd.DataFrame, worst_acc: pd.DataFrame, save_path: str = None, filename_prefix: str = "joint_comparison"):
    # Compute mean accuracy per model
    best_avg = best_acc.groupby('model')['accuracy'].mean().reset_index()
    best_avg['condition'] = 'Best'

    worst_avg = worst_acc.groupby('model')['accuracy'].mean().reset_index()
    worst_avg['condition'] = 'Worst'

    # Lighten the color for 'Worst' condition
    def adjust_saturation(color, factor=0.3):
        r, g, b = color
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        r_new, g_new, b_new = colorsys.hls_to_rgb(h, l, s * factor)
        return (r_new, g_new, b_new)

    light_palette = {
        model: adjust_saturation(color)
        for model, color in PALETTE.items()
    }

    # Force all models to be present in both averages
    models = MODEL_ORDER

    # Ensure all models exist in both best and worst averages
    for model in models:
        if model not in best_avg['model'].values:
            print(f"Adding missing model to best_avg: {model}")
            best_avg = pd.concat([best_avg, pd.DataFrame([{'model': model, 'accuracy': 0.0, 'condition': 'Best'}])],
                                 ignore_index=True)
        if model not in worst_avg['model'].values:
            print(f"Adding missing model to worst_avg: {model}")
            worst_avg = pd.concat([worst_avg, pd.DataFrame([{'model': model, 'accuracy': 0.0, 'condition': 'Worst'}])],
                                  ignore_index=True)

    # Reindex to match plotting order
    best_values = best_avg.set_index('model').reindex(models, fill_value=0)['accuracy']
    worst_values = worst_avg.set_index('model').reindex(models, fill_value=0)['accuracy']

    # Plotting
    x = np.arange(len(models))
    width = 0.43
    fig, ax = plt.subplots(figsize=(10, 5))

    # Worst = left
    bars_worst = ax.bar(x - width / 2, worst_values, width,
                        color=[light_palette[m] for m in models],
                        label='_nolegend_')

    # Best = right
    bars_best = ax.bar(x + width / 2, best_values, width,
                       color=[PALETTE[m] for m in models],
                       label='_nolegend_')

    # Add difference bars (on top of worst, with low opacity)
    diff_values = best_values - worst_values
    bars_diff = ax.bar(x - width / 2, diff_values, width,
                       bottom=worst_values,
                       color=[PALETTE[m] for m in models],
                       alpha=0.1,
                       edgecolor='none',
                       label='_nolegend_')

    # Draw vertical + horizontal lines from worst to best bar top
    for i, model in enumerate(models):
        x_left = x[i] - width / 2
        x_left_mx = x[i] - width
        x_right = x[i] + width / 2
        x_right_mx = x[i] + width
        y_worst = worst_values[model]
        y_best = best_values[model]

        if y_best != y_worst:
            # Vertical segment from worst to best height at left bar
            ax.plot([x_left, x_left],
                    [y_worst, y_best],
                    color='black',
                    linestyle=':',
                    linewidth=1.2,
                    alpha=0.6)

            # Horizontal segment connecting worst to best bar top
            ax.plot([x_left_mx, x_right_mx],
                    [y_best, y_best],
                    color='black',
                    linestyle=':',
                    linewidth=1.2,
                    alpha=0.6)

            # # Optional delta label
            # ax.annotate(f'Δ {y_best - y_worst:.2f}',
            #             xy=((x_left + x_right) / 2, y_best + 0.015),
            #             ha='center', va='bottom',
            #             fontsize=9, color='black')

    # Annotate
    for bars in [bars_best, bars_worst]:
        for bar in bars:
            height = bar.get_height()
            if height >= 0:
                ax.annotate(f'{height:.2f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                            ha='center', va='bottom', fontsize=11)

    # Axes + custom legend
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Accuracy", fontsize=14)
    ax.set_title("Best vs Worst Accuracy per Model", fontsize=16)
    ax.grid(True, axis='y', linestyle='--', alpha=0.5)

    from matplotlib.patches import Patch
    legend_patches = [Patch(color=PALETTE[model], label=model) for model in models]
    ax.legend(handles=legend_patches, title="Model (Best)")

    plt.tight_layout()

    if save_path:
        filename = f"{filename_prefix}_barplot_combined.pdf"
        plt.savefig(os.path.join(save_path, filename), format='pdf')
    plt.show()


experiment_name = "top_20_kinetics_actions"
model_names = ["mvit_base_16x4", "slow_r50", "slowfast_r50", "tc_clip", "x3d_xs"]
file_paths = [f"model_results/{experiment_name}/video_results_extended_{model_name}.csv" for model_name in model_names]
output_path = rf"output_plots\{experiment_name}\model_accuracy"

# Compute joint accuracy
joint_acc, _ = compute_joint_accuracy(file_paths)

# --- Best background+camera ---
joint_best = get_joint_best_or_worst_per_action(joint_acc, best=True)
best_joint_filtered, sorted_actions = prepare_filtered_joint_accuracy(joint_acc, joint_best)
base_actions = best_joint_filtered['action'].cat.categories.tolist()  # ✅ used for filtering worst

# Plot best background+camera
# best_joint_model_avg = plot_joint_accuracy_per_action(
#     best_joint_filtered,
#     "Accuracy per Action (Best Background + Camera Distance)",
#     output_path,
#     "best_joint"
# )

# --- Worst background+camera using same action columns ---
joint_worst = get_joint_best_or_worst_per_action(joint_acc, best=False)
worst_joint_filtered, _ = prepare_filtered_joint_accuracy(joint_acc, joint_worst, sorted_actions, base_actions)

# Plot worst background+camera
# worst_joint_model_avg = plot_joint_accuracy_per_action(
#     worst_joint_filtered,
#     "Accuracy per Action (Worst Background + Camera Distance)",
#     output_path,
#     "worst_joint"
# )


plot_best_worst_joint_barplot(
    best_joint_filtered,
    worst_joint_filtered,
    save_path=output_path,
    filename_prefix="best_vs_worst_joint"
)
