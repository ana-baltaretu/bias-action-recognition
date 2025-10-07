import pandas as pd

# Load the CSV
df = pd.read_csv("video_results.csv")

# Replace values in the 'match' column
# Assuming it's True/False or 1/0 — adjust if needed
df["match"] = df["match"].apply(lambda x: "correct" if x else "incorrect")

# Save the updated CSV
df.to_csv("video_results_cleaned.csv", index=False)

print("Saved as video_results_cleaned.csv")
