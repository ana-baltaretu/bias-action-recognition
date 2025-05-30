import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


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


def plot_violin_with_mean_line(file_paths):
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

        # Convert to long-form
        accuracy_long = accuracy.reset_index().melt(
            id_vars='true_label',
            var_name='camera_distance',
            value_name='accuracy'
        )
        accuracy_long['model'] = model_idx
        model_dfs.append(accuracy_long)

    all_data = pd.concat(model_dfs, ignore_index=True)

    # Plot
    plt.figure(figsize=(14, 6))

    # Violin plots per camera_distance
    sns.violinplot(
        data=all_data,
        x='true_label',
        y='accuracy',
        hue='camera_distance',
        split=True,
        inner=None,
        cut=0,
        scale="width",  # makes all violins the same width
        width=0.9
    )

    # Overlay mean accuracy line
    sns.pointplot(
        data=all_data,
        x='true_label',
        y='accuracy',
        hue='camera_distance',
        # dodge=0.3,
        errorbar=None,  # instead of ci=None
        markers='o',
        linestyles='-',
        palette='dark'
    )

    plt.title("Accuracy Distribution per Action by Camera Distance (Violin + Mean Line)")
    plt.ylabel("Correct Prediction Percentage")
    plt.xlabel("Action")
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(title="Camera Distance")
    plt.tight_layout()
    plt.show()


# model_name = "tc_clip" # mvit_base_16x4, slow_r50, slowfast_r50, tc_clip, x3d_xs
# file_path = f"model_results/older_runs/video_results_extended_{model_name}.csv"
# # plot_camera_distance_accuracy(file_path)
# plot_line_chart_camera_distance_accuracy_per_action(file_path)

model_names = ["mvit_base_16x4", "slow_r50", "slowfast_r50", "tc_clip", "x3d_xs"]
file_paths = [f"model_results/older_runs/video_results_extended_{model_name}.csv" for model_name in model_names]
# # plot_avg_accuracy_camera_distance_per_action_with_std(file_paths)
plot_violin_with_mean_line(file_paths)