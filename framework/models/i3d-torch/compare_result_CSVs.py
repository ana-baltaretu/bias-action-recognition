import csv

# === Replace with your file paths ===
attempt_dataset_name = "attempt2/konzerthaus"
model_name = "slowfast_r50"
initial_file = f"./{attempt_dataset_name}/{model_name}/initial_video_results.csv"
modified_file = f"./{attempt_dataset_name}/{model_name}/modified_video_results.csv"
differences_file = f"./{attempt_dataset_name}/{model_name}/differences_between_runs.csv"


# Load both CSVs into dictionaries keyed by video name
def load_csv_to_dict(filepath):
    data = {}
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            video = row['video']
            data[video] = row
    return data

# Extract prefix to match, e.g. "cartwheel_0_" from "cartwheel_0_modified"
def get_prefix(video_name):
    parts = video_name.split('_')
    return '_'.join(parts[:2]) + "_"

initial_data = load_csv_to_dict(initial_file)
modified_data = load_csv_to_dict(modified_file)

# Build a lookup from prefix to initial video row
initial_by_prefix = {get_prefix(name): row for name, row in initial_data.items()}

# Compare using modified videos
differences = []

for mod_video, mod_row in modified_data.items():
    prefix = get_prefix(mod_video)
    if prefix in initial_by_prefix:
        initial_row = initial_by_prefix[prefix]
        # print(f"Comparing video (prefix): {prefix} between {initial_row['video']} and {mod_row['video']}")

        if (initial_row['raw_prediction'] != mod_row['raw_prediction'] or
                initial_row['result'] != mod_row['result']):
            differences.append({
                "video_prefix": prefix,
                "true_label": initial_row["true_label"],
                "raw_prediction_initial": initial_row["raw_prediction"],
                "raw_prediction_modified": mod_row["raw_prediction"],
                "result_initial": initial_row["result"],
                "result_modified": mod_row["result"]
            })

# Output the differences
if differences:
    print("Differences found in raw predictions or result correctness:\n")
    for row in differences:
        print(row)

    # Optionally save to CSV
    with open(differences_file, "w", newline='', encoding='utf-8') as out_file:
        fieldnames = differences[0].keys()
        writer = csv.DictWriter(out_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(differences)
    print("\n📝 Saved differences to 'differences_between_runs.csv'")
else:
    print("✅ No differences found between the runs.")