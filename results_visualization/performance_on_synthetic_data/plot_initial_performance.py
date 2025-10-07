import pandas as pd
import matplotlib.pyplot as plt

# Use a clean visual style
plt.style.use("seaborn-v0_8-whitegrid")

models = ["tc_clip", "slowfast_r50", "mvit_base_16x4"]
actions = ["cartwheel", "drink", "lunge", "squat", "yoga"]
markers = ['o', 's', '^']

# Store data for plotting
model_accuracies = {}  # model_name -> list of action accuracies
overall_accuracies = {}  # model_name -> overall accuracy

# Gather per-action and overall accuracy
for model_name in models:
    file_path = f"../video_results_with_skin_{model_name}.csv"
    df = pd.read_csv(file_path)
    initial_videos = df[df['video'].str.contains('_initial')]

    correct_total = 0
    total_total = 0
    action_accuracies = []

    for action in actions:
        matching = initial_videos[initial_videos['video'].str.contains(action)]
        total = len(matching)
        correct = len(matching[matching['result'] == 'correct'])
        acc = correct / total if total > 0 else 0
        action_accuracies.append(acc)

        correct_total += correct
        total_total += total

    model_accuracies[model_name] = action_accuracies
    overall_accuracies[model_name] = correct_total / total_total if total_total > 0 else 0

# Make two side-by-side plots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Plot 1: Per-action line plot
for i, model_name in enumerate(models):
    ax1.plot(
        actions,
        model_accuracies[model_name],
        marker=markers[i % len(markers)],
        linewidth=2.5,
        alpha=0.85,
        label=model_name.replace("_", " ").upper()
    )

ax1.set_title("Model Accuracy per Action ('_initial' Videos)", fontsize=14)
ax1.set_xlabel("Action Category", fontsize=12)
ax1.set_ylabel("Accuracy", fontsize=12)
ax1.set_ylim(0, 1)
ax1.set_yticks([i / 10 for i in range(11)])
ax1.legend(title="Model", fontsize=10, title_fontsize=11)
ax1.grid(True)

# Plot 2: Overall accuracy bar chart
model_labels = [m.replace("_", " ").upper() for m in models]
overall_values = [overall_accuracies[m] for m in models]

ax2.bar(model_labels, overall_values, color=['#4c72b0', '#55a868', '#c44e52'], alpha=0.85)
ax2.set_title(f"Overall Accuracy per Model for {actions}", fontsize=14)
ax2.set_ylabel("Accuracy", fontsize=12)
ax2.set_ylim(0, 1)
ax2.set_yticks([i / 10 for i in range(11)])
for i, val in enumerate(overall_values):
    ax2.text(i, val + 0.02, f"{val:.2f}", ha='center', fontsize=10)

plt.tight_layout()
plt.savefig("initial_performance_per_action.png")
plt.show()
