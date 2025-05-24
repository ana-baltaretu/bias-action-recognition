import pandas as pd
from statsmodels.stats.contingency_tables import cochrans_q

# Load data
model_name = "mvit_base_16x4" # mvit_base_16x4, slowfast_r50, tc_clip
df = pd.read_csv(f"../video_results_with_skin_{model_name}.csv")

# Step 1: Create binary column for correctness
df["is_correct"] = df["result"].apply(lambda x: 1 if x == "correct" else 0)

# Step 2: Extract base video name (e.g., 'cartwheel_0')
df["base_video"] = df["video"].str.extract(r'^(.*?)(?:_modified_.*|_initial)?\.mp4$')[0].fillna(df["video"].str.replace('.mp4', '', regex=False))

# Step 3: Pivot: rows = base videos, cols = skin color, values = correctness
pivot = df.pivot_table(
    index="base_video",
    columns="skin_color_category",
    values="is_correct"
)

# print(pivot)

# Step 4: Drop rows with missing values (i.e., not all skin versions exist)
pivot_clean = pivot.dropna()

# print(pivot_clean)

# Step 5: Cochran’s Q test
result = cochrans_q(pivot_clean)
print(f"Cochran's Q test statistic: {result.statistic:.4f}")
print(f"P-value: {result.pvalue:.4f}")
