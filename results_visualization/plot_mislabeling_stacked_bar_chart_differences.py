import pandas as pd
import matplotlib.pyplot as plt

model_name = "tc_clip" # mvit_base_16x4, slowfast_r50, tc_clip
GRAPH_HEIGHT = 70
# Load the data
df = pd.read_csv(f'video_results_with_skin_{model_name}.csv')

# Extract base video identifier
df['base_video'] = df['video'].str.extract(r'(.*)_(?:initial|modified.*)')

# Pivot predictions and correctness per skin color
pred_pivot = df.pivot_table(index='base_video', columns='skin_color_category', values='raw_prediction', aggfunc='first')
corr_pivot = df.pivot_table(index='base_video', columns='skin_color_category', values='result', aggfunc='first')

skin_colors = pred_pivot.columns.tolist()
impact_data = {}
all_totals = []

# Store actual examples of correct → wrong differences
diff_log = []

for sc1 in skin_colors:
    targets = []
    safe_change = []
    broke_change = []

    for sc2 in skin_colors:
        if sc1 == sc2:
            continue

        broke = 0
        safe = 0

        for vid in pred_pivot.index:
            pred1 = pred_pivot.loc[vid, sc1]
            pred2 = pred_pivot.loc[vid, sc2]
            correct1 = corr_pivot.loc[vid, sc1]
            correct2 = corr_pivot.loc[vid, sc2]

            if pd.notna(pred1) and pd.notna(pred2) and pd.notna(correct1) and pd.notna(correct2):
                if pred1 != pred2:
                    if correct1 == "correct" and correct2 == "incorrect":
                        broke += 1
                        diff_log.append({
                            "base_video": vid,
                            "from": sc1,
                            "to": sc2,
                            "prediction_from": pred1,
                            "prediction_to": pred2,
                            "result_from": correct1,
                            "result_to": correct2
                        })
                    else:
                        safe += 1

        total = safe + broke
        if total > 0:
            targets.append(sc2)
            safe_change.append(safe)
            broke_change.append(broke)
            all_totals.append(total)

    impact_data[sc1] = (targets, safe_change, broke_change)

# Save the differences to CSV
diff_df = pd.DataFrame(diff_log)
diff_df.to_csv(f"correct_to_wrong_transitions_{model_name}.csv", index=False)
print(f"Saved {len(diff_log)} correct → wrong transitions to 'correct_to_wrong_transitions.csv'")

# Determine fixed y-limit
max_total = GRAPH_HEIGHT # max(all_totals) if all_totals else 1
ylim_top = max_total + 2

# Plotting
n = len(skin_colors)
ncols = n
nrows = 1

fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(5 * ncols, 5 * nrows))
axes = axes.flatten()

for idx, (sc1, (targets, safe, broke)) in enumerate(impact_data.items()):
    ax = axes[idx]
    bars_safe = ax.bar(targets, safe, label='Change only raw prediction', color='goldenrod')
    bars_broke = ax.bar(targets, broke, bottom=safe, label='Correct → Wrong', color='crimson')

    ax.set_title(f"Changing from '{sc1}' to others")
    ax.set_ylabel("Number of Changed Predictions")
    ax.set_ylim(0, ylim_top)
    ax.set_xticklabels(targets, rotation=45)

    for t, s, b in zip(targets, safe, broke):
        total = s + b
        ax.text(t, total + 0.5, str(total), ha='center', va='bottom', fontsize=8)

# Hide unused subplots
for i in range(len(impact_data), len(axes)):
    axes[i].axis('off')

# Add shared legend
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='upper right')

plt.suptitle("Effect of Skin Color Change on Prediction Accuracy (Raw Counts, Unified Scale)", fontsize=16)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig(f"skin_color_stacked_bar_chart_differences_{model_name}.png")
plt.show()
