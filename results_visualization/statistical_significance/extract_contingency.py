import pandas as pd
from scipy.stats import chi2_contingency

# Load the CSV file
model_name = "tc_clip" # mvit_base_16x4, slowfast_r50, tc_clip
file_path = f"../video_results_with_skin_{model_name}.csv"  # Change this to your file path
df = pd.read_csv(file_path)

# Create the contingency table
contingency_table = (
    df.groupby(['skin_color_category', 'result'])
    .size()
    .unstack(fill_value=0)
    .rename(columns={"correct": "Correct", "incorrect": "Incorrect"})
)

# Display the result
print("Contingency Table by Skin Color:\n")
print(contingency_table)

# Optional: save to CSV
contingency_table.to_csv(f"contingency_table_by_skin_color_{model_name}.csv")

# Run Chi-Square test
chi2, p_value, dof, expected = chi2_contingency(contingency_table)

# Print results
print("Chi-Square Test for Prediction Accuracy Across Skin Color Groups:")
print(f"Chi2 Statistic: {chi2:.4f}")
print(f"Degrees of Freedom: {dof}")
print(f"P-Value: {p_value:.4f}")
