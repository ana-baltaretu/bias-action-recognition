import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re
import numpy as np
from collections import defaultdict

np.random.seed(42)

from matplotlib.offsetbox import OffsetImage, DrawingArea, AnnotationBbox, HPacker, VPacker, TextArea
import matplotlib.image as mpimg
import matplotlib.patches as mpatches


def add_vertical_legend_with_images(ax, entries, image_scale=0.115):
    """
    entries = list of tuples: (image_path, label, marker_style, color)
    """
    legend_items = []

    for image_path, label, marker, color in entries:
        # Load image
        img = mpimg.imread(image_path)
        image = OffsetImage(img, zoom=image_scale)

        # Marker
        marker_box = DrawingArea(20, 20, 0, 0)
        if marker == 'o':
            patch = mpatches.Circle((10, 10), radius=6, facecolor=color, edgecolor='black', linewidth=1)
        elif marker == 's':
            patch = mpatches.Rectangle((4, 4), 12, 12, facecolor=color, edgecolor='black', linewidth=1)
        else:
            patch = mpatches.RegularPolygon((10, 10), numVertices=6, radius=6, orientation=0, facecolor=color)
        marker_box.add_artist(patch)

        # Label
        label_text = TextArea(label, textprops={'fontsize': 12})

        # Marker + label side by side
        label_row = HPacker(children=[marker_box, label_text], align="center", pad=0, sep=6)

        # Stack label + image
        entry = VPacker(children=[label_row, image], align="center", pad=0, sep=4)

        legend_items.append(entry)

    # Stack all entries vertically
    legend_box = HPacker(children=legend_items, align="left", pad=5, sep=10)

    # Put legend in top-right of plot area
    ab = AnnotationBbox(
        legend_box, (0.985, 0.97),
        xycoords='axes fraction',
        box_alignment=(1, 1),
        frameon=True,
        pad=0.5
    )
    ax.add_artist(ab)


def plot_best_model_per_action_background(file_paths, save_path=None):
    model_dfs = []

    for file_path in file_paths:
        df = pd.read_csv(file_path)
        initial_df = df[df['video'].str.contains('_initial')]

        # Extract model name
        model_name = os.path.basename(file_path)
        model_name = re.sub(r'^video_results_extended_(.+?)\.csv$', r'\1', model_name)

        # Accuracy per (action, background)
        correct_counts = (
            initial_df[initial_df['result'] == 'correct']
            .groupby(['true_label', 'background'])
            .size()
        )
        total_counts = (
            initial_df
            .groupby(['true_label', 'background'])
            .size()
        )
        accuracy = (correct_counts / total_counts).unstack().fillna(0) * 100
        accuracy = accuracy[(accuracy != 0).any(axis=1)]

        accuracy_long = accuracy.reset_index().melt(
            id_vars='true_label',
            var_name='background',
            value_name='accuracy'
        )
        accuracy_long['model'] = model_name
        model_dfs.append(accuracy_long)

    all_data = pd.concat(model_dfs, ignore_index=True)

    # Filter for actions with non-zero accuracy
    non_zero_actions = all_data.groupby('true_label')['accuracy'].max().reset_index()
    top_actions = non_zero_actions[non_zero_actions['accuracy'] > 0]['true_label'].tolist()
    all_data = all_data[all_data['true_label'].isin(top_actions)]

    # Group by action and background to find best accuracy
    best_df = (
        all_data
        .groupby(['true_label', 'background'])['accuracy']
        .max()
        .reset_index()
    )

    # Sort actions by their highest accuracy
    sorted_actions = (
        best_df.groupby('true_label')['accuracy']
        .max()
        .sort_values(ascending=False)
        .index.tolist()
    )
    best_df['true_label'] = pd.Categorical(best_df['true_label'], categories=sorted_actions, ordered=True)

    # Plot
    plt.figure(figsize=(12, 6))
    sns.barplot(
        data=best_df,
        x='true_label',
        y='accuracy',
        hue='background',
        palette=["#F45D01", "#8D909B", "#09A129"],
        edgecolor='black'
    )

    plt.title("Best model accuracy per action and background", fontsize=16)
    plt.xlabel("Action", fontsize=14)
    plt.ylabel("Accuracy (%)", fontsize=14)
    plt.xticks(fontsize=12, rotation=45, ha='right')
    plt.yticks(fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)

    plt.gca().get_legend().remove()

    plt.tight_layout()

    entries = [
        ("autumn_hockey.png", "autumn_hockey", 's', "#F45D01"),
        ("konzerthaus.png", "konzerthaus", 's', "#8D909B"),
        ("stadium_01.png", "stadium_01", 's', "#09A129"),
    ]
    add_vertical_legend_with_images(plt.gca(), entries)

    # plt.legend(title="Background", title_fontsize=18, fontsize=18)
    # plt.tight_layout()

    if save_path:
        filename = "best_accuracy_per_action_background.pdf"
        plt.savefig(os.path.join(save_path, filename), format='pdf')
        print(f"Saved: {filename}")
    plt.show()


def plot_predicted_distribution_per_action_background(file_paths, save_path=None):
    model_dfs = []

    for file_path in file_paths:
        df = pd.read_csv(file_path)
        initial_df = df[df['video'].str.contains('_initial')]

        # Extract model name
        model_name = os.path.basename(file_path)
        model_name = re.sub(r'^video_results_extended_(.+?)\.csv$', r'\1', model_name)

        # Count how often each action was predicted per background
        prediction_counts = (
            initial_df.groupby(['mapped_prediction', 'background'])
            .size()
            .reset_index(name='count')
        )
        prediction_counts['model'] = model_name
        model_dfs.append(prediction_counts)

    all_data = pd.concat(model_dfs, ignore_index=True)

    # Normalize per predicted action to get proportions
    total_per_action = (
        all_data.groupby(['model', 'mapped_prediction'])['count']
        .sum()
        .reset_index(name='total')
    )
    merged = all_data.merge(total_per_action, on=['model', 'mapped_prediction'])
    merged['proportion'] = merged['count'] / merged['total'] * 100

    # Now average across models
    avg_proportion = (
        merged.groupby(['mapped_prediction', 'background'])['proportion']
        .mean()
        .reset_index()
    )

    total_per_action = (
        avg_proportion.groupby('mapped_prediction')['proportion']
            .sum()
            .reset_index(name='total')
    )
    avg_proportion = avg_proportion.merge(total_per_action, on='mapped_prediction')
    avg_proportion['proportion'] = avg_proportion['proportion'] / avg_proportion['total'] * 100

    # Sort predicted labels by total average predictions
    sorted_labels = (
        avg_proportion.groupby('mapped_prediction')['proportion']
        .sum()
        .sort_values(ascending=False)
        .index.tolist()
    )
    avg_proportion['mapped_prediction'] = pd.Categorical(avg_proportion['mapped_prediction'],
                                                         categories=sorted_labels, ordered=True)

    # Pivot for stacked bar plot
    pivot = avg_proportion.pivot(index='mapped_prediction', columns='background', values='proportion').fillna(0)

    # Plot
    pivot.plot(kind='bar', stacked=True, figsize=(14, 7),
               color=["#F45D01", "#8D909B", "#09A129"], edgecolor='black')

    plt.title("Predicted action distribution by background (averaged across models)", fontsize=16)
    plt.xlabel("Predicted Action", fontsize=14)
    plt.ylabel("Proportion of Predictions (%)", fontsize=14)
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.yticks(fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.legend(title="Background", title_fontsize=13, fontsize=11)
    plt.tight_layout()

    if save_path:
        filename = "predicted_distribution_per_action_background.pdf"
        plt.savefig(os.path.join(save_path, filename), format='pdf')
        print(f"Saved: {filename}")

    plt.show()


def plot_action_distribution_per_background_stacked(file_paths, save_path=None):

    model_dfs = []

    for file_path in file_paths:
        df = pd.read_csv(file_path)
        initial_df = df[df['video'].str.contains('_initial')]

        # Extract model name
        model_name = os.path.basename(file_path)
        model_name = re.sub(r'^video_results_extended_(.+?)\.csv$', r'\1', model_name)

        # Count how often each action was predicted per background
        prediction_counts = (
            initial_df.groupby(['background', 'mapped_prediction'])
            .size()
            .reset_index(name='count')
        )
        prediction_counts['model'] = model_name
        model_dfs.append(prediction_counts)

    all_data = pd.concat(model_dfs, ignore_index=True)

    # Normalize per background (not action!)
    total_per_background = (
        all_data.groupby(['model', 'background'])['count']
        .sum()
        .reset_index(name='total')
    )
    merged = all_data.merge(total_per_background, on=['model', 'background'])
    merged['proportion'] = merged['count'] / merged['total'] * 100

    # Average across models
    avg_prop = (
        merged.groupby(['background', 'mapped_prediction'])['proportion']
            .mean()
            .reset_index()
    )

    # Re-normalize so proportions sum to 100 per background
    total_per_background = (
        avg_prop.groupby('background')['proportion']
            .sum()
            .reset_index(name='total')
    )
    avg_prop = avg_prop.merge(total_per_background, on='background')
    avg_prop['proportion'] = avg_prop['proportion'] / avg_prop['total'] * 100

    # Group actions with less than 1% into 'other'
    avg_prop['mapped_prediction'] = avg_prop['mapped_prediction'].astype(str)
    avg_prop.loc[avg_prop['proportion'] < 2, 'mapped_prediction'] = 'other'

    # Re-aggregate after merging small ones into 'other'
    avg_prop = (
        avg_prop.groupby(['background', 'mapped_prediction'])['proportion']
            .sum()
            .reset_index()
    )

    # Re-normalize so everything sums to 100 again
    total_per_background = (
        avg_prop.groupby('background')['proportion']
            .sum()
            .reset_index(name='total')
    )
    avg_prop = avg_prop.merge(total_per_background, on='background')
    avg_prop['proportion'] = avg_prop['proportion'] / avg_prop['total'] * 100

    # Sort for plotting consistency
    top_actions = (
        avg_prop.groupby('mapped_prediction')['proportion']
            .sum()
            .sort_values(ascending=False)
            .index.tolist()
    )
    avg_prop['mapped_prediction'] = pd.Categorical(avg_prop['mapped_prediction'], categories=top_actions, ordered=True)

    # Pivot: index = background, columns = predicted action
    pivot = avg_prop.pivot(index='background', columns='mapped_prediction', values='proportion').fillna(0)

    # Drop 'other' column *after* everything is normalized
    if 'other' in pivot.columns:
        pivot = pivot.drop(columns='other')

    # Plot
    pivot.plot(kind='bar', stacked=True, figsize=(12, 12),
               edgecolor='black', colormap='tab20')

    plt.title("Action prediction distribution per background (avg. across models)", fontsize=16)
    plt.xlabel("Background", fontsize=14)
    plt.ylabel("Proportion of Predictions (%)", fontsize=14)
    plt.xticks(rotation=0, fontsize=12)
    plt.yticks(fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.legend(title="Predicted Action", title_fontsize=13, fontsize=9, bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

    if save_path:
        filename = "action_distribution_per_background.pdf"
        plt.savefig(os.path.join(save_path, filename), format='pdf')
        print(f"Saved: {filename}")

    plt.show()


def plot_action_distribution_per_background(file_paths, save_path=None):

    model_dfs = []

    for file_path in file_paths:
        df = pd.read_csv(file_path)
        initial_df = df[df['video'].str.contains('_initial')]

        # Extract model name
        model_name = os.path.basename(file_path)
        model_name = re.sub(r'^video_results_extended_(.+?)\.csv$', r'\1', model_name)

        # Count how often each action was predicted per background
        prediction_counts = (
            initial_df.groupby(['background', 'mapped_prediction'])
            .size()
            .reset_index(name='count')
        )
        prediction_counts['model'] = model_name
        model_dfs.append(prediction_counts)

    all_data = pd.concat(model_dfs, ignore_index=True)

    # Normalize per background (not action!)
    total_per_background = (
        all_data.groupby(['model', 'background'])['count']
        .sum()
        .reset_index(name='total')
    )
    merged = all_data.merge(total_per_background, on=['model', 'background'])
    merged['proportion'] = merged['count'] / merged['total'] * 100

    # Average across models
    avg_prop = (
        merged.groupby(['background', 'mapped_prediction'])['proportion']
            .mean()
            .reset_index()
    )

    # Re-normalize so proportions sum to 100 per background
    total_per_background = (
        avg_prop.groupby('background')['proportion']
            .sum()
            .reset_index(name='total')
    )
    avg_prop = avg_prop.merge(total_per_background, on='background')
    avg_prop['proportion'] = avg_prop['proportion'] / avg_prop['total'] * 100

    # Group actions with less than 1% into 'other'
    avg_prop['mapped_prediction'] = avg_prop['mapped_prediction'].astype(str)
    avg_prop.loc[avg_prop['proportion'] < 4, 'mapped_prediction'] = 'other'

    # Re-aggregate after merging small ones into 'other'
    avg_prop = (
        avg_prop.groupby(['background', 'mapped_prediction'])['proportion']
            .sum()
            .reset_index()
    )

    # Re-normalize so everything sums to 100 again
    total_per_background = (
        avg_prop.groupby('background')['proportion']
            .sum()
            .reset_index(name='total')
    )
    avg_prop = avg_prop.merge(total_per_background, on='background')
    avg_prop['proportion'] = avg_prop['proportion'] / avg_prop['total'] * 100

    # Sort for plotting consistency
    top_actions = (
        avg_prop.groupby('mapped_prediction')['proportion']
            .sum()
            .sort_values(ascending=False)
            .index.tolist()
    )
    # Drop 'other' before plotting
    avg_prop = avg_prop[avg_prop['mapped_prediction'] != 'other']

    # Sort backgrounds and actions for consistent plotting
    avg_prop['background'] = pd.Categorical(avg_prop['background'], categories=sorted(avg_prop['background'].unique()),
                                            ordered=True)

    plt.figure(figsize=(14, 8))
    sns.barplot(
        data=avg_prop,
        x='background',
        y='proportion',
        hue='mapped_prediction',
        palette='tab20',
        dodge=True,
        edgecolor='black'
    )

    plt.title("Action prediction distribution per background (avg. across models)", fontsize=16)
    plt.xlabel("Background", fontsize=14)
    plt.ylabel("Proportion of Predictions (%)", fontsize=14)
    plt.xticks(rotation=0, fontsize=12)
    plt.yticks(fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.legend(title="Predicted Action", title_fontsize=13, fontsize=9, bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

    if save_path:
        filename = "action_distribution_per_background.pdf"
        plt.savefig(os.path.join(save_path, filename), format='pdf')
        print(f"Saved: {filename}")

    plt.show()


def plot_best_model_per_action_background_subplots(file_paths, save_path=None):
    model_dfs = []
    model_names = []

    # Load and process data for all models
    for file_path in file_paths:
        df = pd.read_csv(file_path)
        initial_df = df[df['video'].str.contains('_initial')]

        # Extract model name
        model_name = os.path.basename(file_path)
        model_name = re.sub(r'^video_results_extended_(.+?)\.csv$', r'\1', model_name)
        model_names.append(model_name)

        # Accuracy per (action, background)
        correct_counts = (
            initial_df[initial_df['result'] == 'correct']
            .groupby(['true_label', 'background'])
            .size()
        )
        total_counts = (
            initial_df
            .groupby(['true_label', 'background'])
            .size()
        )
        accuracy = (correct_counts / total_counts).unstack().fillna(0) * 100
        accuracy = accuracy[(accuracy != 0).any(axis=1)]

        accuracy_long = accuracy.reset_index().melt(
            id_vars='true_label',
            var_name='background',
            value_name='accuracy'
        )
        accuracy_long['model'] = model_name
        model_dfs.append(accuracy_long)

    # Combine all data
    all_data = pd.concat(model_dfs, ignore_index=True)

    # Determine common sorted actions
    sorted_actions = (
        all_data.groupby('true_label')['accuracy']
        .max()
        .sort_values(ascending=False)
        .index.tolist()
    )

    all_data['true_label'] = pd.Categorical(
        all_data['true_label'],
        categories=sorted_actions,
        ordered=True
    )

    # Subplot layout: all subplots in one row
    num_models = len(model_names)
    cols = num_models
    rows = 1

    fig, axes = plt.subplots(rows, cols, figsize=(6 * cols, 5), squeeze=False)

    for idx, model_name in enumerate(model_names):
        ax = axes[0][idx]
        model_data = all_data[all_data['model'] == model_name]

        sns.barplot(
            data=model_data,
            x='true_label',
            y='accuracy',
            hue='background',
            palette=["#F45D01", "#8D909B", "#09A129"],
            ax=ax,
            edgecolor='black'
        )
        ax.set_title(model_name, fontsize=14)
        ax.set_xlabel("Action", fontsize=12)
        ax.set_ylabel("Accuracy (%)", fontsize=12)
        ax.tick_params(axis='x', labelrotation=45)
        ax.grid(True, linestyle='--', alpha=0.5)

    # Hide unused subplots
    for i in range(num_models, rows * cols):
        fig.delaxes(axes[i // cols][i % cols])

    handles, labels = axes[0][0].get_legend_handles_labels()
    fig.legend(handles, labels, title='Background', title_fontsize=13, fontsize=11, loc='upper right')
    fig.suptitle("Best Accuracy per Action and Background (per Model)", fontsize=16)
    plt.tight_layout(rect=[0, 0, 0.96, 0.95])

    if save_path:
        filename = "subplots_accuracy_per_action_background.pdf"
        plt.savefig(os.path.join(save_path, filename), format='pdf')
        print(f"Saved: {filename}")

    plt.show()


experiment_name = "top_20_kinetics_actions"
model_names = ["mvit_base_16x4", "slow_r50", "slowfast_r50", "tc_clip", "x3d_xs"]
file_paths = [f"model_results/{experiment_name}/video_results_extended_{model_name}.csv" for model_name in model_names]
output_path = rf"output_plots\{experiment_name}\background"
plot_best_model_per_action_background(file_paths, output_path)
# plot_best_model_per_action_background_subplots(file_paths, output_path)
# plot_predicted_distribution_per_action_background(file_paths, output_path)
# plot_action_distribution_per_background_stacked(file_paths, output_path)
# plot_action_distribution_per_background(file_paths, output_path)


