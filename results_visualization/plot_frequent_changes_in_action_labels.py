import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("prediction_divergence_summary_tc_clip.csv")

# Count each unique from→to transition
counts = df.groupby(['from_prediction', 'to_prediction']).size().reset_index(name='count')
counts = counts.sort_values(by='count', ascending=False)

# Plot
plt.figure(figsize=(12, 6))
plt.barh(
    [f"{row['from_prediction']} → {row['to_prediction']}" for _, row in counts.iterrows()],
    counts['count']
)
plt.xlabel("Number of Videos with This Prediction Change")
plt.title("Most Common Prediction Changes Caused by Skin Color Modification")
plt.tight_layout()
plt.savefig("prediction_change_barplot.png")
plt.show()
