import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re
import numpy as np
from collections import defaultdict
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

np.random.seed(42)

jitter_strength = 0.05  # adjust how much noise




def plot_camera_distance_accuracy(file_path):
    # Load the CSV
    df = pd.read_csv(file_path)

    # Filter to only include '_initial' videos
    initial_df = df[df['video'].str.contains('_initial')]

    # Group by camera_distance and calculate normalized result counts
    result_counts = (
        initial_df.groupby("camera_distance")["result"]
        .value_counts(normalize=True)
        .unstack()
        .fillna(0) * 100
    )

    # Plot
    ax = result_counts.plot(
        kind="bar",
        stacked=True,
        figsize=(8, 6)
    )

    # Add labels and title
    plt.ylabel("Percentage")
    plt.title("Prediction Accuracy by Camera Distance (Initial Videos Only)")
    plt.xticks(rotation=45)
    plt.legend(title="Prediction Result", loc="upper right")
    plt.tight_layout()
    plt.show()


def plot_line_chart_camera_distance_accuracy_per_action(file_path):
    # Load and filter to _initial videos
    df = pd.read_csv(file_path)
    initial_df = df[df['video'].str.contains('_initial')]

    # Compute % correct for each action-camera_distance pair
    grouped = (
            initial_df[initial_df['result'] == 'correct']
            .groupby(['true_label', 'camera_distance'])
            .size()
            .div(initial_df.groupby(['true_label', 'camera_distance']).size())
            .unstack()
            .fillna(0) * 100
    )

    # Plot line chart
    grouped.plot(
        kind='line',
        marker='o',
        figsize=(10, 6)
    )

    plt.ylabel("Correct Prediction Percentage")
    plt.title("Accuracy per Action by Camera Distance (Initial Videos Only)")
    plt.xticks(rotation=45, ha='right')
    plt.legend(title="Camera Distance")
    plt.tight_layout()
    plt.show()


def plot_avg_accuracy_camera_distance_per_action_with_std(file_paths):
    model_results = []

    for file_path in file_paths:
        df = pd.read_csv(file_path)
        initial_df = df[df['video'].str.contains('_initial')]

        # Compute per (action, camera_distance) accuracy
        correct_counts = (
            initial_df[initial_df['result'] == 'correct']
            .groupby(['true_label', 'camera_distance'])
            .size()
        )
        total_counts = (
            initial_df
            .groupby(['true_label', 'camera_distance'])
            .size()
        )
        accuracy = (correct_counts / total_counts).unstack().fillna(0) * 100
        model_results.append(accuracy)

    # Concatenate and compute mean and std
    all_models = pd.concat(model_results, keys=range(len(model_results)))  # Multi-index: (model_index, action)
    mean_accuracy = all_models.groupby(level=1).mean()  # level=1 is true_label
    std_accuracy = all_models.groupby(level=1).std()

    # Plot with error bars (std dev)
    ax = mean_accuracy.plot(
        kind='line',
        yerr=std_accuracy,
        marker='o',
        figsize=(12, 7),
        capsize=4
    )

    plt.ylabel("Correct Prediction Percentage (Avg ± Std)")
    plt.title("Average Accuracy per Action by Camera Distance (Initial Videos Only)")
    plt.xticks(rotation=45, ha='right')
    plt.legend(title="Camera Distance")
    plt.tight_layout()
    plt.show()


def plot_violin_with_mean_line(file_paths, save_path=None):
    model_dfs = []

    for model_idx, file_path in enumerate(file_paths):
        df = pd.read_csv(file_path)
        initial_df = df[df['video'].str.contains('_initial')]

        # Compute per (action, camera_distance) accuracy
        correct_counts = (
            initial_df[initial_df['result'] == 'correct']
                .groupby(['true_label', 'camera_distance'])
                .size()
        )
        total_counts = (
            initial_df
                .groupby(['true_label', 'camera_distance'])
                .size()
        )
        accuracy = (correct_counts / total_counts).unstack().fillna(0) * 100

        # Drop actions where all camera distances have 0 accuracy
        accuracy = accuracy[(accuracy != 0).any(axis=1)]

        # Convert to long-form
        accuracy_long = accuracy.reset_index().melt(
            id_vars='true_label',
            var_name='camera_distance',
            value_name='accuracy'
        )
        accuracy_long['model'] = model_idx
        model_dfs.append(accuracy_long)

    all_data = pd.concat(model_dfs, ignore_index=True)

    # Sort true_labels by max mean accuracy (over camera distances)
    avg_acc = (
        all_data
            .groupby(['true_label', 'camera_distance'])['accuracy']
            .mean()
            .groupby('true_label')
            .max()
            .sort_values(ascending=False)
    )
    sorted_labels = avg_acc.index.tolist()
    all_data['true_label'] = pd.Categorical(all_data['true_label'], categories=sorted_labels, ordered=True)

    # Plot
    plt.figure(figsize=(16, 8))  # slightly larger for better layout

    sns.violinplot(
        data=all_data,
        x='true_label',
        y='accuracy',
        hue='camera_distance',
        split=True,
        inner=None,
        cut=0,
        scale="width",
        width=0.9
    )

    sns.pointplot(
        data=all_data,
        x='true_label',
        y='accuracy',
        hue='camera_distance',
        errorbar=None,
        markers='o',
        linestyles='-',
        palette='dark',
        dodge=0.3
    )

    plt.title("Effect of camera distance on the average performance of models.", fontsize=18)
    plt.ylabel("Accuracy", fontsize=14)
    plt.xlabel("Action label", fontsize=14)
    plt.xticks(rotation=45, ha='right', fontsize=18)
    plt.yticks(fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(title="Camera Distance", title_fontsize=18, fontsize=12)
    plt.tight_layout()

    # Save to PDF if save_path is provided
    if save_path:
        plt.savefig(os.path.join(save_path, "plot_camera_distance_violin.pdf"), format='pdf')
        print(f"Plot saved to {save_path}")
    plt.show()


def plot_boxplot_accuracy(file_paths, save_path=None):
    model_dfs = []

    for model_idx, file_path in enumerate(file_paths):
        df = pd.read_csv(file_path)
        initial_df = df[df['video'].str.contains('_initial')]

        # Compute per (action, camera_distance) accuracy
        correct_counts = (
            initial_df[initial_df['result'] == 'correct']
                .groupby(['true_label', 'camera_distance'])
                .size()
        )
        total_counts = (
            initial_df
                .groupby(['true_label', 'camera_distance'])
                .size()
        )
        accuracy = (correct_counts / total_counts).unstack().fillna(0) * 100

        # Drop actions where all camera distances have 0 accuracy
        accuracy = accuracy[(accuracy != 0).any(axis=1)]

        # Convert to long-form
        accuracy_long = accuracy.reset_index().melt(
            id_vars='true_label',
            var_name='camera_distance',
            value_name='accuracy'
        )
        accuracy_long['model'] = model_idx
        model_dfs.append(accuracy_long)

    all_data = pd.concat(model_dfs, ignore_index=True)

    # Sort true_labels by max mean accuracy (over camera distances)
    avg_acc = (
        all_data
            .groupby(['true_label', 'camera_distance'])['accuracy']
            .mean()
            .groupby('true_label')
            .max()
            .sort_values(ascending=False)
    )
    sorted_labels = avg_acc.index.tolist()
    all_data['true_label'] = pd.Categorical(all_data['true_label'], categories=sorted_labels, ordered=True)

    # Plot
    plt.figure(figsize=(16, 8))

    # Base boxplot per model
    sns.boxplot(
        data=all_data,
        x='true_label',
        y='accuracy',
        hue='camera_distance',
        width=0.8,
        fliersize=2,
        linewidth=1.5
    )

    # Compute average accuracy per action per camera distance across models
    avg_per_action_distance = (
        all_data
            .groupby(['true_label', 'camera_distance'])['accuracy']
            .mean()
            .reset_index()
    )

    # Overlay lines between average points
    sns.pointplot(
        data=all_data,
        x='true_label',
        y='accuracy',
        hue='camera_distance',
        errorbar=None,
        markers='o',
        linestyles='-',
        palette='dark',
        dodge=0.4
    )

    plt.title("Effect of camera distance on the average performance of models.", fontsize=18)
    plt.ylabel("Accuracy", fontsize=18)
    plt.xlabel("Action label", fontsize=18)
    plt.xticks(rotation=45, ha='right', fontsize=18)
    plt.yticks(fontsize=18)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(title="Camera Distance", title_fontsize=18, fontsize=12)

    plt.tight_layout()

    if save_path:
        plt.savefig(os.path.join(save_path, "plot_camera_distance_box.pdf"), format='pdf')
        print(f"Plot saved to {save_path}")
    plt.show()


def plot_avg_bar_accuracy(file_paths, save_path=None):
    model_dfs = []

    for model_idx, file_path in enumerate(file_paths):
        df = pd.read_csv(file_path)
        initial_df = df[df['video'].str.contains('_initial')]

        # Compute per (action, camera_distance) accuracy
        correct_counts = (
            initial_df[initial_df['result'] == 'correct']
                .groupby(['true_label', 'camera_distance'])
                .size()
        )
        total_counts = (
            initial_df
                .groupby(['true_label', 'camera_distance'])
                .size()
        )
        accuracy = (correct_counts / total_counts).unstack().fillna(0) * 100

        # Drop actions where all camera distances have 0 accuracy
        accuracy = accuracy[(accuracy != 0).any(axis=1)]

        # Convert to long-form
        accuracy_long = accuracy.reset_index().melt(
            id_vars='true_label',
            var_name='camera_distance',
            value_name='accuracy'
        )
        accuracy_long['model'] = model_idx
        model_dfs.append(accuracy_long)

    all_data = pd.concat(model_dfs, ignore_index=True)

    # Compute average accuracy per (action, camera distance)
    avg_per_action_distance = (
        all_data
        .groupby(['true_label', 'camera_distance'])['accuracy']
        .mean()
        .reset_index()
    )

    # Sort actions by max avg accuracy
    sorted_labels = (
        avg_per_action_distance
        .groupby('true_label')['accuracy']
        .max()
        .sort_values(ascending=False)
        .index.tolist()
    )
    avg_per_action_distance['true_label'] = pd.Categorical(
        avg_per_action_distance['true_label'],
        categories=sorted_labels,
        ordered=True
    )

    # Plot
    plt.figure(figsize=(16, 8))
    sns.barplot(
        data=avg_per_action_distance,
        x='true_label',
        y='accuracy',
        hue='camera_distance',
        palette='dark'
    )

    plt.title("Average accuracy per action and camera distance", fontsize=18)
    plt.ylabel("Mean Accuracy", fontsize=18)
    plt.xlabel("Action label", fontsize=18)
    plt.xticks(rotation=45, ha='right', fontsize=18)
    plt.yticks(fontsize=18)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(title="Camera Distance", title_fontsize=18, fontsize=12)
    plt.tight_layout()

    if save_path:
        plt.savefig(os.path.join(save_path, "plot_camera_distance_bar.pdf"), format='pdf')
        print(f"Plot saved to {save_path}")
    plt.show()


def plot_avg_bar_accuracy_grouped_by_camera(file_paths, save_path=None, top_k_actions=10):
    model_dfs = []

    for model_idx, file_path in enumerate(file_paths):
        df = pd.read_csv(file_path)
        initial_df = df[df['video'].str.contains('_initial')]

        # Compute per (action, camera_distance) accuracy
        correct_counts = (
            initial_df[initial_df['result'] == 'correct']
                .groupby(['true_label', 'camera_distance'])
                .size()
        )
        total_counts = (
            initial_df
                .groupby(['true_label', 'camera_distance'])
                .size()
        )
        accuracy = (correct_counts / total_counts).unstack().fillna(0) * 100

        # Drop actions where all camera distances have 0 accuracy
        accuracy = accuracy[(accuracy != 0).any(axis=1)]

        # Convert to long-form
        accuracy_long = accuracy.reset_index().melt(
            id_vars='true_label',
            var_name='camera_distance',
            value_name='accuracy'
        )
        accuracy_long['model'] = model_idx
        model_dfs.append(accuracy_long)

    all_data = pd.concat(model_dfs, ignore_index=True)

    # Compute average accuracy per (camera_distance, action)
    avg_per_action_distance = (
        all_data
        .groupby(['camera_distance', 'true_label'])['accuracy']
        .mean()
        .reset_index()
    )

    # Optionally: limit to top_k actions based on overall max performance
    top_actions = (
        avg_per_action_distance
        .groupby('true_label')['accuracy']
        .max()
        .sort_values(ascending=False)
        .head(top_k_actions)
        .index
    )
    avg_per_action_distance = avg_per_action_distance[avg_per_action_distance['true_label'].isin(top_actions)]

    # Plot
    plt.figure(figsize=(16, 8))
    sns.barplot(
        data=avg_per_action_distance,
        x='camera_distance',
        y='accuracy',
        hue='true_label',
        palette='tab20'
    )

    plt.title("Average accuracy per camera distance (grouped by action)", fontsize=18)
    plt.ylabel("Mean Accuracy", fontsize=18)
    plt.xlabel("Camera Distance", fontsize=18)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.legend(title="Action", title_fontsize=16, fontsize=12, bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()

    if save_path:
        plt.savefig(os.path.join(save_path, "plot_camera_distance_bar_by_camera.pdf"), format='pdf')
        print(f"Plot saved to {save_path}")
    plt.show()


def plot_best_model_per_action_camera(file_paths, save_path=None):
    model_dfs = []

    for file_path in file_paths:
        df = pd.read_csv(file_path)
        initial_df = df[df['video'].str.contains('_initial')]

        # Extract model name
        model_name = os.path.basename(file_path)
        model_name = re.sub(r'^video_results_extended_(.+?)\.csv$', r'\1', model_name)

        # Accuracy per (action, camera)
        correct_counts = (
            initial_df[initial_df['result'] == 'correct']
            .groupby(['true_label', 'camera_distance'])
            .size()
        )
        total_counts = (
            initial_df
            .groupby(['true_label', 'camera_distance'])
            .size()
        )
        accuracy = (correct_counts / total_counts).unstack().fillna(0) * 100
        accuracy = accuracy[(accuracy != 0).any(axis=1)]

        accuracy_long = accuracy.reset_index().melt(
            id_vars='true_label',
            var_name='camera_distance',
            value_name='accuracy'
        )
        accuracy_long['model'] = model_name
        model_dfs.append(accuracy_long)

    all_data = pd.concat(model_dfs, ignore_index=True)

    # Keep only actions that have at least one non-zero accuracy
    non_zero_actions = (
        all_data.groupby('true_label')['accuracy']
            .max()
            .reset_index()
    )
    top_actions = non_zero_actions[non_zero_actions['accuracy'] > 0]['true_label'].tolist()

    all_data = all_data[all_data['true_label'].isin(top_actions)]
    # all_data['true_label'] = pd.Categorical(all_data['true_label'], categories=top_actions, ordered=True)

    # Get the best accuracy per (action, camera distance)
    best_df = (
        all_data
        .groupby(['true_label', 'camera_distance'])['accuracy']
        .max()
        .reset_index()
    )

    # Sort true_labels by max accuracy across camera distances
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
        hue='camera_distance',
        palette='tab10',
        edgecolor='black'
    )

    plt.title("Best model accuracy per action and camera distance", fontsize=16)
    plt.xlabel("Action", fontsize=14)
    plt.ylabel("Accuracy (%)", fontsize=14)
    plt.xticks(fontsize=12, rotation=45, ha='right')
    plt.yticks(fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(title="Camera Distance", title_fontsize=13, fontsize=11)
    plt.tight_layout()

    if save_path:
        filename = "best_accuracy_per_action_camera.pdf"
        plt.savefig(os.path.join(save_path, filename), format='pdf')
        print(f"Saved: {filename}")
    plt.show()


def plot_all_models_per_action_camera_subplots(file_paths, save_path=None):
    model_dfs = []

    for file_path in file_paths:
        df = pd.read_csv(file_path)
        initial_df = df[df['video'].str.contains('_initial')]

        # Extract model name
        model_name = os.path.basename(file_path)
        model_name = re.sub(r'^video_results_extended_(.+?)\.csv$', r'\1', model_name)

        # Accuracy per (action, camera)
        correct_counts = (
            initial_df[initial_df['result'] == 'correct']
            .groupby(['true_label', 'camera_distance'])
            .size()
        )
        total_counts = (
            initial_df
            .groupby(['true_label', 'camera_distance'])
            .size()
        )
        accuracy = (correct_counts / total_counts).unstack().fillna(0) * 100
        accuracy = accuracy[(accuracy != 0).any(axis=1)]

        accuracy_long = accuracy.reset_index().melt(
            id_vars='true_label',
            var_name='camera_distance',
            value_name='accuracy'
        )
        accuracy_long['model'] = model_name
        model_dfs.append(accuracy_long)

    all_data = pd.concat(model_dfs, ignore_index=True)

    # Keep only actions with at least one non-zero accuracy
    non_zero_actions = all_data.groupby('true_label')['accuracy'].max()
    valid_actions = non_zero_actions[non_zero_actions > 0].index.tolist()
    all_data = all_data[all_data['true_label'].isin(valid_actions)]

    # Sort actions by mean accuracy
    sorted_actions = (
        all_data.groupby('true_label')['accuracy']
        .mean()
        .sort_values(ascending=False)
        .index.tolist()
    )
    all_data['true_label'] = pd.Categorical(all_data['true_label'], categories=sorted_actions, ordered=True)

    models = all_data['model'].unique()
    fig, axes = plt.subplots(1, len(models), figsize=(6 * len(models), 6), sharey=True)

    if len(models) == 1:
        axes = [axes]

    for ax, model in zip(axes, models):
        model_data = all_data[all_data['model'] == model]
        sns.barplot(
            data=model_data,
            x='true_label',
            y='accuracy',
            hue='camera_distance',
            palette='tab10',
            edgecolor='black',
            ax=ax
        )
        ax.set_title(f"Model: {model}", fontsize=14)
        ax.set_xlabel("Action", fontsize=12)
        ax.set_ylabel("Accuracy (%)", fontsize=12)
        ax.tick_params(axis='x', rotation=45)

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, title="Camera Distance", bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.tight_layout()

    if save_path:
        filename = "all_models_accuracy_per_action_camera_subplots.pdf"
        plt.savefig(os.path.join(save_path, filename), format='pdf')
        print(f"Saved: {filename}")
    plt.show()


def plot_scatter_model_camera_shifted_with_violin(file_paths, save_path=None):
    model_dfs = []

    for file_path in file_paths:
        df = pd.read_csv(file_path)
        initial_df = df[df['video'].str.contains('_initial')]

        # Extract model name
        model_name = os.path.basename(file_path)
        model_name = re.sub(r'^video_results_extended_(.+?)\.csv$', r'\1', model_name)

        # Accuracy per (action, camera)
        correct_counts = (
            initial_df[initial_df['result'] == 'correct']
                .groupby(['true_label', 'camera_distance'])
                .size()
        )
        total_counts = (
            initial_df
                .groupby(['true_label', 'camera_distance'])
                .size()
        )
        accuracy = (correct_counts / total_counts).unstack().fillna(0) * 100
        accuracy = accuracy[(accuracy != 0).any(axis=1)]

        accuracy_long = accuracy.reset_index().melt(
            id_vars='true_label',
            var_name='camera_distance',
            value_name='accuracy'
        )
        accuracy_long['model'] = model_name
        model_dfs.append(accuracy_long)

    all_data = pd.concat(model_dfs, ignore_index=True)

    # Keep only actions with at least one non-zero accuracy
    valid_actions = all_data.groupby('true_label')['accuracy'].max()
    valid_actions = valid_actions[valid_actions > 0].index.tolist()
    all_data = all_data[all_data['true_label'].isin(valid_actions)]

    # Sort model names for x-axis
    model_order = sorted(all_data['model'].unique())
    model_to_x = {model: i for i, model in enumerate(model_order)}
    all_data['model_x'] = all_data['model'].map(model_to_x)

    # Define camera shift mapping
    camera_offsets = {
        'camera_far': -0.15,
        'camera_near': +0.15
    }
    all_data['x_shifted'] = all_data.apply(lambda row: row['model_x'] + camera_offsets.get(row['camera_distance'], 0), axis=1)

    # Color palette
    camera_palette = {'camera_far': '#1f77b4', 'camera_near': '#ff7f0e'}

    # Plot
    plt.figure(figsize=(14, 7))

    # Add violin plots (grouped by model and camera)
    for cam, offset in camera_offsets.items():
        for model in model_order:
            subset = all_data[(all_data['model'] == model) & (all_data['camera_distance'] == cam)]
            if not subset.empty:
                x_pos = model_to_x[model] + offset
                parts = plt.violinplot(
                    subset['accuracy'],
                    positions=[x_pos],
                    widths=0.25,
                    showmeans=False,
                    showmedians=False,
                    showextrema=False
                )
                for pc in parts['bodies']:
                    pc.set_facecolor(camera_palette[cam])
                    pc.set_edgecolor('none')
                    pc.set_alpha(0.2)

    # Overlay scatter points
    for cam in all_data['camera_distance'].unique():
        subset = all_data[all_data['camera_distance'] == cam]

        # Group identical (x, y) pairs
        max_jitter = 0.07
        grouped = subset.groupby(['x_shifted', 'accuracy'])
        jittered_x = []

        for (x_base, y_val), group in grouped:
            n = len(group)
            if n == 1:
                jittered_x.extend([x_base])
            else:
                # Generate evenly spaced offsets
                if n % 2 == 1:
                    offsets = np.linspace(-max_jitter, max_jitter, n)
                else:
                    offsets = np.linspace(-max_jitter + max_jitter / n, max_jitter - max_jitter / n, n)
                jittered_x.extend(x_base + offsets)

        subset['x_jittered'] = jittered_x



        plt.scatter(
            x=subset['x_jittered'],
            y=subset['accuracy'],
            color=camera_palette.get(cam, 'gray'),
            label=cam,
            s=80,
            edgecolor='black',
            alpha=0.7
        )

    plt.title("Accuracy per model by camera distance", fontsize=16)
    plt.xlabel("Model", fontsize=14)
    plt.ylabel("Accuracy (%)", fontsize=14)
    plt.xticks(ticks=list(model_to_x.values()), labels=model_order, rotation=45, ha='right', fontsize=12)
    plt.yticks(fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(title="Camera Distance", title_fontsize=13, fontsize=11)
    plt.tight_layout()

    if save_path:
        filename = "scatter_violin_accuracy_model_camera.pdf"
        plt.savefig(os.path.join(save_path, filename), format='pdf')
        print(f"Saved: {filename}")
    plt.show()

# model_name = "tc_clip" # mvit_base_16x4, slow_r50, slowfast_r50, tc_clip, x3d_xs
# file_path = f"model_results/older_runs/video_results_extended_{model_name}.csv"
# # plot_camera_distance_accuracy(file_path)
# plot_line_chart_camera_distance_accuracy_per_action(file_path)


# def add_image_with_label(ax, image_path, label, pos, marker):
#     # Load image
#     img = mpimg.imread(image_path)
#     imagebox = OffsetImage(img, zoom=0.15)
#
#     # Add image
#     ab = AnnotationBbox(imagebox, pos, frameon=False, xycoords='axes fraction')
#     ax.add_artist(ab)
#
#     # Add marker next to image
#     ax.plot(pos[0] - 0.03, pos[1], marker=marker, markersize=12, color='black', transform=ax.transAxes)
#
#     # Add label next to image
#     ax.text(pos[0] + 0.05, pos[1], label, transform=ax.transAxes,
#             fontsize=12, verticalalignment='center')


from matplotlib.offsetbox import OffsetImage, DrawingArea, AnnotationBbox, HPacker, VPacker, TextArea
import matplotlib.image as mpimg
import matplotlib.patches as mpatches

def add_custom_legend_with_images(ax, entries, image_scale=0.3):
    """
    entries = list of tuples: (image_path, label, marker_style, color)
    """
    legend_items = []

    for image_path, label, marker, color in entries:
        # Load image
        img = mpimg.imread(image_path)
        image = OffsetImage(img, zoom=image_scale)

        # Marker (circle or square)
        marker_box = DrawingArea(20, 20, 0, 0)
        if marker == 'o':
            patch = mpatches.Circle((10, 10), radius=6, facecolor=color, edgecolor='black', linewidth=1)
        elif marker == 's':
            patch = mpatches.Rectangle((4, 4), 12, 12, facecolor=color, edgecolor='black', linewidth=1)
        else:
            patch = mpatches.RegularPolygon((10, 10), numVertices=6, radius=6, orientation=0, facecolor=color)
        marker_box.add_artist(patch)

        # Label (NO AnnotationBbox here)
        label_text = TextArea(label, textprops={'fontsize': 12})

        # Combine marker + label horizontally
        row = HPacker(children=[marker_box, label_text], align="center", pad=0, sep=6)

        # Combine row + image vertically
        full_entry = VPacker(children=[row, image], align="center", pad=0, sep=4)

        legend_items.append(full_entry)

    # Stack all entries vertically
    legend_box = VPacker(children=legend_items, align="left", pad=4, sep=12)

    # Final annotation box in figure
    ab = AnnotationBbox(
        legend_box, (0.98, 0.985),
        xycoords='axes fraction',
        box_alignment=(1, 1),
        frameon=True,
        pad=0.6
    )
    ax.add_artist(ab)


def plot_points_with_error_bars(file_paths, save_path=None):
    model_dfs = []

    for model_idx, file_path in enumerate(file_paths):
        df = pd.read_csv(file_path)
        initial_df = df[df['video'].str.contains('_initial')]

        correct_counts = (
            initial_df[initial_df['result'] == 'correct']
                .groupby(['true_label', 'camera_distance'])
                .size()
        )
        total_counts = (
            initial_df
                .groupby(['true_label', 'camera_distance'])
                .size()
        )
        accuracy = (correct_counts / total_counts).unstack().fillna(0) * 100
        accuracy = accuracy[(accuracy != 0).any(axis=1)]

        accuracy_long = accuracy.reset_index().melt(
            id_vars='true_label',
            var_name='camera_distance',
            value_name='accuracy'
        )
        accuracy_long['model'] = model_idx
        model_dfs.append(accuracy_long)

    all_data = pd.concat(model_dfs, ignore_index=True)

    # Compute mean and std for each (action, camera_distance) pair
    summary = (
        all_data.groupby(['true_label', 'camera_distance'])['accuracy']
        .agg(['mean', 'std'])
        .reset_index()
    )

    # Assign sorted numeric x positions to actions
    sorted_labels = (
        summary.groupby('true_label')['mean']
        .max()
        .sort_values(ascending=False)
        .index.tolist()
    )
    label_to_x = {label: i for i, label in enumerate(sorted_labels)}
    summary['x_base'] = summary['true_label'].map(label_to_x)

    # Create offsets per camera distance
    camera_distances = sorted(summary['camera_distance'].unique())
    offsets = np.linspace(-0.2, 0.2, len(camera_distances))
    distance_to_offset = {dist: offset for dist, offset in zip(camera_distances, offsets)}

    # Optional: assign unique markers for each camera distance
    markers = ['o', 's', 'D', '^', 'v', '*']
    distance_to_marker = {dist: markers[i % len(markers)] for i, dist in enumerate(camera_distances)}

    # Plot
    fig, ax = plt.subplots(figsize=(14, len(sorted_labels) * 1), constrained_layout=True)  # Dynamic height based on number of labels

    # Adjust offset spacing
    offsets = np.linspace(-0.17, 0.17, len(camera_distances))
    distance_to_offset = {dist: offset for dist, offset in zip(camera_distances, offsets)}

    for dist in camera_distances:
        subset = summary[summary['camera_distance'] == dist].copy()
        subset['y'] = subset['x_base'] + distance_to_offset[dist]
        marker = distance_to_marker[dist]

        # Background bars (horizontal)
        ax.barh(
            y=subset['y'],
            width=subset['mean'],
            height=0.34,  # thicker bars
            left=0,
            alpha=0.2,
            label=None,
            zorder=0
        )

        # Handle NaNs and small std
        no_variation_threshold = 1.5
        subset['std'] = subset['std'].fillna(no_variation_threshold)
        subset['std'] = np.where(subset['std'] < no_variation_threshold, no_variation_threshold, subset['std'])

        # Plot error bars and markers
        ax.errorbar(
            x=subset['mean'],
            y=subset['y'],
            xerr=subset['std'],
            fmt=marker,
            markersize=15,
            capsize=4,
            linestyle='none',
            ecolor=(0, 0, 0, 0.35),
            label=dist,
            zorder=2
        )

    # Set axis details
    ax.set_xlim(left=0)  # Accuracy axis starts at 0
    ax.set_yticks(list(label_to_x.values()))
    ax.set_yticklabels(sorted_labels, fontsize=14)
    ax.set_xticks(ax.get_xticks())  # Retain current ticks, just apply style
    ax.tick_params(axis='x', labelsize=12)
    ax.set_xlabel("Accuracy (%)", fontsize=14)
    ax.set_ylabel("Action label", fontsize=14)
    ax.set_title("Effect of viewpoint on the average performance of models", fontsize=18)
    ax.grid(True, axis='x', linestyle='--', alpha=0.5)
    # ax.legend(title="Viewpoint", title_fontsize=14, fontsize=12)  # If you use a standard legend

    fig.tight_layout()

    entries = [
        ("cartwheel_9_modified_hispanic_frame1_near.png", "Camera Near", 's', 'tab:orange'),
        ("cartwheel_9_modified_hispanic_frame1_far.png", "Camera Far", 'o', 'tab:blue'),
    ]
    add_custom_legend_with_images(ax, entries)

    if save_path:
        fig.savefig(os.path.join(save_path, "plot_camera_viewpoint_transposed.pdf"), format='pdf')
        print(f"Plot saved to {save_path}")

    fig.show()


experiment_name = "top_20_kinetics_actions"
model_names = ["mvit_base_16x4", "slow_r50", "slowfast_r50", "tc_clip", "x3d_xs"]
file_paths = [f"model_results/{experiment_name}/video_results_extended_{model_name}.csv" for model_name in model_names]
output_path = rf"output_plots\{experiment_name}"
# # plot_avg_accuracy_camera_distance_per_action_with_std(file_paths)
# plot_violin_with_mean_line(file_paths, output_path)
# plot_boxplot_accuracy(file_paths, output_path)
# plot_avg_bar_accuracy(file_paths, output_path)
# plot_avg_bar_accuracy_grouped_by_camera(file_paths, output_path)
# plot_best_model_per_action_camera(file_paths, output_path)
# plot_all_models_per_action_camera_subplots(file_paths, output_path)
# plot_scatter_model_camera_shifted_with_violin(file_paths, output_path)
plot_points_with_error_bars(file_paths, output_path)